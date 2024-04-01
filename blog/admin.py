from django.contrib import admin
from .models import Post, CustomUser, Category, Tag, BlogComment
from django.http import HttpResponse
import csv

class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'created_date', 'published_date']
    search_fields = ['title', 'author__username', 'created_date', 'published_date'] 
    actions = ['export_posts_to_csv']
    raw_id_fields = ['author']
    autocomplete_fields = ['category']
    filter_horizontal = ['tags']
    list_filter = ['published_date']

    def export_posts_to_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="posts.csv"'
        writer = csv.writer(response)
        writer.writerow(['Title','Author','text', 'Created Date', 'Published Date'])
        for post in queryset:
            writer.writerow([post.title,post.text, post.author, post.created_date, post.published_date])
        return response
    export_posts_to_csv.short_description = "Export selected posts to CSV"

class CustomUserAdmin(admin.ModelAdmin):
    search_fields = ['username', 'email', 'first_name', 'last_name'] 
    list_filter = ['published_date']

class CategoryAdmin(admin.ModelAdmin):
    search_fields = ['name'] 

class TagAdmin(admin.ModelAdmin):
    search_fields = ['name']

class BlogCommentAdmin(admin.ModelAdmin):
    search_fields = ['first_name', 'comment']  

admin.site.register(Post, PostAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(BlogComment, BlogCommentAdmin)
