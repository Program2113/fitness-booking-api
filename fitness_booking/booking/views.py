import logging
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import generics, status
from .models import Class, Booking
from django.contrib.auth.models import User
from .serializers import ClassSerializer, BookingSerializer, BookingRequestSerializer, UserSerializer
from django.utils.timezone import activate
import pytz

logger = logging.getLogger(__name__)

# class CreateUserView(generics.CreateAPIView):
#     """API endpoint for user registration."""
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     permission_classes = [AllowAny]  # Allow anyone to register
#     authentication_classes = []  # No authentication required for registration

#     logger.info("User registration accessed.")


class CreateUserView(generics.CreateAPIView):
    """API endpoint for user registration."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def perform_create(self, serializer):
        user = serializer.save()
        logger.info(f"User registered: {user.username}")

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return Response(
            {"message": "User created successfully", "user_id": response.data['id']},
            status=status.HTTP_201_CREATED
        )


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_classes(request):
    logger.info(f"Fetching classes for the user: {request.user.username}")
    
    tz = request.GET.get("tz", "Asia/Kolkata")
    activate(pytz.timezone(tz))
    classes = Class.objects.all()
    serializer = ClassSerializer(classes, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def book_class(request):
    serializer = BookingRequestSerializer(data=request.data)
    if serializer.is_valid():
        try:
            fitness_class = Class.objects.get(id=serializer.validated_data['class_id'])
            if fitness_class.available_slots <= 0:
                logger.info(f"No available slots for class: {fitness_class.name} requested by user: {request.user.username}")
                return Response({"error": "No slots available"}, status=400)
            
            Booking.objects.create(
                fitness_class=fitness_class,
                client_name=request.user.username,  # Tie to authenticated user
                client_email=request.user.email     # Tie to authenticated user
            )
            fitness_class.available_slots -= 1
            fitness_class.save()
            logger.info(f"Booking successful for user: {request.user.username}, for class: {fitness_class.name}")

            return Response({"message": "Booking successful"}, status=201)
        except Class.DoesNotExist:
            logger.info(f"Class not found for booking request: {serializer.validated_data['class_id']}")
            return Response({"error": "Class not found"}, status=404)
    return Response(serializer.errors, status=400)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_bookings(request):
    email = request.user.email  # Restrict to authenticated user's email
    logger.info(f"Fetching bookings for user: {request.user.username}")
    bookings = Booking.objects.filter(client_email=email)
    print(f"Bookings found: {bookings.count()} for user: {request.user.username}")
    if bookings.count() == 0:
        logger.info(f"No bookings found for user: {request.user.username}")
        return Response({"message": "No bookings found"}, status=400)
    
    serializer = BookingSerializer(bookings, many=True)
    return Response(serializer.data)
