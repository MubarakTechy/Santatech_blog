from unittest import loader
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

from django.contrib.auth import get_user_model, login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Post
from .models import User



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Post, Comment

# Create your views here.
def Home(request):
    posts = Post.objects.all()
    return render(request, "Home.html", {"posts": posts})


def post(request, id):
  post = Post.objects.get(id=id)
  post.views += 1
  post.save()
  return render(request, 'SinglePost.html', {'post': post})



# Signup
def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        if User.objects.filter(email=email).exists():
            return render(request, 'auth/signup.html', {'error': 'Email already exists'})
        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        return redirect('login')
    return render(request, 'auth/signup.html')

# login

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            if user.userType == User.UserType.ADMIN:
                return redirect('/admin/')
            elif user.userType == User.UserType.AUTHOR:
                return redirect('/dashboard')
            elif user.userType == User.UserType.READER:
                return redirect('/')
        else:
            return render(request, 'auth/login.html', {'error': 'Invalid email or password'})
    return render(request, 'auth/login.html')

# Logout
def logout_view(request):
    logout(request)
    return redirect('login')

# Dashboard — shows user's own posts
User = get_user_model()

@login_required(login_url='login')
def dashboard_view(request):
    posts = Post.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'dashboard/index.html', {'posts': posts})


# Create Post
@login_required(login_url='login')
def create_post_view(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        image = request.FILES.get('image')
        Post.objects.create(
            title=title,
            content=content,
            image=image,
            author=request.user
        )
        return redirect('dashboard')
    return render(request, 'dashboard/create.html')

@login_required(login_url='login')
def my_posts_view(request):
    posts = Post.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'dashboard/mypost.html', {'posts': posts})



@login_required(login_url='login')
def profile_view(request):
    return render(request, 'dashboard/profile.html')

#profile image upload
@login_required(login_url='login')
def upload_profile_picture_view(request):
    if request.method == 'POST':
        profile_picture = request.FILES.get('profile_picture')
        request.user.profile_picture = profile_picture
        request.user.save()
    return redirect('profile')

@login_required(login_url='login')
def delete_post_view(request, id):
    post = Post.objects.get(id=id, author=request.user)
    post.delete()
    return redirect('dashboard')
def edit_post_view(request, id):
    post = Post.objects.get(id=id, author=request.user)
    if request.method == 'POST':
        post.title = request.POST.get('title')
        post.content = request.POST.get('content')
        if request.FILES.get('image'):
            post.image = request.FILES.get('image')
        post.save()
        return redirect('dashboard')
    return render(request, 'dashboard/edit.html', {'post': post})


#comments

def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post.views += 1
    post.save()

    # Only top-level comments (no parent)
    comments = post.comments.filter(parent=None).order_by('-created_at')

    return render(request, 'blogs/post.html', {
        'post': post,
        'comments': comments,
    })

@login_required
def add_comment(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        content = request.POST.get('content', '').strip()
        parent_id = request.POST.get('parent_id')  # will be None for top-level

        if content:
            parent = None
            if parent_id:
                try:
                    parent = Comment.objects.get(id=parent_id)
                except Comment.DoesNotExist:
                    pass

            Comment.objects.create(
                post=post,
                author=request.user,
                content=content,
                parent=parent
            )

    return redirect('post', post_id=post_id)