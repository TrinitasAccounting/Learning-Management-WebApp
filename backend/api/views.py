from django.shortcuts import render
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

from api import serializer as api_serializer
from userauths.models import User, Profile
from api import models as api_models

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response

import random
from decimal import Decimal




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



# ListAPIView means we are trying to get a list from the database
class CategoryListAPIView(generics.ListAPIView):
    queryset = api_models.Category.objects.filter(active=True)    # this would only return the Categories that have 'active' set to True. But our Category model doesnt have this field yet so we comment this out
    serializer_class = api_serializer.CategorySerializer
    permission_classes = [AllowAny]


class CourseListAPIView(generics.ListAPIView):
    # We are fetching a list of all Courses if the the platform_status and teacher_course_status are both "Published"
    # We can probably fetch as list of distributors if the User_id is the logged in User, so it just shows us the distributors working with this User
    queryset = api_models.Course.objects.filter(platform_status="Published", teacher_course_status="Published")   
    serializer_class = api_serializer.CourseSerializer
    permission_classes = [AllowAny]


# RetrieveAPIView is used to get 1 single object returned
class CourseDetailAPIView(generics.RetrieveAPIView):
    serializer_class = api_serializer.CourseSerializer
    permission_classes = [AllowAny]

    # We are overridding the fetch because we aren't using the simple get by ID, we are getting by the slug url
    def get_object(self):
        slug = self.kwargs['slug']           # self.kwargs is actually getting what ever is passed into the url. We are calling it the slug in the urls.py
        course = api_models.Course.objects.get(slug=slug, platform_status="Published", teacher_course_status="Published")
        return course


# CreateAPIView is used to create an item or row in the database. Used for POST request I believe
class CartAPIView(generics.CreateAPIView):
    queryset = api_models.Cart.objects.all()
    serializer_class = api_serializer.CartSerializer
    permission_classes = [AllowAny]

    # We are overriding the default save method, so we dont have to pass all of the exact fields to the cart or something
    # We are expecting a course_id to be passed in as the request, this tells our backend what course to go find and then add to the cart
    # If we don't customize the default save method, then we will need to pass exactly the fields in the model in the request 
    # we only have to pass in: course_id, user_id, price, country_name, cart_id
    # {
    # "price": "100",
    # "country_name": "United States",
    # "cart_id": "234567923",
    # "date": "2025-03-28T17:45:23.441Z",
    # "course_id": 1,
    # "user_id": 1
    # }
    def create(self, request, *args, **kwargs):
        course_id = request.data['course_id']        # this 'course_id' needs to match whatever name we are calling it from the frontend as do the rest of them actually
        user_id = request.data['user_id']
        price = request.data['price']
        country_name = request.data['country_name']
        cart_id = request.data['cart_id']             # this is how the cart is tracked since we aren't restricting cart functionality to only authenticated logged in users

        # grabbing the actual course using the course_id
        course = api_models.Course.objects.filter(id=course_id).first()          # filtering all of the courses in the database where the id is the same as whatever id was passed in with the request
        
        # grabbing the user_id who sent the request to add to their cart. I think in MyPrice software, there will always be a user logged in so we can track it this way and not via the 'cart_id'
        if user_id != "undefined":
            user = User.objects.filter(id=user_id).first()
        else:
            user = None

        try:
            country_object = api_models.Country.objects.filter(name=country_name).first()      # getting the country based on the country_name that was passed to us on the frontend
            country = country_object.name
        except:
            country_object = None
            country = 'United States'            # default country that we will use if the country is not in our system for some reason

        if country_object:
            tax_rate = country_object.tax_rate / 100              # getting the tax_rate if this country by accessing the country_objects tax_rate field
        else:
            tax_rate = 0             # setting a default tax_rate

        # can also do the below to get the price from the course table instead of the user passing it in
        # course = api_models.Course.objects.filter(id=course_id).first()
        # then below in the cart section do: cart.price = course.price


        # we are actually trying to figure out if a cart with this id already exist, so we can either add to it or create a new cart with this id
        # since non logged in users can add to their cart, this system is tracking it by a cart_id. We may not need this in MyPrice, but we will have to enforce that only authenticated users can add to the cart
        # we should restict cart functionality to authenticated users, and probably track is based on the user_id maybe. Complicated
        cart = api_models.Cart.objects.filter(cart_id=cart_id, course=course).first()

        if cart:
            cart.course = course
            cart.user = user
            cart.price = price
            cart.tax_fee = Decimal(price) * Decimal(tax_rate)             # we do the Decimal to make sure we dont get a type error when doing the math. Make sure to have import Decimal at the top. 
            cart.country = country
            cart.cart_id = cart_id
            cart.total = Decimal(cart.price) + Decimal(cart.tax_fee)
            cart.save()

            return Response({"message": "Cart Updated Successfully"}, status=status.HTTP_200_OK)

        else:
            cart = api_models.Cart()
            cart.course = course
            cart.user = user
            cart.price = price
            cart.tax_fee = Decimal(price) * Decimal(tax_rate)             # we do the Decimal to make sure we dont get a type error when doing the math. Make sure to have import Decimal at the top. 
            cart.country = country
            cart.cart_id = cart_id
            cart.total = Decimal(cart.price) + Decimal(cart.tax_fee)
            cart.save()

            return Response({"message": "Cart Created Successfully"}, status=status.HTTP_201_CREATED)



