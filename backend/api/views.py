from django.shortcuts import render
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

from api import serializer as api_serializer
from userauths.models import User, Profile

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response

import random




class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = api_serializer.MyTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = api_serializer.RegisterSerializer    # just our serializer for the registration that we created in the serializer.py file


def generate_random_otp(length=7):
    otp = ''.join([str(random.randint(0, 9)) for _ in range(length)])
    return otp


class PasswordResetEmailVerifyAPIView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = api_serializer.UserSerializer

    def get_object(self):
        email = self.kwargs['email']    # the url will be something like 'api/v1/password-email-verify/johnclayton@gmail.com'  and we are essentially grabbing the end of the url which is the email because we set it up that way

        user = User.objects.filter(email=email).first()    # when this was a '.get(email=email)' then it was fetching a User from the database by the email (essentially finding the user with the email that has been passed in)
                                                            # now that it is a filter, I think it is still doing the same thing but im not positive
        if user:

            uuidb64 = user.pk                      # uuid64 is the id we use to verify the user (I think it will be in the url)
            refresh = RefreshToken.for_user(user)
            refresh_token = str(refresh.access_token)

            user.refresh_token = refresh_token
            user.otp = generate_random_otp()       # this will give us a unique 7 digit otp
            user.save()

            link = f"http://localhost:5173/create-new-password/?otp={user.otp}&uuidb64={uuidb64}&refresh_token={refresh_token}"
            
            context = {
                "link": link,
                "username": user.username
            }

            subject = "Password Reset Email"
            text_body = render_to_string("email/password_reset.txt", context)    # we will have a folder for multiple different email templates. Anymail allows us to customize the body of the email
            html_body = render_to_string("email/password_reset.html", context)

            msg = EmailMultiAlternatives(                  # this appears to be our email that we will send to and from
                subject=subject,
                from_email=settings.FROM_EMAIL,
                to=[user.email],
                body=text_body
            )

            msg.attach_alternative(html_body, "text/html")     # rendering the html body in the email
            msg.send()                                          # this is the actual send of the email I think


            print("link ====== ", link)

        return user



class PasswordChangeAPIView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = api_serializer.UserSerializer

    def create(self, request, *args, **kwargs):
        # payload = request.data      # I believe this is just storing what the user passes in, storing it as a variable called payload.

        # request.data   =>   this is the information the user will pass in when they are reseting the password on the specific link. It is stored in the "request" property
        # we are just storing the Users current properties into our fields that we will be using 
        otp = request.data['otp']
        uuidb64 = request.data['uuidb64']
        password = request.data['password']

        user = User.objects.get(id=uuidb64, otp=otp)
        if user:
            user.set_password(password)
            user.otp = ""
            user.save()

            return Response({"message": "Password Changed Successfully"}, status=status.HTTP_201_CREATED)

        else:
            return Response({"message": "User does not exists"}, status=status.HTTP_404_NOT_FOUND)


