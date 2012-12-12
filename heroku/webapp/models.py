from django.db import models
from django.contrib.auth.models import User


class Tag(models.Model):
    name = models.CharField(max_length=30, primary_key=True)
    
    def __unicode__(self):
        return self.name

# Requests for help.
class Bid(models.Model):
    owner = models.ForeignKey(User)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    initialOffer = models.IntegerField()
    tags = models.ManyToManyField(Tag)
    expiretime = models.DateTimeField() # By when does the user need this request filled?
    posttime = models.DateTimeField(auto_now_add=True)

    active = models.BooleanField(default=True)

    def __unicode__(self):
        return str(self.owner) + ': "' + self.title + '"';

class Transaction(models.Model):
    """ Records a transaction between two users """
    # related_name is what this field is called in the reverse relation django
    # automatically makes from User back to Transaction
    from_user = models.ForeignKey(User, related_name='transaction_from_user')
    to_user = models.ForeignKey(User, related_name='transaction_to_user')
    
    amount = models.IntegerField()
    time = models.DateTimeField(auto_now_add=True) # defaults to datetime row is created
    bid = models.ForeignKey(Bid, null=True)
    
    def __unicode__(self):
        return str(self.from_user) + " sent " + str(self.amount) + " to " + str(self.to_user)

class BidInteraction(models.Model):
    """ A bid interaction represents an offer for a particular bid and all related info. """
    parentBid = models.ForeignKey(Bid)
    owner = models.ForeignKey(User)
    
    def __unicode__(self):
        return str(self.owner) + " responding to bid [" + str(self.parentBid) + "]";
    
class InteractionMessage(models.Model):
    interaction = models.ForeignKey(BidInteraction) 
    text = models.CharField(max_length=10000)
    timestamp = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User)
 
    def __unicode__(self):
        return str(owner) + " said " + str(text)[:30]

class BetaEmail(models.Model):
    email = models.CharField(max_length=100)

    def __unicode__(self):
        return str(email)

# additional info about users that is not part of django's auth system
class UserProfile(models.Model):
    """ 
        The model for a user's profile is instantiated the first time it is 
        accessed. It will fail if it does not know what to initialize the row with. 
    """
    user = models.ForeignKey(User, unique=True)
    rep = models.IntegerField(default=0)
    credits = models.IntegerField(default=0)
    tags = models.ManyToManyField(Tag) # no default needed

# Attach a handle to the user's profile to the user object. Creates a profile
# if it does not exist yet.
User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])


