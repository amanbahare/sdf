from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('post/new/', views.post_new, name='post_new'),
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),
    path('post/<slug:slug>/edit/', views.post_edit, name='post_edit'),
    path('category/<str:category>/', views.category_posts, name='category_posts'),
    path('tag/<str:tag>/', views.tags_posts, name='tags_posts'),
    path('author/<int:pk>/', views.author_posts, name='author_posts'),
    path('post/<int:pk>/comment/', views.add_comment, name='add_comment'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