# When ever this route gets called, it will return all the items that are in that particular cart
# This requires a cart_id to be passed in, but we should change that to user_id
class CartListAPIView(generics.ListAPIView):
    serializer_class = api_serializer.CartSerializer
    permission_classes = [AllowAny]

    #overiding the default queryset. 
    def get_queryset(self):
        # we are finding the cart by the 'cart_id' but we can easily find it by the 'user_id' passed in instead
        cart_id = self.kwargs['cart_id']
        queryset = api_models.Cart.objects.filter(cart_id=cart_id)
        return queryset


# DestroyAPIView => this will delete what ever item is returned to it
class CartItemDeleteAPIView(generics.DestroyAPIView):
    serializer_class = api_serializer.CartSerializer
    permission_classes = [AllowAny]

    # We are passing in the cart_id, but probably should be the user_id. And passing in the item_id to remove from the cart
    def get_object(self):
        cart_id = self.kwargs['cart_id']
        item_id = self.kwargs['item_id']

        # to filter by the user, the instructor did a double underscore of 'user__id=user_id'  So maybe we have to try it this way. Since it would have to go into the User model and filter by the id in there
        return api_models.Cart.objects.filter(cart_id=cart_id, id=item_id).first()


# this will be used to send information back to the frontend about the cart such as total price of the cart, items etc.
class CartStatsAPIView(generics.RetrieveAPIView):
    serializer_class = api_serializer.CartSerializer
    permission_classes = [AllowAny] 
    # the default lookup_field is the pk (primary key id), when we want to customize the lookup_field we manually type it in like below
    lookup_field = 'cart_id'

    # to get the correct cart by the cart_id
    def get_queryset(self):
        cart_id = self.kwargs['cart_id']
        queryset = api_models.Cart.objects.filter(cart_id=cart_id)
        return queryset

    def get(self, request, *args, **kwargs):
        # we are running the above function to get the correct cart based on the cart_id passed in
        queryset = self.get_queryset()

        total_price = 0.00
        total_tax = 0.00
        total_total = 0.00

        # Looping through the items in the cart, and calculating the totals for the cart
        for cart_item in queryset:
            total_price += float(self.calculate_price(cart_item))
            total_tax += float(self.calculate_tax(cart_item))
            total_total += round(float(self.calculate_total(cart_item)), 2)

        # By doing this object and returning it in the Response, we can control what is sent to the frontend as a Response
        data = {
            "price": total_price,
            "tax": total_tax,
            "total": total_total
        }

        return Response(data)

    def calculate_price(self, cart_item):
        return cart_item.price

    def calculate_tax(self, cart_item):
        return cart_item.tax_fee

    def calculate_total(self, cart_item):
        return cart_item.total




