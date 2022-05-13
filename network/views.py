from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.core.paginator import Paginator
from .models import Post, Like, Follower
from django import forms
from datetime import datetime

# from requests import request
from django.contrib.auth.decorators import login_required

from .models import User

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
            posts = Post.objects.all()

            paginator = Paginator(posts, 10) # Show 10 contacts per page.
            page_number = request.GET.get('page')
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

        return redirect(reverse("index"))


@login_required
def profile(request):
    if request.method == "POST":
        pass
    else:
        pass



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

def error(request, errortext):
    return render(request, "network/index.html", {
        "errortext": errortext
    })