from django import forms
from django.contrib.auth.models import User
from rango.models import Page, Category, UserProfile


class CategoryForm(forms.ModelForm):
    name = forms.CharField(max_length=128,
                           help_text='Please enter the category name.')
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    likes = forms.IntegerField(widget=forms.HiddenInput(), initial=0)

    class Meta:
        model = Category


class PageForm(forms.ModelForm):
    title = forms.CharField(max_length=128,
                            help_text='Please enter the title of the page.')
    url = forms.URLField(max_length=200,
                         help_text='Please enter the URL of the page.')
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)

    class Meta:
        model = Page
        fields = ['title', 'url', 'views']

    def clean(self):
        cleaned_data = self.cleaned_data
        url = cleaned_data.get('url')
        if url and not url.startswith('http://'):
            url = 'http://' + url
            cleaned_data['url'] = url
        return cleaned_data


class UserForm(forms.ModelForm):
    username = forms.CharField(help_text="Please enter a username.")
    email = forms.CharField(help_text="Please enter your email.")
    email2 = forms.CharField(help_text="Repeat your email.")
    password = forms.CharField(widget=forms.PasswordInput(),
                               help_text="Please enter a password.")
    password2 = forms.CharField(widget=forms.PasswordInput(),
                                help_text="Repeat your password.")
    first_name = forms.CharField(help_text="Please enter your first name.")
    last_name = forms.CharField(help_text="Please enter your last name.")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username',
                  'password', 'password2', 'email', 'email2']

    def clean_username(self):
        try:
             User.objects.get(username=self.data['username'])
        except User.DoesNotExist:
            return self.data['username']
        raise forms.ValidationError('The username is already taken.')

    def clean_password(self):
        if self.data['password'] != self.data['password2']:
            raise forms.ValidationError('Passwords are not the same.')
        return self.data['password']

    def clean_email(self):
        if self.data['email'] != self.data['email2']:
            raise forms.ValidationError('Emails are not the same.')
        return self.data['email']
                                            
    def clean(self):
        cleaned_data = self.cleaned_data
        self.clean_username()
        self.clean_password()
        self.clean_email()
        return cleaned_data


class UserProfileForm(forms.ModelForm):
    website = forms.URLField(help_text="Please enter your website.",
                             required=False)
    picture = forms.ImageField(help_text="Select a profile image to upload.",
                               required=False)

    class Meta:
        model = UserProfile
        fields = ['website', 'picture']


class UserUpdateForm(forms.ModelForm):
    email = forms.CharField(help_text="Please enter your email.")
    email2 = forms.CharField(help_text="Repeat your email.")
    first_name = forms.CharField(help_text="Please enter your first name.")
    last_name = forms.CharField(help_text="Please enter your last name.")

    class Meta:
        model = User
        exclude = ('username', 'password',)
        fields = ['first_name', 'last_name', 'email', 'email2']

    def clean_email(self):
        if self.data['email'] != self.data['email2']:
            raise forms.ValidationError('Emails are not the same.')
        return self.data['email']
                                            
    def clean(self):
        cleaned_data = self.cleaned_data
        self.clean_email()
        return cleaned_data


class UserPasswordChangeForm(forms.ModelForm):
    old_password = forms.CharField(widget=forms.PasswordInput(),
                                   help_text="Please enter your OLD password.")
    password = forms.CharField(widget=forms.PasswordInput(),
                               help_text="Please enter a NEW password.")
    password2 = forms.CharField(widget=forms.PasswordInput(),
                                help_text="Repeat your new password.")

    class Meta:
        model = User
        exclude = ('username',)
        fields = ['old_password', 'password', 'password2']

    def clean_old_password(self):
        u = User.objects.get(username=self.instance.username)
        pass_check = u.check_password(self.data['old_password'])
        if not pass_check:
            raise forms.ValidationError('Invalid OLD Password.')
        return self.data['old_password']

    def clean_password(self):
        if self.data['password'] != self.data['password2']:
            raise forms.ValidationError('Passwords are not the same.')
        return self.data['password']

    def clean(self):
        cleaned_data = self.cleaned_data
        self.clean_old_password()
        self.clean_password()
        return cleaned_data
