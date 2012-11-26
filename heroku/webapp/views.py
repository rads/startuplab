from datetime import datetime
from django.shortcuts import render_to_response, redirect, get_object_or_404
from webapp import forms, models, settings
from django.contrib import auth
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt


from webapp.credits import record_transaction, try_transact_funds
from webapp.helpers import JsonResponse, render_to, simplify, _lock_dat_shit 

import logging

log_info = logging.getLogger('file_info')
log_error = logging.getLogger('django.request')

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
            #TODO catch if this fails and don't try to log the user in (and log successful creation of user if successful)

            login(request, authenticate(username=data['username'], password=data['pass1']))
            return redirect(index)

        else: #TODO if form is not valid?
            pass

    elif request.method == 'GET':
        form = forms.SignUpForm()
    
    return {'form': form}

@render_to('signin.html')
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
        success_redirect_url = request.GET.get('next', '/')
        
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
        log_error.error('Two bids with id ' + bidID)
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


@csrf_exempt
def getResponsesForBid(request):
    pass


@csrf_exempt
def getMessagesForInteraction(request):
    interactionID = request.GET.get('id')
    interaction = models.BidInteraction.objects.get(id=interactionID)
    
    interaction_dict = {}
    
    messages = list(models.InteractionMessage.objects.filter(interaction=interaction).order_by('timestamp'))
    messages_dict = map(lambda x: {'name': x.owner.username, 'msg': x.text}, messages)
    
    interaction_dict['responder'] = interaction.owner.username
    interaction_dict['messages'] = messages_dict

    return JsonResponse(interaction_dict)

@login_required
@render_to('post.html')
def newbid(request): 
    if request.method == 'GET':
        return {}

    elif request.method == 'POST':
        raw_tags = request.POST.get('tags', '')
        tags = map(lambda x: x.strip(' '), raw_tags.split(','))
        
        bid = models.Bid()
        bid.owner = request.user
        
        def fail(name, msg):
            return JsonResponse({'success': False, 'error': { 'name': name, 'msg': msg}})

        ## Begin data verification
        #TODO more error checking!
        amount = request.POST.get('initialOffer', '-1')
        if not amount.isdigit():
            return fail('initialOffer', "Invalid  amount") 

        bid.initialOffer = amount
        bid.title = request.POST.get('title')

        datetime_str = request.POST.get('expiretime')
        bid.expiretime = datetime.strptime(datetime_str, "%m/%d/%Y") 
        
        bid.posttime = datetime.now()
        bid.description = request.POST.get('description', '')
       
        raw_tags = request.POST.get('tags', '')
        tags = map(lambda x: x.strip(' '), raw_tags.split(','))   
           

        ## End data verification


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
        
        log_info.info("Succesfully created new bid with id " + str(bid.id))

        return JsonResponse({'success': True, 'redirect': '/questions/' + str(bid.id)})

@csrf_exempt
def querybids(request):
    if request.GET.get('ownerID'):
        bids = models.Bid.objects.filter(id=request.GET.get('ownerID'))
        print "returning"
        return JsonResponse(map(simplify, bids)) 

    # Applies the various filters to a query
    def filtrate(obj):
        return obj

    # Get a specific bid by id

    if request.GET.get('bidID'):
        bid = models.Bid.objects.get(id=request.GET.get('bidID'))
        return JsonResponse([simplify(bid)])

    # for now this is a sane default. Eventually server should set a hard 
    # max on how many it gets from the DB
    if request.GET.getlist('tags[]') == [] and request.GET.getlist('keywords[]') == []:
        return JsonResponse(map(simplify, list(models.Bid.objects.all())))

    tags = []
    if request.GET.getlist('tags[]'):
        tags = request.GET.getlist('tags[]')
    
    keywords = []
    if request.GET.getlist('keywords[]'):
        keywords = request.GET.getlist('keywords[]')
       
        
    # initialize to empty resultset so that we can use union operator 
    data = models.Bid.objects.none()
    
    # Assumption : all of these tags already exist in the database
    for tag in tags:
        try:
            newTag = models.Tag.objects.get(name=tag)
            data = data | (filtrate(newTag.bid_set.all()))
        except Exception, e:
            log_error.error("There is more than one tag with the name " + tag)

    #TODO add keyword search
    data_list = sorted(list(data), key=lambda x: x.initialOffer)
    print data_list
    return JsonResponse(map(simplify, data_list))


