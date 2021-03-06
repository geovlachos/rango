from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from rango.models import Category
from rango.models import Page
from rango.models import UserProfile
from rango.forms import CategoryForm, PageForm, EditPageForm
from rango.forms import UserForm, UserProfileForm, UserDeleteForm
from rango.forms import UserUpdateForm, UserPasswordChangeForm
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def encode_url(url):
    return url.replace(' ', '_')


def decode_url(url):
    return url.replace('_', ' ')


def get_category_list(max_results=0, contains='', request=''):
    cat_list_pages = []
    if contains:
        cat_list_pages = Category.objects.filter(
            name__contains=contains).extra(
            select={'lower_name': 'lower(name)'}).order_by('lower_name')
    else:
        cat_list_pages = Category.objects.all().extra(
            select={'lower_name': 'lower(name)'}).order_by('lower_name')

    if max_results > 0:
        if len(cat_list_pages) > max_results:
            cat_list_pages = cat_list_pages[:max_results]

    paginator = Paginator(cat_list_pages, 5)
    page_idx = request.GET.get('cat_page')
    try:
        cat_list = paginator.page(page_idx)
    except PageNotAnInteger:
        cat_list = paginator.page(1)
    except EmptyPage:
        cat_list = paginator.page(paginator.num_pages)

    for cat in cat_list:
        cat.url = encode_url(cat.name)

    return cat_list


def index(request):
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.filter(views__gte=1).order_by('-views')[:5]
    context = {'boldmessage': 'explore them...',
               'categories': category_list,
               'pages': page_list,
               'cat_list': get_category_list(request=request)
               }
    for category in category_list:
        category.url = encode_url(category.name)
    return render(request, 'rango/index.html', context)


def about(request):
    context = {'boldmessage': 'is a fantastic dude!!!!!'}
    context['cat_list'] = get_category_list(request=request)
    return render(request, 'rango/about.html', context)


def category(request, category_name_url):
    category_name = decode_url(category_name_url)
    context = {'category_name': category_name}
    context['category_name_url'] = category_name_url
    context['cat_list'] = get_category_list(request=request)
    try:
        category = Category.objects.get(name=category_name)
        pages_list = Page.objects.filter(category=category).order_by('-views')
        paginator = Paginator(pages_list, 15)
        page_idx = request.GET.get('page')
        try:
            pages = paginator.page(page_idx)
        except PageNotAnInteger:
            pages = paginator.page(1)
        except EmptyPage:
            pages = paginator.page(paginator.num_pages)

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
                  {'form': form,
                   'cat_list': get_category_list(request=request)})


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
            return redirect('/rango/category/' + category_name_url)
        else:
            print form.errors
    else:
        form = PageForm()

    return render(request, 'rango/add_page.html',
                  {'form': form,
                   'category_name_url': category_name_url,
                   'category_name': category_name,
                   'cat_list': get_category_list(request=request)}
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
                   'cat_list': get_category_list(request=request)}
                 )


def user_login(request):
    cat_list = get_category_list(request=request)
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
                              {'disabled_account': True,
                               'cat_list': cat_list})
        else:
            return render(request, 'rango/login.html',
                          {'bad_details': True,
                           'cat_list': cat_list})
    else:
        return render(request, 'rango/login.html',
                      {'cat_list': cat_list})


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/rango/')


@login_required
def profile(request):
    cat_list = get_category_list(request=request)
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
    contains = ''
    if request.method == 'GET':
        contains = request.GET['suggestion']
    #if contains:
    #    cat_list = get_category_list(5, contains)
    #else:
        cat_list = get_category_list(contains=contains, request=request)
    return render(request, 'rango/category_list.html', {'cat_list': cat_list })


@login_required
def profile_update(request):
    if request.method == 'POST':
        user = User.objects.get(username=request.user)
        user_form = UserUpdateForm(data=request.POST, instance=user)
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
        user_form = UserUpdateForm(instance=user)
        up = UserProfile.objects.get_or_create(user=user)[0]
        profile_form = UserProfileForm(instance=up)
        user_form.fields['retype_email'].initial = user_form['email'].value()

    return render(request, 'rango/profile_update.html',
                  {'user_form': user_form,
                   'profile_form': profile_form,
                   'cat_list': get_category_list(request=request)}
                 )


def check_new_username(request):
    username = None
    if request.method == 'GET':
        username = request.GET['new_username']
    if username:
        try:
            user = User.objects.get(username=username)
        except:
            user = None
        if user:
            return HttpResponse('* This username is already taken.')
    return HttpResponse('')


