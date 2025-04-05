from django.db import models
from django.utils.text import slugify
from shortuuid.django_fields import ShortUUIDField
from django.utils import timezone
from moviepy.editor import VideoFileClip
import math

from userauths.models import User, Profile


# These are Tuples that are used in the below (Course) to give choices to the model or something
LANGUAGE = (
    ("English", "English"),
    ("Spanish", "Spanish"),
    ("French", "French"),
)

LEVEL = (
    ("Beginner", "Beginner"),
    ("Intermediate", "Intermediate"),
    ("Advanced", "Advanced"),
)

TEACHER_STATUS = (
    ("Draft", "Draft"),
    ("Disabled", "Disabled"),
    ("Published", "Published"),
)

PAYMENT_STATUS = (
    ("Paid", "Paid"),
    ("Processing", "Processing"),
    ("Failed", "Failed"),
)

PLATFORM_STATUS = (
    ("Review", "Review"),
    ("Disabled", "Disabled"),
    ("Draft", "Draft"),
    ("Published", "Published"),
)

# Important to note: the value is an integer and not a string. I had to fix this bug before
RATING = (
    (1, "1 Stars"),
    (2, "2 Stars"),
    (3, "3 Stars"),
    (4, "4 Stars"),
    (5, "5 Stars"),
)

NOTI_TYPE = (
    ("New Order", "New Order"),
    ("New Review", "New Review"),
    ("New Course Question", "New Course Question"),
    ("Course Published", "Course Published"),
    ("Course Enrollment Completed", "Course Enrollment Completed"),
)



class Teacher(models.Model):
                                                                         # CASCADE means, as soon as we delete a User from the database, we also want to delete the Teacher connected to it
    user = models.OneToOneField(User, on_delete=models.CASCADE)          # the OneToOneField is used instead of ForeignKey(), because we want to tell it that a Teacher should only have one User associated, and not multiple Users
    image = models.FileField(upload_to="course-file", blank=True, null=True, default="default.jpg")       # the upload_to is just a folder that we will store the uploaded images into I believe
    full_name = models.CharField(max_length=100)
    bio = models.CharField(max_length=100, null=True, blank=True)
    facebook = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    about = models.TextField(null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)


    def __str__(self):
        return self.full_name

    #  I think this is getting the students connected to a teacher
    def students(self):
        return CartOrderItem.objects.filter(teacher=self)      # returning all of the CartOrderItem objects where the teacher is equal to the teacher it is called on. 

    # Getting all courses associated with the teacher
    def courses(self):
        return Course.objects.filter(teacher=self)

    # Finding how many reviews the courses have that are associated with this Teacher
    def review(Self):
        return Course.objects.filter(teacher=self).count()

