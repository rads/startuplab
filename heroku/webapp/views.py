#TODO clean up these imports and split up this file
from datetime import datetime
import json
from functools import wraps
from django.db import connection
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect, get_object_or_404
from webapp import forms, models, settings
from django.core import serializers
from django.contrib import auth
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


# Helper functions
def JsonResponse(obj):
    return HttpResponse(json.dumps(obj), mimetype="application/json")

def render_to(template, mimetype=None):
    """ Use this decorator to render the returned dictionary from a function
        to a template in the proper context. If return value is not a dictionary,
        it is not modified. """
    def renderer(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            output = func(request, *args, **kwargs)
            if not isinstance(output, dict):
                return output
            return render_to_response(template, 
                                      output, 
                                      context_instance=RequestContext(request),
                                      mimetype=mimetype)
        return wrapper
    return renderer

def _sql_lock_string(sql):
    return sql + ' FOR UPDATE' 

def _lock_dat_shit(model_instance, field):
    """ 
        Given a model instance and a field name (string), calling this function
        will lock the row corresponding to the model instance until an UPDATE is
        called on that row, and then update that field on the model instance with
        the locked value in the DB. 
        YOU MUST CALL THIS FUNCTION FROM SOMETHING WRAPPED IN @transaction.commit_on_success
        WHICH ALSO CALLS model_instance.save() OR ELSE I CAN'T GUARANTEE WTF WILL HAPPEN
        This means you MUST wrap this in a try block where you release the lock in 
        "finally" in case shit goes wrong.
    """
    #TODO make this into something I can use in a 'with' block

    model_type = model_instance.__class__
    query = model_type.objects.filter(id = model_instance.id).values_list(field)
    
    # get the SQL that django would have generated
    (raw_sql, params) = query._as_sql(connection=connection)
    sql = ''

    # don't do anything locally because SQLite sucks
    # TODO(nikolai) set up postgres on dev machine so that we don't have to deploy to test
    if settings.DEBUG:
        sql = raw_sql
    else:
        sql = _sql_lock_string(raw_sql)

    # LOCK DAT SHIT
    cursor = connection.cursor()
    cursor.execute(sql, params)
    
    # MAKE SURE NOBODY FUCKS WITH OUR FIELD, YO
    field_value = cursor.fetchone()[0]
    setattr(model_instance, field, field_value)


# End helper functions


@render_to('index.html')
def index(request):
    return {}

@render_to('signup.html')
#TODO refactor to not use django forms
def signup(request):
    if request.method == 'POST': 
        form = forms.SignUpForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            user = User.objects.create_user(data['username'], data['email'], data['pass1'])
            #TODO catch if this fails and don't try to log the user in

            login(request, authenticate(username=data['username'], password=data['pass1']))
            return redirect(index)

        else: #TODO if form is not valid?
            pass

    elif request.method == 'GET':
        form = forms.SignUpForm()
    
    return {'form': form}

@render_to('signin.html')
#TODO refactor to not use django forms
def signin(request):

    if request.user.is_authenticated(): 
        return redirect(index)

    if request.method == 'POST':
        un = request.POST['username']
        pw = request.POST['password']
        user = authenticate(username=un, password=pw)

        if user is not None:
            login(request, user)
            return redirect(request.POST.get('next', '/index/'))
        
        else:
            form = AuthenticationForm(initial={'username':un})
            error = "Wrong username or password"
            return { 
                'form': form,
                'error': error,
                'next': request.POST.get('next', '/index/')
            }

    elif request.method == 'GET':        
        success_redirect_url = request.GET.get('next', '/index/')
        
        form = AuthenticationForm()
        return { 'form': form, 'next': success_redirect_url }




def signout(request):
    logout(request)
    return redirect(index)

@login_required
@render_to('feed.html')
def feed(request):
    return {}

@login_required
def add_message(request):
    """ Hit by an AJAX call. Adds the given message to the bid's interaction. If no
        interaction exists, it makes one. """
    try:
        user = request.user
        bid = models.Bid.objects.get(id=request.POST.get('bidID')) 
        interaction = models.BidInteraction.objects.get_or_create(parentBid=bid, owner=user)

        msg = models.InteractionMessage()
        msg.interaction = interaction
        msg.text = request.POST.get('message', '')
        msg.timestamp = datetime.now()
        msg.owner = request.user # exists because of login_required
        msg.save()
        return JsonResponse({'success': True})
    
    except Exception, e:
        #TODO log
        return JsonResponse({'success': False, 'msg': "Something went wrong"})


# API under discussion
# This is called for the successful termination of an interaction 
# (and will trigger an exchange of credits)  
def closeInteraction(interaction):
    bid = interaction.parentBid    
    #TODO(andrey) discuss and implement bid closure
    
    #TODO(andrey) error checking (and logging)
    try_transact_funds(bid.owner, interaction.owner, interaction.offerAmount, bid)


def getInteractionsForUser(request):
    """ JSON: Gets bids that this user responded to, as well as all of the messages """ 
    user = request.user
    bids = models.Bid.objects.filter(owner=user)
    interactions = models.BidInteraction.objects.filter(owner=user)    
    interaction_dicts = []
    for interaction in interactions:
        pass         

    return { 'bids': bids, 'interactions': interaction_dicts }


def getMessagesForBid(request):
    bidid = request.GET.get('id')
    bid = models.Bid.objects.get(id=bidid)
    interactions = models.BidInteraction.objects.filter(parentBid=bid)
    ret = []
    for interaction in interactions:
        messages = models.InteractionMessage.objects.filter(interaction=interaction).order_by('timestamp')
        map(messages, lambda x: {'name': x.owner.username, 'msg': x.text})
        ret.push(messages)

    return JsonResponse(ret)

@login_required
@render_to('post.html')
def newbid(request):      # TODO in progress, don't touch
    if request.method == 'GET':
        return {}

    elif request.method == 'POST':
        raw_tags = request.POST.get('tags', '')
        tags = map(lambda x: x.strip(' '), raw_tags.split(','))
        
        bid = models.Bid()
        bid.owner = request.user
        bid.initialOffer = request.POST.get('initaialOffer', 0)
        bid.title = request.POST.get('title')

        datetime_str = request.POST.get('expiretime')
        bid.expiretime = datetime.strptime(datetime_str, "%m/%d/%Y") 
        
        bid.posttime = datetime.now()
        bid.description = request.POST.get('description', '')
       
        raw_tags = request.POST.get('tags', '')
        tags = map(lambda x: x.strip(' '), raw_tags.split(','))   
           
        tagModels = []
                       
        for tag in tags:
            print tag + " added to DB"
            newTag = models.Tag(name = tag)
            newTag.save()
            tagModels.append(newTag)
       
        # stupid fix to get the bid to have a pk so the many-to-many relationship works 
        bid.save()        
        bid.tags = tagModels
        bid.save()

        #TODO(andrey)  there is some good default page for successfully saving a bid
        # it's probably something out of the bid interaction user flow
        return HttpResponse("good job") 

@csrf_exempt
def querybids(request):
    
        # TODO(nikolai) replace this with a better serialization solution
    def simplify(bid):
        ret = {}
        ret['id'] = bid.id
        ret['title'] = bid.title
        ret['description'] = bid.description
        ret['expiretime'] = str(bid.expiretime)
        # TODO get the list of tag names for tags it has
        # I tried  map(lambda x: x.name, bid.tags)  but it doesn't work
        # also tried  list(bid.tags)  but it's not a queryset so that doesn't work
        ret['tags'] = ["TODO"]
        return ret

    # Applies the various filters to a query
    def filtrate(obj):
        return obj

    # for now this is a sane default. Eventually server should set a hard 
    # max on how many it gets from the DB
    if request.GET.getlist('tags[]') == [] and request.GET.getlist('keywords[]') == []:
        return JsonResponse(map(simplify, list(models.Bid.objects.all())))

    tags = []
    if request.GET.getlist('tags[]'):
        tags = request.GET.getlist('tags[]')
    
    keywords = []
    if request.GET.get('keywords[]'):
        keywords = request.GET.get('keywords[]')
       
        
    # initialize to empty resultset so that we can use union operator 
    data = models.Bid.objects.none()
    
    # Assumption : all of these tags already exist in the database
    for tag in tags:
        try:
            newTag = models.Tag.objects.get(name=tag)
            data = data | (filtrate(newTag.bid_set.all()))
        except Exception, e:
            #TODO log(e)
            print "THIS CODE PATH HURTS MAKE IT STOP ='["

    #TODO add keyword search

    return JsonResponse(map(simplify, data))



@csrf_exempt
def alltags(request):
    #TODO make this only get tags that have bids
    # like if someone added a stupid tag nobody uses through their profile, don't
    # auto-suggest it for people querying bids
    """ Get a list of all the tags. Used to populate auto-suggest field thing. """
    return JsonResponse(map(lambda x: x.name, list(models.Tag.objects.all())))

    
@login_required
@render_to('profile.html')
def profile(request, username=''):
    """ Show a user's profile. If the profile is the profile of whoever is logged
        in, allow the user to POST and edit fields. 
        Returns full page for GET and JSON {success, error} object for POST"""
        
    # the user that is logged in
    session_user = request.user
    profile_user = get_object_or_404(User, username=username)

    # Note: The view passes the whole profile to the template engine, which contains
    # stuff that may not need to be visible to people who are not viewing their own 
    # profile. This means it is up to the template code to not expose anything sensitive
    # for now.
    profile = profile_user.profile
    is_own_profile = (session_user == profile_user)
    

    if request.method == 'GET':
        return { 'profile': profile, 'is_own_profile': is_own_profile }
    
    elif request.method == 'POST':
        # A POST is made to this URL every time any field or combinations of fields
        # are modified. The client is free to send updates consisting of any combination
        # of fields. 


        ### Go through each field and update as necessary, but do not save the profile
        ### object to the db until all fields are updated

        if request.POST.getlist('tags[]'):
            tag_names = request.POST.getlist('tags[]')
            #TODO(andrey)  I want to save this list of tags to UserProfile just like
            # we already do for Bid.tags elsewhere. I think it's a good idea to let them
            # create new tags from their profile too, so we need to have basically the
            # exact same functionality in both places. 
            # Maybe something like
            ## tags = tags_from_names(tag_names)   <---- creates new tags if they don't exist
            ## userprofile.tags = tags
            ## userprofile.save()

        # non-array example
        if request.POST.get('shit'):
            pass
            

        return JsonResponse()


### credit transactions
## If you touch this shit without telling me I will fuck you up

## EXCHANGE is a magic user who we can give funds to via backdoor.
## Adding/removing funds to a user account directly (as in, not user-to-user)
## is done by making transactions to/from EXCHANGE.
## This is NOT a scalable solution because EXCHANGE's user profile is locked
## for every transaction.

## Assumes credits never overflow.

from django.db import transaction

def record_transaction(from_username, to_username, amount, timestamp, bid=None):
    """ Just records the transaction. Assumes caller is handling correctness / locking. """
    #TODO logger thing
    trans = models.Transaction(
        from_user = User.objects.get(username=from_username),
        to_user = User.objects.get(username=to_username),
        amount = amount,
        time = timestamp,
        bid = bid
    )
    trans.save()
    

@transaction.commit_on_success
#TODO(nikolai) Do you really need both the bid and the from_username? 
# In fact you can find all of this from just the interaction! 
# >>> Interactions aren't the only ways transactions could happen
def try_transact_funds(from_username, to_username, amount, bid=None):
    """ Returns (success, msg) tuple """
    try:
        from_prof = User.objects.get(username=from_username).profile
        to_prof = User.objects.get(username=to_username).profile
    except User.DoesNotExist:
        print "uh oh"
        #TODO logger

    try:
        _lock_dat_shit(from_prof, 'credits')
        _lock_dat_shit(to_prof, 'credits')
        if (from_prof.credits < amount):
            if from_username == 'EXCHANGE': # if the exchange runs out, re-up it
                from_prof.credits += 10000 + amount # in case transaction is more than 10000
            else:
                return (False, "Not enough credits") 

        #TODO think of more ways this could go wrong
        
        record_transaction(from_username, to_username, amount, datetime.now(), bid)
        from_prof.credits -= amount
        to_prof.credits += amount
        # saves in finally block
        return (True, "success")

    except Exception, msg:
        return (False, "Something went wrong")
        #TODO log(msg)

    finally:
        # unlocks the fields
        from_prof.save()
        to_prof.save()


@transaction.commit_on_success
def add_credit_backdoor(username, amount):
    """ Use try_transact_credits to make all transactions except backdoor bonuses """
    user = User.objects.get(username=username)
    user_profile = user.profile
    _lock_dat_shit(user_profile, 'credits')
    try:
        # safety zone start
        user_profile.credits += amount
        record_transaction('EXCHANGE', username, amount, datetime.now(), None)
    finally:
        user_profile.save()
        # safety zone end


@csrf_exempt
def credit_test(request):
    res = ''

    if (request.GET.get('act') == 'transact'):
        success, msg = try_transact_funds('nikolai', 'u1', 5)
        res += msg
    elif request.GET.get('act') == 'add':
        add_credit_backdoor(request.GET.get('username'), int(request.GET.get('amount')))
        res += 'added credits'

    return HttpResponse(res)


