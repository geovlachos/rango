from django import forms
from django.contrib.auth.models import User
from rango.models import Page, Category, UserProfile


class CategoryForm(forms.ModelForm):
    name = forms.CharField(max_length=128,
                           help_text='Please enter the category name:')
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    likes = forms.IntegerField(widget=forms.HiddenInput(), initial=0)

    class Meta:
        model = Category


class PageForm(forms.ModelForm):
    title = forms.CharField(max_length=128,
                            help_text='Please enter the title of the page:')
    url = forms.URLField(max_length=200,
                         help_text='Please enter the URL of the page:')
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)

    class Meta:
        model = Page
        fields = ['title', 'url', 'views']

    def clean(self):
        cleaned_data = self.cleaned_data
        url = cleaned_data.get('url')
        if url and not (url.startswith('http://') or url.startswith('https://')):
            url = 'http://' + url
            cleaned_data['url'] = url
        return cleaned_data


class UserForm(forms.ModelForm):
    first_name = forms.CharField(help_text="Please enter your first name:")
    last_name = forms.CharField(help_text="Please enter your last name:")
    username = forms.CharField(help_text="Please enter a username:")
    password = forms.CharField(widget=forms.PasswordInput(render_value=True),
                               help_text="Please enter a password:")
    retype_password = forms.CharField(widget=forms.PasswordInput(
                                      render_value=True),
                                      help_text="Retype your password:")
    email = forms.EmailField(help_text="Please enter your email:")
    retype_email = forms.EmailField(help_text="Retype your email:")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username',
                  'password', 'retype_password', 'email', 'retype_email']

    def clean_username(self):
        try:
             User.objects.get(username=self.data['username'])
        except User.DoesNotExist:
            return self.data['username']
        raise forms.ValidationError('This username is already taken.')

    def clean_password(self):
        if self.data['password'] != self.data['retype_password']:
            raise forms.ValidationError('Passwords are not the same.')
        return self.data['password']

    def clean_email(self):
        if self.data['email'] != self.data['retype_email']:
            raise forms.ValidationError('Emails are not the same.')
        return self.data['email']


class UserProfileForm(forms.ModelForm):
    website = forms.URLField(help_text="Please enter your website:",
                             required=False)
    picture = forms.ImageField(help_text="Select a profile image to upload:",
                               required=False)

    class Meta:
        model = UserProfile
        fields = ['website', 'picture']


class UserUpdateForm(UserForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'retype_email']

    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        self.fields.pop('username')
        self.fields.pop('password')
        self.fields.pop('retype_password')


class UserPasswordChangeForm(UserForm):
    old_password = forms.CharField(widget=forms.PasswordInput(),
                                   help_text="Please enter your OLD password:")

    class Meta:
        model = User
        fields = ['old_password', 'password', 'retype_password']

    def __init__(self, *args, **kwargs):
        super(UserPasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields.pop('first_name')
        self.fields.pop('last_name')
        self.fields.pop('username')
        self.fields.pop('email')
        self.fields.pop('retype_email')
        self.fields['password'].widget = \
            forms.PasswordInput(render_value=False)
        self.fields['retype_password'].widget = \
            forms.PasswordInput(render_value=False)

    def clean_old_password(self):
        user = User.objects.get(username=self.instance.username)
        if user.is_staff or user.is_superuser:
            raise forms.ValidationError('Staff users cannot change their \
                password from here.')
        valid_old_password = user.check_password(self.data['old_password'])
        if not valid_old_password:
            raise forms.ValidationError('Invalid Password.')
        return self.data['old_password']


class UserDeleteForm(UserPasswordChangeForm):
    class Meta:
        model = User
        fields = ['old_password']

    def __init__(self, *args, **kwargs):
        super(UserDeleteForm, self).__init__(*args, **kwargs)
        self.fields.pop('password')
        self.fields.pop('retype_password')
        self.fields['old_password'].help_text= "Please enter your password:"


class EditPageForm(PageForm):
    category = forms.ModelChoiceField(queryset=Category.objects.all(),
                                      empty_label=None,
                                      help_text="Select a page Category:")
    class Meta:
        model = Page
