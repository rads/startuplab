from functools import wraps
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from webapp import forms
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
            user.save() # does create_user auto-save? unclear...
            return HttpResponse("User %s registered" % data['username'])
    
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
            return redirect(index)

    elif request.method == 'GET':        
        form = AuthenticationForm()
        return { 'form': form }

def signout(request):
    logout(request)
    return redirect(index)

@login_required
@render_to('feed.html')
def feed(request):
    return {}


@render_to('post.html')
def post(request):
    return { 'form' : forms.PostForm() } 


