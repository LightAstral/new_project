import random
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from django.contrib.auth import login
from .forms import UserRegistrationForm
from .models import Post, Category, Comment, UserProfile
from django.db.models import Q
from .forms import PostForm, CommentForm, UserProfileForm, AvatarUploadForm, UserForm
from django import forms


# Create your views here.
def dummy():
    return str(random.randint(1, 10))


def get_categories():
    all = Category.objects.all()
    count = all.count()
    half = count // 2
    if count % 2 != 0:
        half += 1
    return {"cat1": all[:half], "cat2": all[half:]}


# def get_categories():
#     all = Category.objects.all()
#     count = all.count()
#     half = count // 2 + 1
#     return {"cat1": all[:half], "cat2": all[half:]}


def index(request):
    # posts = Post.objects.all()
    # posts = Post.objects.filter(title__contains='python')
    # posts = Post.objects.filter(published_date__year=2023)
    # posts = Post.objects.filter(category__name___iexact='python')
    posts = Post.objects.order_by('-published_date')
    paginator = Paginator(posts, 2)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    # categories = Category.objects.all()

    context = {'posts': page_obj}
    context.update(get_categories())

    return render(request, 'blog/index.html', context=context)


def post(request, id=None):
    post = get_object_or_404(Post, pk=id)
    comments = Comment.objects.filter(post=post)
    comment_form = CommentForm()
    context = {"post": post, "comments": comments, 'comment_form': comment_form}
    context.update(get_categories())

    return render(request, 'blog/post.html', context=context)


def category(request, name=None):
    c = get_object_or_404(Category, name=name)
    posts = Post.objects.filter(category=c).order_by('-published_date')
    context = {"posts": posts}
    context.update(get_categories())

    return render(request, 'blog/index.html', context=context)


def about(request):
    return render(request, 'blog/about.html')


def contact(request):
    return render(request, 'blog/contact.html')


def services(request):
    return render(request, 'blog/services.html')


def search(request):
    query = request.GET.get('query')
    posts = Post.objects.filter(Q(content__icontains=query) | Q(title__icontains=query))
    context = {"posts": posts}
    context.update(get_categories())

    return render(request, 'blog/index.html', context=context)


@login_required
def create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.published_date = now()
            post.user = request.user
            post.save()
            form.save_m2m()
            return redirect('index')
    else:
        form = PostForm()
    return render(request, 'blog/create.html', {'form': form})


def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user if request.user.is_authenticated else None
            comment.save()
            return render(request, "blog/post.html", context={'post': post, 'comments': post.comments.all()})

    comments = Comment.objects.filter(post=post)
    comment_form = CommentForm()
    context = {"post": post, "comments": comments, 'comment_form': comment_form}
    context.update(get_categories())
    return render(request, "blog/post.html", context=context)


@login_required
def user_profile(request):
    user = request.user
    if request.method == 'POST':
        avatar_form = AvatarUploadForm(request.POST, request.FILES, instance=user.userprofile)
        if 'delete_avatar' in request.POST:
            user.userprofile.avatar.delete()
            return redirect('user_profile')
        if avatar_form.is_valid():
            avatar_form.save()
            return redirect('user_profile')
    else:
        avatar_form = AvatarUploadForm(instance=user.userprofile)
    return render(request, 'blog/user_profile.html', {'user': user, 'avatar_form': avatar_form})


@login_required
def edit_profile(request):
    user = request.user
    user_profile, created = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, instance=user_profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('user_profile')
    else:
        user_form = UserForm(instance=user)
        profile_form = UserProfileForm(instance=user_profile)

    return render(request, 'blog/edit_profile.html', {'user_form': user_form, 'profile_form': profile_form})


@login_required
def private_message(request, username):
    if request.method == 'POST':
        pass
    else:
        recipient = User.objects.get(username=username)
        context = {
            'recipient': recipient,
        }
        return render(request, 'blog/private_message.html', context)


@login_required
def delete_avatar(request):
    user = request.user
    if user.userprofile.avatar:
        user.userprofile.avatar.delete()
    return redirect('user_profile')


@login_required
def my_posts(request):
    user = request.user
    user_posts = Post.objects.filter(user=user)
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = user
            post.save()
            return redirect('my_post')
    else:
        form = PostForm()
    return render(request, 'blog/my_post.html', {'user_posts': user_posts, 'form': form})


def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if request.user == post.user:
        post.delete()
        messages.success(request, 'Пост успешно удален.')
    else:
        messages.error(request, 'Вы не можете удалить этот пост, так как вы не являетесь его автором.')

    return redirect('my_posts')


def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserRegistrationForm()
    return render(request, 'blog/registration_user.html', {'user_form': form})
