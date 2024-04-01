from django import forms

from .models import Post

from .models import CustomUser

class PostForm(forms.ModelForm):
    
    class Meta:
        model = Post
        fields = ('title', 'text','category','tags','featured_image')

class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email','profile_image']

print(ProfileForm)