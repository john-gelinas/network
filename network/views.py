from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.core.paginator import Paginator
from .models import Post, Like, Follower
from django import forms
from datetime import datetime
from django.http import JsonResponse
import json

# from requests import request
from django.contrib.auth.decorators import login_required

from .models import User, Post, Like, Follower


class PostForm(forms.Form):
    title = forms.CharField(label="Title", widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    text = forms.CharField(label="Post", widget=forms.Textarea(
        attrs={'class': 'form-control'}))


def index(request):
    return ("hi")
    # if request.user.is_authenticated:
    #     if request.method == "POST":
    #         # throw error if post
    #         return error(request, "Invalid Submission")
    #     else:
    #         posts = Post.objects.all().order_by('-time')
    #         paginator = Paginator(posts, 10)  # Show 10 contacts per page.
    #         page_number = request.GET.get(
    #             'page') if request.GET.get('page') else 1
    #         page_obj = paginator.get_page(page_number)
    #         return render(request, "network/index.html", {'page_obj': page_obj})
    # else:
    #     return redirect(reverse("login"))


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


@login_required
def newpost(request):
    if request.method == "POST":
        # create post
        postform = PostForm(request.POST)
        if postform.is_valid():
            text = postform.cleaned_data['text']
            title = postform.cleaned_data['title']
            user = request.user
            edited = False
            time = datetime.now()
        newpost = Post(text=text, title=title, user=user,
                       time=time, edited=edited)
        newpost.save()
        return(redirect("profile", profile_id=user.id))
    else:
        return render(request, "network/newpost.html", {
            "form": PostForm
        })


def profile(request, profile_id):
    if request.user.is_authenticated:
        user = request.user
        if request.method == "POST":
            # throw error if post
            return error(request, "Invalid Submission")
        else:
            posts = Post.objects.filter(user=profile_id).order_by('-time')
            paginator = Paginator(posts, 10)  # Show 10 contacts per page.
            page_number = request.GET.get(
                'page') if request.GET.get('page') else 1
            page_obj = paginator.get_page(page_number)
            profile = User.objects.get(id=profile_id)
            following = len(Follower.objects.filter(follower=profile))
            followers = len(Follower.objects.filter(following=profile))
            user_following = len(Follower.objects.filter(following=user))
            # check if profile is user's
            if user == profile:
                button = False
            else:
                button = True
            return render(request, "network/index.html", {
                'page_obj': page_obj,
                'followers': followers,
                'following': following,
                'profile': profile,
                'button': button,
                'profile_id': profile_id,
                'user_following': user_following
            })
    else:
        return redirect(reverse("login"))


def following(request):
    if request.user.is_authenticated:
        user = request.user
        if request.method == "POST":
            # throw error if post
            return error(request, "Invalid Submission")
        else:
            # get profiles user is following from list of following objects
            following_id_list = Follower.objects.filter(
                follower=user).values('following_id')
            following_user_list = User.objects.filter(
                id__in=following_id_list).values('id')
            # get posts of profiles user is following
            posts = Post.objects.filter(
                user__in=following_user_list).order_by('-time')
            paginator = Paginator(posts, 10)  # Show 10 contacts per page.
            page_number = request.GET.get(
                'page') if request.GET.get('page') else 1
            page_obj = paginator.get_page(page_number)
            return render(request, "network/index.html", {'page_obj': page_obj})
    else:
        return redirect(reverse("login"))


@login_required
def followapi(request, follow_id):
    user = request.user
    #  check for profile
    try:
        profile = User.objects.get(pk=follow_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "Profile not found."}, status=404)

    # Return follow status
    if request.method == "GET":
        try:
            follow = Follower.objects.get(following=follow_id, follower=user)
            follow = True
        except Follower.DoesNotExist:
            follow = False
        profile = User.objects.get(id=follow_id)
        following = len(Follower.objects.filter(follower=profile))
        followers = len(Follower.objects.filter(following=profile))
        return JsonResponse({
            "follow": follow,
            "followers": followers,
            "following": following
        }, status=200)

    # Update whether follow need to be true or false
    elif request.method == "PUT":
        data = json.loads(request.body)
        if data.get("following") == False:
            # check if follow already exists despite client reporting that new follower should be added
            # status 429 - too many requests (rapidly clicking follow button)
            if Follower.objects.filter(following=follow_id, follower=user.id).count() != 0:
                return HttpResponse(status=429)
            # user cannot follow themselves
            if follow_id == user.id:
                return HttpResponse(status=400)
            # add new follow
            follower = user
            following = User.objects.get(pk=follow_id)
            follow = Follower(follower=follower, following=following)
            follow.save()
        else:
            # delete follow (unfollow profile)
            Follower.objects.filter(
                following=follow_id, follower=user).delete()
        return HttpResponse(status=204)

    # Email must be via GET or PUT
    else:
        return JsonResponse({
            "error": "GET or PUT request required."
        }, status=400)


@login_required
def editapi(request):
    user = request.user
    data = json.loads(request.body)
    #  check for post
    try:
        post_id = data.get("post_id")
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return error(request, "404: Post Not Found", 404)
    if post.user != user:
        return error(request, "incorrect account to edit this post", 401)
    # if put request, delete post
    if request.method == "PUT":
        post.delete()
        print(post_id)
        return JsonResponse({"deleted": post_id}, status=200)
    # if post request, edit post text and update time
    if request.method == "POST":
        post_text = data.get("posttext")
        post.time = datetime.now()
        post.text = post_text
        post.edited = True
        post.save()
        return JsonResponse({
            "post_id": post_id,
            "post_text": post_text
        }, status=200)
    else:
        return redirect(reverse("index"))


@login_required
def likeapi(request, post_id):
    user = request.user
    #  check for post
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return error(request, "404: Post not found.", 404)

    # Return like status
    if request.method == "GET":
        try:
            like = Like.objects.get(post=post_id, user=user)
            liked = True
        except Like.DoesNotExist:
            liked = False
        total_likes = Like.objects.filter(post=post_id).count()
        return JsonResponse({"liked": liked, "total_likes": total_likes}, status=200)

    # Update whether post needs to be liked or unliked
    elif request.method == "PUT":
        data = json.loads(request.body)
        if data.get("liked") == False:
            # check if like already exists despite client reporting that new like should be added
            # status 429 - too many requests (rapidly clicking like button)
            if Like.objects.filter(post=post_id, user=user).count() != 0:
                return HttpResponse(status=429)
            # add new like
            post = Post.objects.get(pk=post_id)
            like = Like(user=user, post=post)
            like.save()
        else:
            # delete like
            Like.objects.filter(post=post_id, user=user).delete()
        return HttpResponse(status=204)

    # Email must be via GET or PUT
    else:
        return error(request, "GET or PUT request required.", 400)


def error(request, errortext, status):
    return render(request, "network/index.html", {
        "errortext": errortext
    },
        status
    )
