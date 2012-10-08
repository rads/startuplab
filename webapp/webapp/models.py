from django.db import models
from django.contrib.auth.models import User


class PostTag(models.Model):
    name = models.CharField(max_length=30)

# Requests for help.
class Post(models.Model):
    owner = models.ForeignKey(User)
    title = models.CharField(max_length=100)
    text = models.CharField(max_length=1000)
    amount = models.IntegerField()
    tags = models.ManyToManyField(PostTag)
    endtime = models.DateTimeField() # By when does the user need this request filled?
    posttime = models.DateTimeField(auto_now_add=True)
    edittime = models.DateTimeField(auto_now=True)

# additional info about users that is not part of django's auth model
class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    rating = models.DecimalField(max_digits=15, decimal_places=2)

# Attach a handle to the user's profile to the user object. Creates one
# if it does not exist yet.
User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])
