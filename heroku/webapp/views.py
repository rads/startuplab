#TODO clean up these imports and split up this file
from datetime import datetime
import json
from functools import wraps
from django.db.models import Q
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


# End helper functions

@render_to('index.html')
def index(request, *args):
    return {}

@render_to('signup.html')
def signup(request):
    if request.method == 'POST': 
        form = forms.SignUpForm(request.POST)
        if form.is_valid():
            # any validation logic that does not touch the DB should be done in
            # SignUpForm inside forms.py
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
@render_to('post.html')
def newbid(request):      # TODO in progress, don't touch
    if request.method == 'GET':
        return {}

    elif request.method == 'POST':
    
        
        initialOffer = request.POST.get('initialOffer', 0)
    
        raw_tags = request.POST.get('tags', '')
        tags = map(lambda x: x.strip(' '), raw_tags.split(','))
        print tags
        
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
                
        bid.tags = tagModels
        
        bid.save()

        #TODO(andrey)  there is some good default page for successfully saving a bid
        # it's probably something out of the bid interaction user flow
        return HttpResponse("good job") 

@csrf_exempt
def querybids(request):
    
    # Applies the various filters to a query
    def filtrate(obj):
        obj.filter(title__contains='bid')
        return obj

    # TODO(nikolai) replace this with a better serialization solution
    def simplify(bid):
        ret = {}
        ret['pk'] = bid.pk
        ret['title'] = bid.title
        ret['description'] = bid.description
        ret['expiretime'] = str(bid.expiretime)
        # get the list of tag names for tags it has
        # I tried  map(lambda x: x.name, bid.tags)  but it doesn't work
        # also tried  list(bid.tags)  but it's not a queryset so that doesn't work
        ret['tags'] = ["TODO"]
        return ret

    
    # for now this is a sane default. Eventually server should set a hard 
    # max on how many it gets from the DB
    if request.GET.getlist('tags[]') == []:
        return JsonResponse(map(simplify, list(models.Bid.objects.all())))

    tags = request.GET.getlist('tags[]')
    print tags
    
    # initialize to empty resultset so that we can use union operator 
    data = models.Tag.objects.none()
    
    # Assumption : all of these tags already exist in the database
    for tag in tags:
        try:
            newTag = models.Tag.objects.get(name=tag)
            data = data | (filtrate(newTag.bid_set.all()))
        except Exception, e:
            # TODO(andrey) change this to use the logger, since we want to know
            # if this code path gets hit. I guess that actually means:
            # TODO(andrey) figure out logging shit
            print "THIS CODE PATH HURTS MAKE IT STOP ='["


    return JsonResponse(map(simplify, data))

@csrf_exempt
def alltags(request):
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

from django.db import transaction


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
    """


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


@transaction.commit_on_success
def make_transaction(from_username, to_username, amount):
    pass

def remove_credit(username, amount):
    pass

@transaction.commit_on_success
def add_credit(username, amount):
    user = User.objects.get(username=username)
    user_profile = user.profile
    _lock_dat_shit(user_profile, 'credits')
    # safety zone start
    user_profile.credits += amount

    # safety zone end
    user_profile.save()


@csrf_exempt
def credit_test(request):
    res = ''

    add_credit(request.GET.get('username'), int(request.GET.get('amount')))
    res += 'added credits'
 
    return HttpResponse(res)


