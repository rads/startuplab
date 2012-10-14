from datetime import datetime
from functools import wraps
from django.db.models import Q
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from webapp import forms, models
from django.contrib import auth
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse


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

@render_to('index.html')
def index(request):
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
        return { 'form' : forms.BidForm() }

    elif request.method == 'POST':
        # 
        form = forms.BidForm(request)
        if not form.is_valid: #TODO THEN DO SOMETHING ABOUT IT MAN 
            pass
        bid = form.save(commit=False) # don't save to DB quite yet...

        # add in fields that are not required in form but required in DB
        bid.owner = user
        bid.posttime = datetime.now()

def querybids(request):
    """ Use this to do AJAX calls to update filter settings """

    ## Filter options
    if "debugging":
        tags = ['yeah', 'bitch']
        pricerange = (0, 100)
    else:
        tags = request.GET['tags']
        pricerange = (request.GET['minprice'], request.GET['maxprice']) 
    ##

    resultset = models.Bid.objects.filter(
        Q(expiretime__gte = datetime.now()),
        Q(initialOffer__gte=pricerange[0]) & Q(initialOffer__lte=pricerange[1]),
    )

    return HttpResponse(resultset)
    