@login_required
def change_password(request):
    if request.method == 'POST':
        user = User.objects.get(username=request.user)
        user_form = UserPasswordChangeForm(data=request.POST, instance=user)
        if user_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user.password)
            user.save()
            return render(request, 'rango/message.html',
                          {'message_header': 'User: ' + user.username,
                           'message_body': 'Password changed successfully.',
                           'cat_list': get_category_list(request=request)}
                         )
        else:
            print user_form.errors
    else:
        user = User.objects.get(username=request.user)
        user_form = UserPasswordChangeForm(instance=user)

    return render(request, 'rango/change_password.html',
                  {'user_form': user_form,
                   'cat_list': get_category_list(request=request)}
                 )


@login_required
def delete_user(request):
    if request.method == 'POST':
        user = User.objects.get(username=request.user)
        user_form = UserDeleteForm(data=request.POST, instance=user)
        if user_form.is_valid():
            user = user_form.save(commit=False)
            up = UserProfile.objects.get(user=user)
            if up.picture:
                up.picture.delete()
            user.delete()
            logout(request)
            return render(request, 'rango/message.html',
                          {'message_header': 'User: ' + user.username,
                           'message_body': 'Account deleted successfully.',
                           'cat_list': get_category_list(request=request)}
                         )
        else:
            print user_form.errors
    else:
        user = User.objects.get(username=request.user)
        user_form = UserDeleteForm(instance=user)

    return render(request, 'rango/delete_user.html',
                  {'user_form': user_form,
                   'cat_list': get_category_list(request=request)}
                 )


@login_required
def delete_page(request, page_id):
    url = '/rango/'
    if request.method == 'GET':
        if page_id:
            try:
                page = Page.objects.get(id=page_id)
                category = page.category
                url = '/rango/category/' + encode_url(category.name)
                page.delete()
            except:
                return render(request, 'rango/message.html',
                              {'message_header': 'Page not Found',
                               'message_body': 'Requested page with ID: ' + \
                                               page_id + \
                                               ' not found for deletion',
                               'cat_list': get_category_list(request=request)}
                             )

    return redirect(url)


@login_required
def edit_page(request, page_id):
    if request.method == 'POST':
        url = '/rango/'
        page = Page.objects.get(id=page_id)
        category = page.category
        page_form = EditPageForm(data=request.POST, instance=page)
        if page_form.is_valid():
            page.save()
            url = '/rango/category/' + encode_url(category.name)
            return redirect(url)
        else:
            print page_form.errors
    else:
        if page_id:
            try:
                page = Page.objects.get(id=page_id)
                page_form = EditPageForm(instance=page)
                category = page.category
            except:
                return render(request, 'rango/message.html',
                              {'message_header': 'Page not Found',
                               'message_body': 'Requested page with ID: ' + \
                                               page_id + ' not found for edit',
                               'cat_list': get_category_list(request=request)}
                             )

    return render(request, 'rango/edit_page.html',
                  {'form': page_form,
                   'page_id': page_id,
                   'category_name': category,
                   'cat_list': get_category_list(request=request)}
                 )


@login_required
def delete_category(request, category_url):
    url = '/rango/'
    if request.method == 'GET':
        if category_url:
            try:
                category = Category.objects.get(name=decode_url(category_url))
                category.delete()
            except:
                return render(request, 'rango/message.html',
                              {'message_header': 'Category not Found',
                               'message_body': 'Requested category with URL: ' + \
                                               category_url + \
                                               ' not found for deletion',
                               'cat_list': get_category_list(request=request)}
                             )

    return redirect(url)


@login_required
def edit_category(request, category_url):
    if request.method == 'POST':
        url = '/rango/'
        category = Category.objects.get(name=decode_url(category_url))
        category_form = CategoryForm(data=request.POST, instance=category)
        if category_form.is_valid():
            category.save()
            url = '/rango/category/' + encode_url(category.name)
            return redirect(url)
        else:
            print category_form.errors
    else:
        if category_url:
            try:
                category = Category.objects.get(name=decode_url(category_url))
                category_form = CategoryForm(instance=category)
            except:
                return render(request, 'rango/message.html',
                              {'message_header': 'Category not Found',
                               'message_body': 'Requested category with URL: ' + \
                                               category_url + \
                                               ' not found for deletion',
                               'cat_list': get_category_list(request=request)}
                             )

    return render(request, 'rango/edit_category.html',
                  {'form': category_form,
                   'category_url': category_url,
                   'category_name': category,
                   'cat_list': get_category_list(request=request)}
                 )
