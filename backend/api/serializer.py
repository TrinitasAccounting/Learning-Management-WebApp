
from django.contrib.auth.password_validation import validate_password
from api import models as api_models

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








class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        fields = ['id', 'title', 'image', 'slug', 'active', 'course_count']
        model = api_models.Category

class TeacherSerializer(serializers.ModelSerializer):

    class Meta:
        fields = [ "user", "image", "full_name", "bio", "facebook", "twitter", "linkedin", "about", "country", "students", "courses", "review",]
        model = api_models.Teacher




class VariantItemSerializer(serializers.ModelSerializer):
    
    class Meta:
        fields = '__all__'
        model = api_models.VariantItem

    
    # def __init__(self, *args, **kwargs):
    #     super(VariantItemSerializer, self).__init__(*args, **kwargs)
    #     request = self.context.get("request")
    #     if request and request.method == "POST":
    #         self.Meta.depth = 0
    #     else:
    #         self.Meta.depth = 3


class VariantSerializer(serializers.ModelSerializer):
    variant_items = VariantItemSerializer(many=True)
    items = VariantItemSerializer(many=True)
    class Meta:
        fields = '__all__'
        model = api_models.Variant


    # def __init__(self, *args, **kwargs):
    #     super(VariantSerializer, self).__init__(*args, **kwargs)
    #     request = self.context.get("request")
    #     if request and request.method == "POST":
    #         self.Meta.depth = 0
    #     else:
    #         self.Meta.depth = 3




class Question_Answer_MessageSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(many=False)

    class Meta:
        fields = '__all__'
        model = api_models.Question_Answer_Message


class Question_AnswerSerializer(serializers.ModelSerializer):
    messages = Question_Answer_MessageSerializer(many=True)             # if a special method needs access to another serializer or model, you have to add it here. And make sure that serializer is defined above this model so python can access its variable
    profile = ProfileSerializer(many=False)                    # because we are trying to get one users profile, we have many=False
    
    class Meta:
        fields = '__all__'
        model = api_models.Question_Answer



class CartSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = api_models.Cart

    # def __init__(self, *args, **kwargs):
    #     super(CartSerializer, self).__init__(*args, **kwargs)
    #     request = self.context.get("request")
    #     if request and request.method == "POST":
    #         self.Meta.depth = 0
    #     else:
    #         self.Meta.depth = 3


class CartOrderItemSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = api_models.CartOrderItem

    # def __init__(self, *args, **kwargs):
    #     super(CartOrderItemSerializer, self).__init__(*args, **kwargs)
    #     request = self.context.get("request")
    #     if request and request.method == "POST":
    #         self.Meta.depth = 0
    #     else:
    #         self.Meta.depth = 3


class CartOrderSerializer(serializers.ModelSerializer):
    order_items = CartOrderItemSerializer(many=True)
    
    class Meta:
        fields = '__all__'                   # even if you define a special method above, you can still use '__all__' and it will still find that method
        model = api_models.CartOrder


    # def __init__(self, *args, **kwargs):
    #     super(CartOrderSerializer, self).__init__(*args, **kwargs)
    #     request = self.context.get("request")
    #     if request and request.method == "POST":
    #         self.Meta.depth = 0
    #     else:
    #         self.Meta.depth = 3

class CertificateSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = api_models.Certificate



class CompletedLessonSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = api_models.CompletedLesson


    # def __init__(self, *args, **kwargs):
    #     super(CompletedLessonSerializer, self).__init__(*args, **kwargs)
    #     request = self.context.get("request")
    #     if request and request.method == "POST":
    #         self.Meta.depth = 0
    #     else:
    #         self.Meta.depth = 3

class NoteSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = api_models.Note



class ReviewSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(many=False)

    class Meta:
        fields = '__all__'
        model = api_models.Review

    # def __init__(self, *args, **kwargs):
    #     super(ReviewSerializer, self).__init__(*args, **kwargs)
    #     request = self.context.get("request")
    #     if request and request.method == "POST":
    #         self.Meta.depth = 0
    #     else:
    #         self.Meta.depth = 3

class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = api_models.Notification


class CouponSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = api_models.Coupon


class WishlistSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = api_models.Wishlist

    # def __init__(self, *args, **kwargs):
    #     super(WishlistSerializer, self).__init__(*args, **kwargs)
    #     request = self.context.get("request")
    #     if request and request.method == "POST":
    #         self.Meta.depth = 0
    #     else:
    #         self.Meta.depth = 3

class CountrySerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = api_models.Country




class EnrolledCourseSerializer(serializers.ModelSerializer):
    lectures = VariantItemSerializer(many=True, read_only=True)
    completed_lesson = CompletedLessonSerializer(many=True, read_only=True)
    curriculum =  VariantSerializer(many=True, read_only=True)
    note = NoteSerializer(many=True, read_only=True)
    question_answer = Question_AnswerSerializer(many=True, read_only=True)
    review = ReviewSerializer(many=False, read_only=True)


    class Meta:
        fields = '__all__'
        model = api_models.EnrolledCourse

    def __init__(self, *args, **kwargs):
        super(EnrolledCourseSerializer, self).__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.method == "POST":
            self.Meta.depth = 0
        else:
            self.Meta.depth = 3



class CourseSerializer(serializers.ModelSerializer):
    students = EnrolledCourseSerializer(many=True, required=False, read_only=True,)      # any custom functions need to have this so it can properly access the correct model and serialize it to run the custom function
    curriculum = VariantSerializer(many=True, required=False, read_only=True,)
    lectures = VariantItemSerializer(many=True, required=False, read_only=True,)
    reviews = ReviewSerializer(many=True, read_only=True, required=False)

    class Meta:
        fields = ["id", "category", "teacher", "file", "image", "title", "description", "price", "language", "level", "platform_status", "teacher_course_status", "featured", "course_id", "slug", "date", "students", "curriculum", "lectures", "average_rating", "rating_count", "reviews",]
        model = api_models.Course

    # Controlling the depth of our json objects returned
    # Without this, our courses was not returning the teachers information, just was returning 1
    # This is how far into our foreign key/manytomany models we go, and through how many foreignKeys inside of the children models we go
    # EXTREMELY IMPORTANT IMPORTANT IMPORTANT IMPORTANT IMPORTANT IMPORTANT IMPORTANT IMPORTANT IMPORTANT IMPORTANT IMPORTANT IMPORTANT IMPORTANT IMPORTANT IMPORTANT IMPORTANT
    def __init__(self, *args, **kwargs):
        super(CourseSerializer, self).__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.method == "POST":
            self.Meta.depth = 0
        else:
            self.Meta.depth = 3

        
