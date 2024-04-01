from django.conf import settings
from django.db import models
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from autoslug import AutoSlugField
import csv
from django.http import HttpResponse
from django.core.mail import send_mail
import threading
from django.template.loader import render_to_string

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    published_date = models.DateTimeField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='post_images', blank=True, null=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username','first_name', 'last_name']
    def __str__(self):
        return self.username

class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = AutoSlugField(unique=True, populate_from='name') 
    def __str__(self):
        return self.name

class Tag(models.Model):
    name=models.CharField(max_length=100)
    slug = AutoSlugField(unique=False, populate_from='name')
    def __str__(self):
        return self.name

class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True, related_name='posts')
    tags = models.ManyToManyField(to=Tag, related_name="posts", blank=True)
    featured_image = models.ImageField(upload_to='post_images/', null=True, blank=True)
    slug = AutoSlugField(unique=True, populate_from='title') 

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        is_new = not self.pk  # Check if it's a new post
        super().save(*args, **kwargs)
        if is_new:  # If it's a new post, send email notifications
            self.send_email_notifications()

    def send_email_notifications(self):
        subject = 'New Post Notification'
        template = 'email_templates/new_post_email.html'
        context = {'post_title': self.title, 'author_name': self.author.username}
        message = render_to_string(template, context)
        recipient_list = CustomUser.objects.values_list('email', flat=True)

        # Define function to send email in a separate thread
        def send_email_to_user(recipient, subject, message):
            send_mail(subject, '', settings.EMAIL_HOST_USER, [recipient], html_message=message)

        # Create threads to send emails
        threads = []
        for recipient in recipient_list:
            thread = threading.Thread(target=send_email_to_user, args=(recipient, subject, message))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

class BlogComment(models.Model):
    sno = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=150, default='')
    comment = models.TextField()
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, related_name='replies')
    timestamp = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        print("Before saving, first_name:", self.first_name)
        self.first_name = self.user.first_name
        print("After setting first_name, first_name:", self.first_name)
        super().save(*args, **kwargs)
