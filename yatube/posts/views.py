from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import (get_object_or_404,
                              redirect, render)
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post
from .utils import paginator_func

User = get_user_model()


@cache_page(settings.CACHE_PERIOD)
def index(request):
    post_list = Post.objects.all()
    page_obj = paginator_func(request, post_list)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    context = {
        'page_obj': page_obj,
        'form': form,
        'post_list': post_list,
        'cache_period': settings.CACHE_PERIOD,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    page_obj = paginator_func(request, post_list)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    records_count = post_list.count()
    page_obj = paginator_func(request, post_list)

    following = False
    if request.user.username:
        if request.user.username != username:
            following = Follow.objects.filter(
                author=author, user=request.user).exists

    context = {
        'page_obj': page_obj,
        'author': author,
        'records_count': records_count,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post_author_count = Post.objects.filter(author=post.author).count()
    comments = Comment.objects.filter(post=post_id)
    form = CommentForm(
        request.POST or None
    )
    context = {
        'post': post,
        'post_author_count': post_author_count,
        'comments': comments,
        'form': form,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    if request.method == 'POST':
        if form.is_valid():
            form = form.save(commit=False)
            form.author = request.user
            form.save()
            return redirect('posts:profile', username=request.user.username)

    return render(request, 'posts/create_post.html', {'form': form, })


@login_required
def post_edit(request, post_id):
    post_obj = get_object_or_404(Post, id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post_obj
    )
    is_edit = True

    if request.user.id != post_obj.author.pk:
        return redirect('posts:posts', post_id=post_id)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id)

    return render(
        request, 'posts/create_post.html',
        {'form': form, 'is_edit': is_edit, 'post_obj': post_obj}
    )


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    follow_list = Follow.objects.filter(user=request.user)
    user_list = User.objects.filter(following__in=follow_list)
    post_list = Post.objects.filter(author__in=user_list)

    page_obj = paginator_func(request, post_list)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    if request.user.username == username:
        return redirect('posts:index')

    author = get_object_or_404(User, username=username)
    if Follow.objects.filter(author=author, user=request.user).exists():
        return redirect('posts:index')

    Follow.objects.create(
        user=request.user,
        author=author,
    )
    following = True

    post_list = author.posts.all()
    records_count = post_list.count()
    page_obj = paginator_func(request, post_list)
    context = {
        'following': following,
        'author': author,
        'records_count': records_count,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(author=author, user=request.user).delete()

    post_list = author.posts.all()
    records_count = post_list.count()
    page_obj = paginator_func(request, post_list)
    context = {
        'author': author,
        'records_count': records_count,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)