class Category(models.Model):
    title = models.CharField(max_length=100)
    image = models.FileField(upload_to="course-file", default="category.jpg", null=True, blank=True)
    active = models.BooleanField(default=True)
    slug = models.SlugField(unique=True, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Category"
        ordering = ['title']             # this orders the categories by the title in alphabetical order

    def __str__(self):
        return self.title

    # Counting the number of courses that are in this category?
    def course_count(self):
        return Course.objects.filter(category=self).count()

    # Overriding the default save method so we can slugify
    def save(self, *args, **kwargs):
        if self.slug == "" or self.slug == None:
            self.slug = slugify(self.title)
        super(Category, self).save()

class Course(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)     # on delete of the Category, we just want to set this course to null and not delete it as well
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    file = models.FileField(upload_to="course-file", blank=True, null=True)
    image = models.FileField(upload_to="course-file", blank=True, null=True)
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    language = models.CharField(max_length=100, choices=LANGUAGE, default="English")
    level = models.CharField(max_length=100, choices=LEVEL, default="Beginner")
    platform_status = models.CharField(max_length=100, choices=PLATFORM_STATUS, default="Published")
    teacher_course_status = models.CharField(max_length=100, choices=TEACHER_STATUS, default="Published")
    featured = models.BooleanField(default=False)
    course_id = ShortUUIDField(unique=True, length=6, max_length=20, alphabet="1234567890")     # I believe this is creating us a unique id for each course automatically, which will be a length of 6 digits and will pick from the numerical numbers we passed in as alphabet
    slug = models.SlugField(unique=True, null=True, blank=True)
    date = models.DateTimeField(default=timezone.now)       # this allow it to grab the current time when it is added, but use this one because auto_Add_now does not allow us to view the data and time in the admin or something like that

    def __str__(self):
        return self.title


    # Overriding the default save method so we can slugify
    def save(self, *args, **kwargs):
        if self.slug == "" or self.slug == None:
            self.slug = slugify(self.title)
        super(Course, self).save()

    # Get all the students in the course
    def students(self):
        return EnrolledCourse.objects.filter(course=self)

    def curriculum(self):
        return Variant.objects.filter(course=self)    # the double underscore __ => it grabs the field called "variant" and then does a two step look up and grabs the course field as well. Or it is grabbing any field that is in the "variant" and quering it by something

    # Returning lectures that are related to a course
    def lectures(self):
        return VariantItem.objects.filter(variant__course=self)

    # Finding the average rating of a course
    def average_rating(self):
        average_rating = Review.objects.filter(course=self, active=True).aggregate(avg_rating=models.Avg('rating'))   # finding all of the Reviews that are associated with this course, then aggregating them by average. In Reviews model, there will be a field called 'rating'. We are using the built in Django Avg function to find the average of all of the 'rating' that are in the returned rows of data from Review that are associated with this course  
        return average_rating['avg_rating']

    # Counting the total number of rated reviews that are associated with the course. Comes from the Review table
    def rating_count(self):
        return Review.objects.filter(course=self, active=True).count()

    # Returning all of the reviews associated with this course
    def reviews(self):
        return Review.objects.filter(course=self, active=True)

class Variant(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=1000)
    variant_id = ShortUUIDField(unique=True, length=6, max_length=20, alphabet="1234567890")
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

    def variant_items(self):
        return VariantItem.objects.filter(variant=self)

class VariantItem(models.Model):
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE, related_name="variant_items")
    title = models.CharField(max_length=1000)
    description = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to="course-file", null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    content_duration = models.CharField(max_length=1000, null=True, blank=True)
    preview = models.BooleanField(default=False)
    variant_item_id = ShortUUIDField(unique=True, length=6, max_length=20, alphabet="1234567890")
    date = models.DateTimeField(default=timezone.now)


    # This appears to be using the foreign key column to go and get the parent variant's title, through the variant_item(self) method created in the Variant model. Then it is getting its on title. 
    def __str__(self):
        return f"{self.variant.title} - {self.title}"

    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)     # this is actually calling the original save method immediately, and passing in all of the original parameters

        if self.file:
            clip = VideoFileCLip(self.file.path)      # this is passing in the file that was uploaded and it will have a path with it
            duration_seconds = clip.duration          # the duration is returned in number of seconds it is long

            minutes, remainder = divmod(duration_seconds, 60)       # after ever 60 seconds it will add 1 minute to the minutes. divmod() => takes two values, something to divide and how much to divide by. It returns two values, the number of times it could divide by it, and the remainer left over after it couldn't divide a whole time any longer
            minutes = math.floor(minutes)               # rounding the minutes returned to the nearest integer
            seconds = math.floor(remainder) 

            duration_text = f"{minutes}m {seconds}s"         # formatting our return to be something we can use such as: 49m 34s
            self.content_duration = duration_text
            super().save(update_fields=['content_duration'])       # we are only resaving fields that have been updated since we first saved fields in the beginning

class Question_Answer(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True )      # this means one User can have many Questions
    title = models.CharField(max_length=1000, null=True, blank=True)
    qa_id = ShortUUIDField(unique=True, length=6, max_length=20, alphabet="1234567890")
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.course.title}"         


    class Meta:
        ordering = ['-date']

    # Returning all the messages related to this question and answer
    def messages(self):
        return Question_Answer_Message.objects.filter(question=self)


    # Getting the profile of the user associated with the question
    def profile(self):
        return Profile.objects.get(user=self.user)

class Question_Answer_Message(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    question = models.ForeignKey(Question_Answer, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True )
    message = models.TextField(null=True, blank=True)
    qam_id = ShortUUIDField(unique=True, length=6, max_length=20, alphabet="1234567890")
    qa_id = ShortUUIDField(unique=True, length=6, max_length=20, alphabet="1234567890")
    date = models.DateTimeField(default=timezone.now)


    def __str__(self):
        return f"{self.user.username} - {self.course.title}"         


    class Meta:
        ordering = ['date']         # ordering from oldest to newest

    # Getting the profile of the user associated with the question
    def profile(self):
        return Profile.objects.get(user=self.user)

class Cart(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True )
    price = models.DecimalField(max_digits=12, default=0.00, decimal_places=2)
    tax_fee = models.DecimalField(max_digits=12, default=0.00, decimal_places=2)
    total = models.DecimalField(max_digits=12, default=0.00, decimal_places=2)
    country = models.CharField(max_length=100, null=True, blank=True)
    cart_id = ShortUUIDField( length=6, max_length=20, alphabet="1234567890")
    date = models.DateTimeField(default=timezone.now)


    def __str__(self):
        return self.course.title

class CartOrder(models.Model):
    student = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True )
    teachers = models.ManyToManyField(Teacher, blank=True)
    sub_total = models.DecimalField(max_digits=12, default=0.00, decimal_places=2)
    tax_fee = models.DecimalField(max_digits=12, default=0.00, decimal_places=2)
    total = models.DecimalField(max_digits=12, default=0.00, decimal_places=2)
    initial_total = models.DecimalField(max_digits=12, default=0.00, decimal_places=2)
    saved = models.DecimalField(max_digits=12, default=0.00, decimal_places=2)
    payment_status = models.CharField(max_length=255, choices=PAYMENT_STATUS, default="Processing")
    full_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    coupons = models.ManyToManyField("api.Coupon", blank=True)        # null=True    does not work on ManyToManyField()
    stripe_session_id = models.CharField(max_length=1000, null=True, blank=True)
    oid = ShortUUIDField(unique=True, length=6, max_length=20, alphabet="1234567890")
    date = models.DateTimeField(default=timezone.now)


    class Meta:
        ordering = ['-date']           # ordering from newest order to the oldest order


    def order_items(self):
        return CartOrderItem.objects.filter(order=self)


    def __str__(self):
        return self.oid

