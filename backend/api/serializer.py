
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers
from userauths.models import Profile, User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        #  I believe the below are returned with the token so we can access them, but I really am not sure
        # Seems like we are doing this so we specific exact information that we want to pass into the token
        # When the token is returned, it returns with these fields below added to the json. We can use them I believe. It mainly provides better information for us
        token['full_name'] = user.full_name
        token['email'] = user.email
        token['username'] = user.username

        return token


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])   # the validate_password will automatically suggest not using too simple of a password such as only numbers or too short or whatever
    password2 = serializers.CharField(write_only=True, required=True)   

    class Meta:
        model = User
        fields = ['full_name', 'email', 'password', 'password2']

    # We are validating that both the passwords entered match each other. If not we are raising a Validation Error
    def validate(self, attr):
        if attr['password'] != attr['password2']:
            raise serializers.ValidationError({'Password fields did not match.'})

        return attr

    def create(self, validated_data):
        user = User.objects.create(
            full_name=validated_data['full_name'],
            email=validated_data['email'],
        )

        email_username, _ = user.email.split("@")
        user.username = email_username
        user.set_password(validated_data['password'])
        user.save()

        return user




class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'


class ProfileSerializer(serializers.ModelSerializer):

    class Meta: 
        model = Profile
        fields = '__all__'





