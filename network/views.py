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
    if request.user.is_authenticated:
        if request.method == "POST":
            # throw error if post
            return error(request, "Invalid Submission")
        else:
            posts = Post.objects.all().order_by('-time')
            paginator = Paginator(posts, 1) # Show 10 contacts per page.
            page_number = request.GET.get('page') if request.GET.get('page') else 1
            page_obj = paginator.get_page(page_number)
            return render(request, "network/index.html", {'page_obj': page_obj})    
    else:
        return redirect(reverse("login"))


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
            time = datetime.now()
        newpost = Post(text=text, title=title, user=user, time=time)
        newpost.save()
        return(redirect("profile"))
    else:
        return render(request, "network/newpost.html", {
            "form": PostForm
        })

def profile(request, profile):
    if request.user.is_authenticated:
        user = request.user
        if request.method == "POST":
            # throw error if post
            return error(request, "Invalid Submission")
        else:
            posts = Post.objects.filter(user=profile).order_by('-time')
            paginator = Paginator(posts, 1) # Show 10 contacts per page.
            page_number = request.GET.get('page') if request.GET.get('page') else 1
            page_obj = paginator.get_page(page_number)
            profile = User.objects.get(id=profile)
            following = len(Follower.objects.filter(follower=profile))
            followers = len(Follower.objects.filter(following=profile))
            user_following = len(Follower.objects.filter(following=user))
            # check if profile is user's
            if user == profile:
                button = None
            else:
                # check if user is following profile
                if user_following:
                    button = "Unfollow"
                else:
                    button = "Follow"
            return render(request, "network/index.html", {
                'page_obj': page_obj,
                'followers': followers,
                'following': following,
                'profile': profile,
                'button': button
                })    
    else:
        return redirect(reverse("login"))



@login_required
def following(request):
    if request.method == "POST":
        pass
    else:
        pass

@login_required
def editapi(request):
    if request.method == "POST":
        pass
    else:
        pass

@login_required
def likeapi(request, post_id):
    user = request.user
    #  check for post
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)
    
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
            like = Like(user = user, post = post)
            like.save()
        else:
            # delete like
            Like.objects.filter(post=post_id, user=user).delete()
        return HttpResponse(status=204)

    # Email must be via GET or PUT
    else:
        return JsonResponse({
            "error": "GET or PUT request required."
        }, status=400)


def error(request, errortext):
    return render(request, "network/index.html", {
        "errortext": errortext
    })