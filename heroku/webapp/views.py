#TODO clean up these imports and split up this file
from datetime import datetime
import json
from functools import wraps
from django.db.models import Q
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect, get_object_or_404
from webapp import forms, models
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
    return HttpResponse(serializers.serialize('json', obj), mimetype="application/json")

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
        
        initialOffer = request.POST.get('initialOffer', '')
        if (False):
            # TODO validation bullshit
            return { errors: 'validation fail' }
        
        bid = models.Bid()
        bid.owner = request.user
        bid.initialOffer = request.POST.get('initaialOffer', 0)

        datetime_str = request.POST.get('expiretime')
        bid.expiretime = datetime.strptime(datetime_str, "%m/%d/%Y") 
        
        bid.posttime = datetime.now()
        bid.description = request.POST.get('description', '')
       
        raw_tags = request.POST.get('tags', '')
        tags = map(lambda x: x.strip(' '), raw_tags.split(','))
        print tags 
        # bid.tags = some shit with tags
        # TODO(andrey)  figure out how to get an array of tag names into 
        # the bid ManyToMany field properly (look at Tag and Bid models)
        
        
        bid.save()


        return HttpResponse("good job") 

@csrf_exempt
def querybids(request):
    """ Use this to do AJAX calls to update filter settings """
    data = models.Bid.objects.all()
    return JsonResponse(data)

@csrf_exempt
def alltags(request):
    """ Get a list of all the tags. Used to populate auto-suggest field thing. """
    return map(lambda x: x.name, models.Tag.objects.all())

@login_required
@render_to('profile.html')
def profile(request, username=''):
    """ Show a user's profile. If the profile is the profile of whoever is logged
        in, allow the user to POST and edit fields. """

    if request.method == 'GET':
        # the user that is logged in
        session_user = request.user
        profile_user = get_object_or_404(User, username=username)

        # Note: The view passes the whole profile to the template engine, which contains
        # stuff that may not need to be visible to people who are not viewing their own 
        # profile. This means it is up to the template code to not expose anything sensitive
        # for now.
        profile = profile_user.profile
        own_profile = (session_user == profile_user)
    
        return { 'profile': profile, 'own_profile': own_profile }
    
    elif request.method == 'POST':
        # A POST is made to this URL every time any field or combinations of fields
        # are modified. The client is free to send updates consisting of any combination
        # of fields. 
        user = request.user  # authenticated by login_required
            
        # Example for how to do all other field updates
        if request.POST['tags']:
            # TODO(andrey) adapt whatever you make for new bid to work here
            pass 

