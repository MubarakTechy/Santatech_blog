from django.urls import path
from django.contrib import admin
from . import views


urlpatterns = [
    path("", views.Home, name="Home"),
    # path("about/", views.about, name="about"),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/create/', views.create_post_view, name='create_post'),
    path('dashboard/mypost/', views.my_posts_view, name='my_post'),
    path('dashboard/profile/', views.profile_view, name='profile'),
    # post management with title slug
    path('dashboard/post/<slug:slug>/edit/', views.edit_post_view, name='edit_post'),
    path('dashboard/post/<int:id>/delete/', views.delete_post_view, name='delete_post'),

    # path('post/<slug:slug>/', views.post_detail, name='post'),
    path('post/<slug:slug>/comment/', views.add_comment, name='add_comment' ),
    path('post/<slug:slug>/', views.post, name='post'),
]