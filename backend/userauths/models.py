from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save

# Create your models here.

class User(AbstractUser):
    username = models.CharField(unique=True, max_length=100)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=100)
    otp = models.CharField(max_length=100, null=True, blank=True)        # seems like an otp is what is stored for a user to allow them to update a password or something???
    refresh_token = models.CharField(max_length=1000, null=True, blank=True)

    USERNAME_FIELD = 'email'           # this is making our login use an email instead of the username for them to login in with
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    # this is a special save method that checks or updates criteria and then saves the user
    def save(self, *args, **kwargs):             # this overrides the standard save process, and takes the args and kwargs that were passed in for the fields
        email_username, full_name = self.email.split("@")       # johnclayton@gmail.com   => the first part will be saved as email_username and the second part after the @ symbol will be saved as full_name
        if self.full_name == "" or self.full_name == None: 
            self.full_name == email_username                     # this line and the one above, they are saying that if the full_name from the above User is blank, then it will split the email and then save the email_username as the full_name in the model
        if self.username == "" or self.username == None:
            self.username = email_username                       # same thing as above, if its blank then we are saving email_username into the username field
        super(User, self).save(*args, **kwargs)


# this is built so that when we want users to update things, or we need to fetch user information. We are fetching or updating this model, and not
# always updating or fetching from the mmore elaborate or secure User model that is above. This make it faster and more secure
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)     # this is another way of doing it. Where if the User is deleted, then this profile field is just set to null and is not also deleted. May store permenant information for us
    image = models.FileField(upload_to="user_folder", default="default-user.jpg", null=True, blank=True)    # this is just creating a default image in case the user does not upload an image
    full_name = models.CharField(max_length=100)
    country = models.CharField(max_length=100, null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        if self.full_name:
            return str(self.full_name)
        else:
            return str(self.user.full_name)


    # this is our way of telling the User model to update when the Profile model is updated
    def save(self, *args, **kwargs):             # this overrides the standard save process, and takes the args and kwargs that were passed in for the fields
        if self.full_name == "" or self.full_name == None: 
            self.full_name == self.user.username                  # this line and the one above, they are saying that if the full_name from the above User is blank, then it will split the email and then save the email_username as the full_name in the model
                    
        super(Profile, self).save(*args, **kwargs)



def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

# This runs the following functions after it has a new save. It is running this code and passing in the User information. 
# These are essentially automatically creating the profile when a new User is created, so we dont have to manually create it everytime
post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)