import models
from django import forms


class BidForm(forms.ModelForm):
    class Meta:
        model = models.Bid
        fields = ('initialOffer', 'tags', 'expiretime')

class SignUpForm(forms.Form):
    email = forms.EmailField(required=True, label='Email')
    def clean_email(self):
        email = self.cleaned_data['email']
        if email[-7:] != 'cmu.edu': #TODO
            raise forms.ValidationError("You must use a CMU email")
        return email
   
    username = forms.CharField(label='Username')
    def clean_username(self):
        #TODO check if username exists
        return self.cleaned_data['username'] 

    pass1 = forms.CharField(label='Password', widget=forms.PasswordInput)  
    pass2 = forms.CharField(label='Password Again', widget=forms.PasswordInput)  
    def clean_pass2(self):
        if self.cleaned_data['pass1'] != self.cleaned_data['pass2']:
            raise forms.ValidationError("Your passwords did not match")
        return self.cleaned_data['pass2']


