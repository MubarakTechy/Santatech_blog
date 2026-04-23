from django.contrib import admin
from .models import User, Post

# Register your models here.
admin.site.register(User)
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ('views',)
    # exclude = ('author',)  # exclude author from form, we'll set it in save_model

    # def save_model(self, request, obj, form, change):
    #     if not obj.author:
    #         obj.author = request.user  # set the author to the logged-in user
    #     super().save_model(request, obj, form, change)