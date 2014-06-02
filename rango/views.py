from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from rango.models import Category
from rango.models import Page
from rango.models import UserProfile
from rango.forms import CategoryForm, PageForm
from rango.forms import UserForm, UserProfileForm, UserFormUpdate
from django.contrib.auth.models import User


def encode_url(url):
    return url.replace(' ', '_')


def decode_url(url):
    return url.replace('_', ' ')


def get_category_list(max_results=0, starts_with=''):
    cat_list = []
    if starts_with:
        cat_list = Category.objects.filter(name__istartswith=starts_with)
    else:
        cat_list = Category.objects.all()

    if max_results > 0:
        if len(cat_list) > max_results:
            cat_list = cat_list[:max_results]

    for cat in cat_list:
        cat.url = encode_url(cat.name)

    return cat_list


def index(request):
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.filter(views__gte=1).order_by('-views')[:5]
    context = {'boldmessage': 'explore them...',
               'categories': category_list,
               'pages': page_list,
               'cat_list': get_category_list()
               }
    for category in category_list:
        category.url = encode_url(category.name)
    return render(request, 'rango/index.html', context)


def about(request):
    context = {'boldmessage': 'is a fantastic dude!!!!!'}
    context['cat_list'] = get_category_list()
    return render(request, 'rango/about.html', context)


def category(request, category_name_url):
    category_name = decode_url(category_name_url)
    context = {'category_name': category_name}
    context['category_name_url'] = category_name_url
    context['cat_list'] = get_category_list()
    try:
        category = Category.objects.get(name=category_name)
        pages = Page.objects.filter(category=category).order_by('-views')
        context['pages'] = pages
        context['category'] = category
    except Category.DoesNotExist:
        pass
    return render(request, 'rango/category.html', context)


@login_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return index(request)
        else:
            print form.errors
    else:
        form = CategoryForm()

    return render(request, 'rango/add_category.html',
                  {'form': form, 'cat_list': get_category_list()})


@login_required
def add_page(request, category_name_url):
    category_name = decode_url(category_name_url)
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            page = form.save(commit=False)
            try:
                cat = Category.objects.get(name=category_name)
                page.category = cat
            except Category.DoesNotExist:
                return render(request, 'rango/add_category.html', {})
            page.views = 0
            page.save()
            return category(request, category_name_url)
        else:
            print form.errors
    else:
        form = PageForm()

    return render(request, 'rango/add_page.html',
                  {'form': form,
                   'category_name_url': category_name_url,
                   'category_name': category_name,
                   'cat_list': get_category_list()}
                 )


def register(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user.password)
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            profile.save()
            registered = True
        else:
            print user_form.errors, profile_form.errors
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request, 'rango/register.html',
                  {'user_form': user_form,
                   'profile_form': profile_form,
                   'registered': registered,
                   'cat_list': get_category_list()}
                 )


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                if request.POST.get('next') != '':
                    return HttpResponseRedirect(request.POST.get('next'))
                else:
                    return HttpResponseRedirect('/rango/')
            else:
                return render(request, 'rango/login.html',
                              {'disabled_account': True})
        else:
            return render(request, 'rango/login.html',
                          {'bad_details': True})
    else:
        return render(request, 'rango/login.html',
                      {'cat_list': get_category_list()})


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/rango/')


@login_required
def profile(request):
    cat_list = get_category_list()
    context = {'cat_list': cat_list}
    u = User.objects.get(username=request.user)
    try:
        up = UserProfile.objects.get(user=u)
    except:
        up = None
    context['user'] = u
    context['userprofile'] = up
    return render(request, 'rango/profile.html', context)


def track_url(request):
    page_id = None
    url = '/rango/'
    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']
            try:
                page = Page.objects.get(id=page_id)
                page.views = page.views + 1
                page.save()
                url = page.url
            except:
                pass

    return redirect(url)


@login_required
def like_category(request):
    cat_id = None
    if request.method == 'GET':
        cat_id = request.GET['category_id']
    likes = 0
    if cat_id:
        category = Category.objects.get(id=int(cat_id))
        if category:
            likes = category.likes + 1
            category.likes =  likes
            category.save()

    return HttpResponse(likes)


def suggest_category(request):
    cat_list = []
    starts_with = ''
    if request.method == 'GET':
        starts_with = request.GET['suggestion']

    cat_list = get_category_list(8, starts_with)

    return render(request, 'rango/category_list.html', {'cat_list': cat_list })


@login_required
def profile_update(request):
    if request.method == 'POST':
        user = User.objects.get(username=request.user)
        user_form = UserFormUpdate(data=request.POST, instance=user)
        up = UserProfile.objects.get(user=user)
        profile_form = UserProfileForm(data=request.POST, instance=up)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            profile.save()
            return redirect('/rango/profile')
        else:
            print user_form.errors, profile_form.errors
    else:
        user = User.objects.get(username=request.user)
        user_form = UserFormUpdate(instance=user)
        up = UserProfile.objects.get_or_create(user=user)[0]
        profile_form = UserProfileForm(instance=up)
        user_form.fields['email2'].initial = user_form['email'].value()

    return render(request, 'rango/profile_update.html',
                  {'user_form': user_form,
                   'profile_form': profile_form,
                   'cat_list': get_category_list()}
                 )
