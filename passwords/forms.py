
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Password
from django.contrib.auth.models import User
from .models import Profile
from .models import StoredFile

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['photo']  # Add other fields if needed

class EditFileForm(forms.ModelForm):
    class Meta:
        model = StoredFile
        # Specify the fields that you want to allow editing
        fields = ['comment']
        # Optionally, you can add widgets or customize the appearance of form fields
        widgets = {
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class FileUploadForm(forms.ModelForm):
    class Meta:
        model = StoredFile
        fields = ['file', 'file_type', 'comment']

class FileShareForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all())

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    photo = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

        

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['photo']

class PasswordForm(forms.ModelForm):
    class Meta:
        model = Password
        fields = ['website', 'username', 'password']
        widgets = {
            'password': forms.PasswordInput(),
        }

    ''' def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        if not any(char.isdigit() for char in password):
            raise forms.ValidationError("Password must contain at least one number.")
        if not any(char.isupper() for char in password):
            raise forms.ValidationError("Password must contain at least one uppercase letter.")
        if not any(char.islower() for char in password):
            raise forms.ValidationError("Password must contain at least one lowercase letter.")
        return password
    
    
     '''

