from django.db import models
from django.utils.text import slugify
from shortuuid.django_fields import ShortUUIDField
from django.utils import timezone

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

PLATFORM_STATUS = (
    ("Review", "Review"),
    ("Disabled", "Disabled"),
    ("Draft", "Draft"),
    ("Published", "Published"),
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
    slug = models.SlugField(unique=True, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Category"
        ordering = ['title']             # this orders the categories by the title in alphabetical order

    def __str__(self):
        return self.title

    # Counting the number of courses that are in this category?
    def course_count(Self):
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
        return VariantItem.objects.filter(variant__course=self)    # the double underscore __ => it grabs the field called "variant" and then does a two step look up and grabs the course field as well. Or it is grabbing any field that is in the "variant" and quering it by something

    # Returning lectures that are related to a course
    def lectures(self):
        return VariantItem.objects.filter(variant__course=self)

    # Finding the average rating of a course
    def average_rating(Self)






