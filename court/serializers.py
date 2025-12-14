from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Case, Vote

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Incorrect Credentials")

class CaseSerializer(serializers.ModelSerializer):
    submitted_by = UserSerializer(read_only=True)

    class Meta:
        model = Case
        fields = ['id', 'title', 'argument', 'evidence', 'evidence_file', 'submitted_by', 'status', 'created_at', 'updated_at']

class VoteSerializer(serializers.ModelSerializer):
    juror = UserSerializer(read_only=True)

    class Meta:
        model = Vote
        fields = ['id', 'case', 'juror', 'verdict', 'voted_at']