@csrf_exempt
def alltags(request):
    #TODO make this only get tags that have bids
    # like if someone added a stupid tag nobody uses through their profile, don't
    # auto-suggest it for people querying bids
    """ Get a list of all the tags. Used to populate auto-suggest field thing. """
    return JsonResponse(map(lambda x: x.name, list(models.Tag.objects.all())))

@csrf_exempt 
@login_required
@render_to('profile.html')
def profile(request, username=''):
    """ Show a user's profile. If the profile is the profile of whoever is logged
        in, allow the user to POST and edit fields. 
        Returns full page for GET and JSON {success, error} object for POST"""
    
    # the user that is logged in
    session_user = request.user
    if username == '':
        profile_user = session_user
    else:
        profile_user = get_object_or_404(User, username=username)

    # Note: The view passes the whole profile to the template engine, which contains
    # stuff that may not need to be visible to people who are not viewing their own 
    # profile. This means it is up to the template code to not expose anything sensitive
    # for now.
    profile = profile_user.profile
    is_own_profile = (session_user == profile_user)
    

    if request.method == 'GET':
        return { 
            'profile': profile, 
            'is_own_profile': is_own_profile,
            'watched_tag_string': "15-1xx, 15-2xx, 21-1xx, 21-2xx, Python, C, C#",

        }
    
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


def _single_interaction_dict(interaction):
    """ Populates a dictionary with all the information from a single interaction """
    messages = models.InteractionMessage.objects.filter(interaction=interaction)

    message_list = []
    
    for message in messages:
        message_dict = {'owner_name': message.owner.username,
                        'text': message.text,
                        'timestamp': str(message.timestamp)}
        message_list.append(message_dict)

    interaction_dict = {
        'responder_id': interaction.owner.id,
        'messages': sorted(message_list, key=lambda n: n['timestamp']).reverse(),
    }

    return interaction_dict


@login_required
@render_to('ownbid.html')
def single_bid(request, bidID):
    """ 
    Hit from /questions/<bidID>
    If the user is the owner, display the question
    and links to all interactions. If the user is not the owner, redirects to 
    /question/<bidID>/<userID>    (userID for logged in user)
    """
    bid = models.Bid.objects.get(id=bidID)
    interactions = models.BidInteraction.objects.filter(parentBid=bid)

    interactionDictList = []

    if (request.user == bid.owner):
        for interaction in interactions:
            interactionDictList.append(_single_interaction_dict(interaction))
            
        content_dict = {
            'interactions': interactionDictList,
            'bidID': bidID,
        }
        return content_dict

    else:
        return redirect('/questions/' + str(bidID) + '/' + str(request.user.id))

    
    return JsonResponse(content_dict)

@csrf_exempt
def direct_add_message(request):
    """
    Can be hit from anywhere a bid can be responded to (feed page, bid pages).
    If the user is not the owner, make sure an interaction exists and then add the message.
    """
    interactionID = int(request.POST.get('interactionID'))
    interaction = models.BidInteraction.objects.get(id=interactionID)
    message = models.InteractionMessage()
    message.interaction = interaction    
    message.text = request.POST.get('message')
    message.timestamp = datetime.now()
    message.owner = request.user
    
    message.save()
    
    #TODO(andrey) redirect to a good success page
    return JsonResponse({ 'success': True, 'name': message.owner.username, 'text': message.text })
    

@login_required
@render_to('interaction.html')
def single_interaction(request, bidID, responderID):
    """
    Hit from /questions/<bidID>/<userID>
    This shows the interaction between the bid owner and user from url.
    This should create an interaction for this user if the user has not interacted with
    the bid yet.
    """

    bid = models.Bid.objects.get(id=bidID)
    
    #OH GOD WHAT IS THIS TODO(nikolai) fix it
    if request.user.id == bid.owner.id:
        if request.user.id == responderID:
            return redirect('/questions/' + str(bidID)) # single_bid(request, bidID)
        if models.BidInteraction.objects.filter(owner__id=responderID, parentBid=bid).count() == 0:
            return redirect('/questions/' + str(bidID))  #(request, bidID)
        else:
            pass # content dict

    else:
        if request.user.id == responderID:
            pass # content dict
        else:
            pass # content dict

    tup = models.BidInteraction.objects.get_or_create(parentBid=bid, owner = User.objects.get(id=responderID))
    interaction = tup[0]
    content_dict = _single_interaction_dict(interaction)
    
    content_dict['bidID'] = bidID
    content_dict['interactionID'] = interaction.id
    content_dict['bid_owner'] = bid.owner.username

    if request.GET.get('type', '') == 'json':
        return JsonResponse(content_dict)

    return content_dict
