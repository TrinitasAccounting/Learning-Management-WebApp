from django.db import models
from userauths.model import User, Profile



class Teacher(models.Model):
                                                                         # CASCADE means, as soon as we delete a User from the database, we also want to delete the Teacher connected to it
    user = models.OneToOneField(User, on_delete=models.CASCADE)          # the OneToOneField is used instead of ForeignKey(), because we want to tell it that a Teacher should only have one User associated, and not multiple Users
    image = models.FileField(upload_to="course-file", blank=True, null=True, default="default.jpg")       # the upload_to is just a folder that we will store the uploaded images into I believe
    full_name = models.CharField(max_length=100)
    bio = models.CharField(max_length=100, null=True, blank=True)
    facebook = mmodels.URLField(blank=True, null=True)
    twitter = mmodels.URLField(blank=True, null=True)
    linkedin = mmodels.URLField(blank=True, null=True)
    about = models.TextField(null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)


    def __str__(self):
        return self.full_name

    #  I think this is getting the students connected to a teacher
    def students(self):
        return CartOrderItem.objects.filter(teacher=self)      # returning all of the CartOrderItem objects where the teacher is equal to the teacher it is called on. 

    def courses










