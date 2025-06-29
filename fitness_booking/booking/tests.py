# tests.py
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.utils.timezone import make_aware
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from .models import Class, Booking  # Adjust based on your models
import pytz
import logging
from rest_framework_simplejwt.tokens import RefreshToken  # For JWT token generation

logger = logging.getLogger(__name__)

class BookingAPITests(TestCase):
    def setUp(self):
        # Initialize the API client
        self.client = APIClient()

        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpass', email='testuser@example.com')

        # Generate a JWT token for the test user
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)

        # Set the token in the client's headers
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

        # Set up test data (e.g., a Class object)
        ist = pytz.timezone("Asia/Kolkata")  # Adjust timezone as needed
        self.class1 = Class.objects.create(
            name="Yoga",
            instructor="Amit",
            datetime=make_aware(datetime.now() + timedelta(days=1), ist),
            available_slots=3
        )

    def test_get_classes(self):
        # Test retrieving class list
        response = self.client.get("/classes/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Yoga")

    def test_book_class_success(self):
        # Test booking a class successfully
        payload = {
            "class_id": self.class1.id,
            "client_name": "Dummy Name",  # Included but overridden by view
            "client_email": "dummy@example.com"  # Included but overridden by view
        }
        response = self.client.post("/book/", payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.class1.refresh_from_db()
        self.assertEqual(self.class1.available_slots, 2)
        self.assertEqual(Booking.objects.count(), 1)
        booking = Booking.objects.first()
        self.assertEqual(booking.fitness_class, self.class1)
        self.assertEqual(booking.client_name, self.user.username)
        self.assertEqual(booking.client_email, self.user.email)

    def test_book_class_invalid_id(self):
        # Test booking with an invalid class ID
        payload = {
            "class_id": 999,  # Non-existent ID
            "client_name": "Invalid User",
            "client_email": "invalid@example.com"
        }
        response = self.client.post("/book/", payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_book_class_no_slots(self):
        # Test booking when no slots are available
        self.class1.available_slots = 0
        self.class1.save()
        payload = {
            "class_id": self.class1.id,
            "client_name": "Full User",
            "client_email": "full@example.com"
        }
        response = self.client.post("/book/", payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_user_bookings_with_bookings(self):
        # Test retrieving bookings for the authenticated user when bookings exist
        Booking.objects.create(
            fitness_class=self.class1,
            client_name=self.user.username,
            client_email=self.user.email
        )
        response = self.client.get("/bookings/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['client_email'], self.user.email)

    def test_get_user_bookings_no_bookings(self):
        # Test retrieving bookings when none exist for the user
        response = self.client.get("/bookings/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"message": "No bookings found"})

    def test_get_bookings_unauthorized(self):
        # Test accessing bookings without authentication
        self.client.credentials()  # Clear token
        response = self.client.get("/bookings/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)