class CartOrderItem(models.Model):
    order = models.ForeignKey(CartOrder, on_delete=models.CASCADE, related_name="orderitem")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="order_item")
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=12, default=0.00, decimal_places=2)
    tax_fee = models.DecimalField(max_digits=12, default=0.00, decimal_places=2)
    total = models.DecimalField(max_digits=12, default=0.00, decimal_places=2)
    initial_total = models.DecimalField(max_digits=12, default=0.00, decimal_places=2)
    saved = models.DecimalField(max_digits=12, default=0.00, decimal_places=2)
    coupons = models.ManyToManyField("api.Coupon", blank=True)
    applied_coupon = models.BooleanField(default=False)
    oid = ShortUUIDField(unique=True, length=6, max_length=20, alphabet="1234567890")
    date = models.DateTimeField(default=timezone.now)



    class Meta:
        ordering = ['-date']           # ordering from newest order to the oldest order


    def order_id(self):
        return f"Order ID #{self.order.oid}"


    def payment_status(self):
        return f"{self.order.payment_status}"


    def __str__(self):
        return self.oid

class Certificate(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True )
    certificate_id = ShortUUIDField(unique=True, length=6, max_length=20, alphabet="1234567890")
    date = models.DateTimeField(default=timezone.now)


    def __str__(self):
        return self.course.title

class CompletedLesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True )
    variant_item = models.ForeignKey(VariantItem, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)


    def __str__(self):
        return self.course.title

class EnrolledCourse(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True )
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
    order_item = models.ForeignKey(CartOrderItem, on_delete=models.CASCADE)
    enrollment_id = ShortUUIDField(unique=True, length=6, max_length=20, alphabet="1234567890")
    date = models.DateTimeField(default=timezone.now)


    def __str__(self):
        return self.course.title

    
    def lectures(self):
        return VariantItem.onjects.filter(variant__course=self.course)      # called a field lookup


    def completed_lesson(self):
        return CompletedLesson.objects.filter(course=self.course, user=self.user)

    
    def curriculum(self):
        return Variant.objects.filter(course=self.course)


    def note(self):
        return Note.objects.filter(course=self.course, user=self.user)


    def question_answer(Self):
        return Question_Answer.objects.filter(course=self.course)

    
    def review(self):
        return Review.objects.filter(course=self.course, user=self.user).first()

class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True )
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=1000, null=True, blank=True)
    note = models.TextField()
    note_id = ShortUUIDField(unique=True, length=6, max_length=20, alphabet="1234567890")
    date = models.DateTimeField(default=timezone.now)


    def __str__(self):
        return self.title

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True )
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    review = models.TextField()
    rating = models.IntegerField(choices=RATING, default=None)
    reply = models.CharField(max_length=1000, null=True, blank=True)
    active = models.BooleanField(default=False)
    date = models.DateTimeField(default=timezone.now)


    def __str__(self):
        return self.course.title

    
    def profile(self):
        return Profile.objects.get(user=self.user)       # it appears that if the field is not a ForeignKey() then we dont have to do the self.XXXXX.user

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(CartOrder, on_delete=models.SET_NULL, null=True, blank=True)
    order_item = models.ForeignKey(CartOrderItem, on_delete=models.SET_NULL, null=True, blank=True)
    review = models.ForeignKey(Review, on_delete=models.SET_NULL, null=True, blank=True)
    type = models.CharField(max_length=100, choices=NOTI_TYPE)
    seen = models.BooleanField(default=False)
    date = models.DateTimeField(default=timezone.now)


    def __str__(self):
        return self.type

class Coupon(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
    used_by = models.ManyToManyField(User, blank=True)
    code = models.CharField(max_length=50)
    discount = models.IntegerField(default=1)
    active = models.BooleanField(default=False)
    date = models.DateTimeField(default=timezone.now)


    def __str__(self):
        return self.code

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)


    def __str__(self):
        return self.code

class Country(models.Model):
    name = models.CharField(max_length=100)
    tax_rate = models.IntegerField(default=5)
    active = models.BooleanField(default=True)


    def __str__(self):
        return self.name

    






    
    














