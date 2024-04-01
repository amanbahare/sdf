from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from blog.forms import PostForm
from .models import Post, CustomUser,Category ,Tag, BlogComment
from django.utils import timezone
from django.http import HttpResponseBadRequest
from django.contrib import messages
from .forms import ProfileForm

def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')
    if request.user.is_authenticated and request.GET.get('login_success'):
        messages.success(request, "Login successful!")
    return render(request, 'blog/post_list.html', {'posts': posts})
    author_username = request.GET.get('author')  

def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    return render(request, 'blog/post_detail.html', {'post': post})

@login_required
def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            form.save_m2m()
            return redirect('post_detail', slug=post.slug)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})

@login_required
def post_edit(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if request.user == post.author:
        if request.method == "POST":
            form = PostForm(request.POST,request.FILES,instance=post)
            if form.is_valid():
                post = form.save(commit=False)
                post.author = request.user
                post.published_date = timezone.now()
                post.save()
                form.save_m2m()
                return redirect('post_detail', slug=post.slug)
        else:
            form = PostForm(instance=post)
        return render(request, 'blog/post_edit.html', {'form': form, 'post': post})
    else:
        return redirect('post_list')

def handleSignUp(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        fname = request.POST['fname']
        lname = request.POST['lname']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        if pass1 != pass2:
            messages.error(request, "Passwords do not match, Signup again")
            return render(request, 'blog/signup.html')

                # Check if the email already exists in the database
        existing_user = CustomUser.objects.filter(email=email).exists()
        if existing_user:
            messages.error(request, "An account with this email already exists. Please login instead.")
            return redirect('login')

        existing_username = CustomUser.objects.filter(username=username).exists()
        if existing_username:
            messages.error(request, "Username already exists. Please choose a different username.")
            return render(request, 'blog/signup.html')

        myuser = CustomUser.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.save()
        messages.success(request, "Signup successful! Please login now")
        return redirect('login')
    else:
        return render(request, 'blog/signup.html')  
def handleLogin(request):
    if request.method == "POST":
        username = request.POST['loginusername']
        password = request.POST['loginpass']
        user = authenticate(username=username, password=password)
        print(user)
        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('post_list')
        else:
            messages.error(request, "Invalid credentials. Please try again.")
            return render(request, 'blog/login.html')
    else:
        return render(request, 'blog/login.html')

def handleLogout(request):
    logout(request)
    messages.success(request, "Logout successfully")
    return redirect('post_list')

@login_required
def profile(request):
    user = request.user
    return render(request, 'blog/profile.html', {'user': user})

@login_required
def edit_profile(request):
    user = request.user
    print(user.profile_image,'user name')
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('post_list')
    else:
        form = ProfileForm(instance=user)
        print(user)
    return render(request, 'blog/profile.html', {'form': form, 'user': user})

def category_posts(request, category):
    category = get_object_or_404(Category, slug=category)
    posts = category.posts.all() 
    return render(request, 'blog/post_list.html', {'category': category, 'posts': posts})

def tags_posts(request, tag):
    tag = get_object_or_404(Tag, slug=tag)
    posts = tag.posts.all()
    return render(request, 'blog/post_list.html', {'tag': tag, 'posts': posts})

def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    if request.method == 'POST':
        comment_text = request.POST.get('comment')
        parent_id = request.POST.get('parent_id')
        
        if comment_text:
            if request.user.is_authenticated:
                if parent_id:  # If it's a reply
                    parent_comment = BlogComment.objects.get(pk=parent_id)
                    comment = BlogComment.objects.create(
                        comment=comment_text,
                        user=request.user,
                        post=post,
                        parent=parent_comment,
                        timestamp=timezone.now()
                    )
                else:  # If it's a parent comment
                    comment = BlogComment.objects.create(
                        comment=comment_text,
                        user=request.user,
                        post=post,
                        timestamp=timezone.now()
                    )
                    
                return redirect('post_detail', slug=post.slug)
            else:
                return render(request, 'blog/login.html')

def author_posts(request, pk):
    author = get_object_or_404(CustomUser, pk=pk)
    posts = Post.objects.filter(author=author, published_date__lte=timezone.now()).order_by('-published_date')
    return render(request, 'blog/post_list.html', {'author': author, 'posts': posts})

