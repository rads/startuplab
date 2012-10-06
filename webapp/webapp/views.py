from django.template import RequestContext
from django.shortcuts import render_to_response
from webapp.forms import *
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse

def signup(request):
    if request.method == 'POST': 
        form = SignUpForm(request.POST)
        if form.is_valid():
            # any validation logic that does not touch the DB should be done in
            # SignUpForm inside forms.py
            data = form.cleaned_data
            user = User.objects.create_user(data['username'], data['email'], data['pass1'])
            user.save() # does create_user auto-save? unclear...
            return HttpResponse("User %s registered" % data['username'])
    
    elif request.method == 'GET':
        form = SignUpForm()
    
    return render_to_response(
        'dev/signup.html', 
        {'form': form},
        context_instance=RequestContext(request)
    )

def signin(request):
    pass

def signout(request):
    pass
