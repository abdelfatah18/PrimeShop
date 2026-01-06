from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'date_of_birth', 'profile_photo', 'is_active', 'is_staff', 'is_superuser')