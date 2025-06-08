from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Class, Booking


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = '__all__'


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'

class BookingRequestSerializer(serializers.Serializer):
    class_id = serializers.IntegerField()
    client_name = serializers.CharField(max_length=100)
    client_email = serializers.EmailField()
