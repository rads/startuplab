from django.db import models
from django.contrib.auth.models import User


# Requests for help.
class Bid(models.Model):
    owner = models.ForeignKey(models.User)
    amount = models.IntegerField()
    tags = models.ManyToManyField(PostTags)
    endtime = models.DateTimeField() # By when does the user need this request filled?
    posttime = models.DateTimeField(auto_now_add=True)
    edittime = models.DateTimeField(auto_now=True)

class PostTags(models.Model):
    name = models.CharField(max_length=30)

# additional info about users that is not part of django's auth model
class UserProfile(modelsModel):
    user = models.ForeignKey(User, unique=True)
    rating = models.DecimalField()

# Attach a handle to the user's profile to the user object. Creates one
# if it does not exist yet.
User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])
