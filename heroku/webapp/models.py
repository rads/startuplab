from django.db import models
from django.contrib.auth.models import User


class Tag(models.Model):
    name = models.CharField(max_length=30, primary_key=True)
    
    def __unicode__(self):
        return self.name

# Requests for help.
class Bid(models.Model):
    owner = models.ForeignKey(User)
    title = models.CharField(max_length=100, primary_key=True)
    description = models.CharField(max_length=1000)
    initialOffer = models.IntegerField()
    tags = models.ManyToManyField(Tag)
    expiretime = models.DateTimeField() # By when does the user need this request filled?
    posttime = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return str(self.owner) + ': "' + self.title + '"';

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
    
    transaction = models.ForeignKey(Transaction, null=True)

    def __unicode__(self):
        return str(self.owner) + " responding to bid [" + str(self.bid) + "]";
    

class InteractionMessage(models.Model):
    interaction = models.ForeignKey(BidInteraction) 
    text = models.CharField(max_length=10000)
    timestamp = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User)

# additional info about users that is not part of django's auth model
class UserProfile(models.Model):
    """ ALL FIELDS MUST HAVE DEFAULT VALUES
        The model for a user's profile is instantiated the first time it is 
        accessed. It will fail if it does not know what to initialize the row with. """
    user = models.ForeignKey(User, unique=True)
    rep = models.IntegerField(default=0)
    credits = models.IntegerField(default=0)
    tags = models.ManyToManyField(Tag) # no default needed
    
class UXSettings(models.Model):
    """ Configurations for things like notifications and site preferences """
    pass


# Attach a handle to the user's profile to the user object. Creates one
# if it does not exist yet.
User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])


