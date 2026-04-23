from django.db import models
from django.utils.text import slugify

from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager
)
from cloudinary.models import CloudinaryField

# 🔥 Custom Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        user = self.create_user(email, username, password)

        user.is_staff = True
        user.is_superuser = True
        user.userType = User.UserType.ADMIN  # ✅ ensure admin role

        user.save(using=self._db)
        return user


# 🔥 Custom User Model
class User(AbstractBaseUser, PermissionsMixin):

    class UserType(models.TextChoices):
        READER = 'reader', 'Reader'
        AUTHOR = 'author', 'Author'
        ADMIN = 'admin', 'Admin'

    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)

    userType = models.CharField(
        max_length=10,
        choices=UserType.choices,
        default=UserType.READER
    )

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    profile_picture = CloudinaryField('profile_picture', blank=True, null=True)


    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.username} ({self.email})"


# Blog Post Model
class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = CloudinaryField('image', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    views = models.PositiveIntegerField(default=0)
    slug = models.SlugField(max_length=200, unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            import uuid
            self.slug = slugify(self.title) + "-" + str(uuid.uuid4())[:6]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} by {self.author.username}"


# 🔥 Comment Model
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    # 🔥 Better self-relation (threaded comments)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='replies'
    )

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"