# This is creating a CartOrder for us, that has all the items that were in the cart for that cart_id or user
class CreateOrderAPIView(generics.CreateAPIView):
    serializer_class = api_serializer.CartOrderSerializer
    permission_classes = [AllowAny]
    queryset = api_models.CartOrder.objects.all()

    # By doing this, we are overriding the create method and we can control what variables have to be passed in from the frontend. Otherwise they will have to pass in all variables that the model requires
    def create(self, request, *args, **kwargs):
        full_name = request.data['full_name']
        email = request.data['email']
        country = request.data['country']
        cart_id = request.data['cart_id']
        user_id = request.data['user_id']

        # If a user is not logged in, we will send 0 as the user_id
        if user_id != 0:
            # if there is a user, we will grab the User object for the logged in User in this manner
            user = User.objects.get(id=user_id)
        else:
            user = None

        #  Fetching all of the items in the cart, filtered by the cart_id. We should be filtering by the user_id for MyPrice probably
        cart_items = api_models.Cart.objects.filter(cart_id=cart_id)

        total_price = Decimal(0.00)
        total_tax = Decimal(0.00)
        total_initial_total = Decimal(0.00)
        total_total = Decimal(0.00)

        order = api_models.CartOrder.objects.create(
            full_name=full_name,
            email=email,
            country=country,
            student=user
        )

        # Looping through all of the items already in the cart, so we can create the full order I believe
        # We should probably use a loop through function to loop through all items in the cart when user selects the "price comparison"
        # and we will loop through to return the custom pricing from each distributor for each item
        # This is creating a CartOrderItem will all of the fields from the CartOrderItem model
        for c in cart_items:
            api_models.CartOrderItem.objects.create(
                order=order,            # we created an order above this, I am not really sure how this works though
                course=c.course,
                teacher=c.course.teacher,      # we using the foreign key here to go inside of the course and find the teacher
                price=c.price,
                tax_fee=c.tax_fee,
                total=c.total,
                initial_total=c.total,
            )

            # These will update everytime we loop through and calculate the total for all items in the cart
            total_price += Decimal(c.price)
            total_tax += Decimal(c.tax_fee)
            total_initial_total += Decimal(c.total)
            total_total += Decimal(c.total)

            order.teachers.add(c.course.teacher)      # something about it going and grabbing the teacher, and adding it to something

        # We are filling in any of the model columns that we left out from the for loop
        # We are actually creating a CartOrder so it needs all of the models fields I believe. We add some in the order= above and then some in the for loop as well
        order.sub_total = total_price
        order.tax_fee = total_tax
        order.initial_total = total_initial_total
        order.total = total_total

        order.save()

        return Response({'message': "Order Created Successfully"}, status=status.HTTP_201_CREATED)



# This is just a view that allows us to pass an oid and it provides us with all of the details of that particualr cart order
# I am assuming we are going to use this to pass this to the strip payment functionality
# We can make our lookup field to be any of the unique fields in the CartOrder model
class CheckoutAPIView(generics.RetrieveAPIView):
    serializer_class = api_serializer.CartOrderSerializer
    permission_classes = [AllowAny]
    queryset = api_models.CartOrder.objects.all()
    lookup_field = 'oid'




class CouponApplyAPIView(generics.CreateAPIView):
    serializer_class = api_serializer.CouponSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        order_oid = request.data['order_oid']
        coupon_code = request.data['coupon_code']

        order = api_models.CartOrder.objects.get(oid=order_oid)
        coupon = api_models.Coupon.objects.get(code=coupon_code)

        if coupon:
            # We are getting all of the items that are in this partical CartOrder
            order_items = api_models.CartOrderItem.objects.filter(order=order, teacher=coupon.teacher)       # because the order is a foreign key, it needs the entire object it seems like. Teacher object is passed as well
            for i in order_items:
                if not coupon in i.coupons.all():
                    discount = i.total * coupon.discount / 100            # this is just using the total field found in CartOrderItem, and then finding the discount field found in the coupon that was passed in via the coupon_code
                    
                    i.total -= discount
                    i.price -= discount        # we are removing the discount from the total and the price for this CartOrderItem.
                    i.saved += discount        # we are then adding the discount into the saved field for this CartOrderItem
                    i.applied_coupon = True
                    i.coupons.add(coupon)

                    order.coupons.add(coupon)     # adding this particular coupon to the CartOrder, so it shows there in the coupons field
                    order.total -= discount
                    order.sub_total -= discount
                    order.saved += discount        # adding how much they have saved into the CartOrder for this item

                    i.save()
                    order.save()
                    coupon.used_by.add(order.student)

                    return Response({"message": "Coupon Found and Activated"}, status=status.HTTP_201_CREATED)
                else:
                    return Response({"message": "Coupon Already Applied"}, status=status.HTTP_200_OK)

        else:
            return Response({"message": "Coupone Not Found"}, status=status.HTTP_404_NOT_FOUND)

        










