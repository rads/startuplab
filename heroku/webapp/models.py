from django.db import models
from django.contrib.auth.models import User


class Tag(models.Model):
    name = models.CharField(max_length=30)

# Requests for help.
class Bid(models.Model):
    owner = models.ForeignKey(User)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    initialOffer = models.IntegerField()
    tags = models.ManyToManyField(Tag)
    expiretime = models.DateTimeField() # By when does the user need this request filled?
    posttime = models.DateTimeField(auto_now_add=True)

class Transaction(models.Model):
    """ Records a transaction between two users """
    # related_name is what this field is called in the reverse relation django
    # automatically makes from User back to Transaction
    buyer = models.ForeignKey(User, related_name='transaction_buyer')
    seller = models.ForeignKey(User, related_name='transaction_seller')
    
    amount = models.IntegerField()
    time = models.DateTimeField(auto_now_add=True) # defaults to datetime row is created

class BidInteraction(models.Model):
    """ A bid interaction represents an offer for a particular bid and all related info. """
    parentBid = models.ForeignKey(Bid)
    offerAmount = models.IntegerField()
    owner = models.ForeignKey(User)
    accepted = models.BooleanField(default=False)

    # Null if interaction is not finished yet
    #TODO make nullable
    transaction = models.ForeignKey(Transaction)

class InteractionMessage(models.Model):
    interaction = models.ForeignKey(BidInteraction) 
    text = models.CharField(max_length=10000)
    timestamp = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User)

# additional info about users that is not part of django's auth model
class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    rating = models.DecimalField(max_digits=15, decimal_places=2)
    credits = models.IntegerField()

# Attach a handle to the user's profile to the user object. Creates one
# if it does not exist yet.
User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])


