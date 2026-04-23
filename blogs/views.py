from unittest import loader
import cloudinary
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

from django.contrib.auth import get_user_model, login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Post
from .models import User
import requests
from django.utils.text import slugify
import uuid
from django.db.models import Q


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Post, Comment

# Create your views here.
def Home(request):
    # Order by created_at descending (newest first)
    posts = Post.objects.all().order_by('-created_at')
    
    
    # Fetch real news for carousel
    news_articles = []
    try:
        api_key = '36f3605260a842eeab995d262daff1d8'  # paste your key here
        url = f'https://newsapi.org/v2/top-headlines?language=en&pageSize=8&apiKey={api_key}'
        response = requests.get(url, timeout=5)
        data = response.json()

        # Only keep articles that have both an image and a title
        news_articles = [
            article for article in data.get('articles', [])
            if article.get('urlToImage') and article.get('title')
        ][:8]  # max 8 slides

    except Exception:
        pass  # if API fails, carousel just shows nothing — won't crash the page

    return render(request, 'Home.html', {
        'posts': posts,
        'news_articles': news_articles,
    })


def post(request, slug):
    post = get_object_or_404(Post, slug=slug)

    if request.method == "POST":
        content = request.POST.get("content")
        parent_id = request.POST.get("parent_id")

        Comment.objects.create(
            post=post,
            author=request.user,
            content=content,
            parent_id=parent_id if parent_id else None
        )

        return redirect(request.path)  # 🔥 important refresh

    comments = post.comments.filter(parent__isnull=True).order_by("-created_at")

    return render(request, "SinglePost.html", {
        "post": post,
        "comments": comments
    })


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

        postSlug = slugify(title) + "-" + str(uuid.uuid4())[:6]

        Post.objects.create(
            title=title,
            content=content,
            image=image,  # ✅ pass file directly
            slug=postSlug,
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
            try:
                upload_result = cloudinary.uploader.upload(request.FILES['image'])
                post.image = upload_result.get('secure_url')
            except Exception as e:
                print("Cloudinary error:", e)
        post.save()
        return redirect('dashboard')
    return render(request, 'dashboard/edit.html', {'post': post})


#comments

def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
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

    return redirect('post', slug=post.slug)