from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
# Register your models here.
from .models import User, Post, Like, Follower

# create like inline class to allow for addition of likes for posts
class LikeInline(admin.TabularInline):
    model = Like

class FollowerInline(admin.TabularInline):
    model = Follower
    fk_name = "following"

class FollowingInline(admin.TabularInline):
    model = Follower
    fk_name = "follower"


class PostAdmin(admin.ModelAdmin):
    model = Post
    list_display = ("title", "text", "user", "time", "get_likes")
    # get the likes associated post object
    def get_likes(self, post):
        # get list of likes associated with the post, then count
        likes = post.like.values()
        print(likes)
        return len(likes)
    get_likes.short_description = "Likes"
    inlines = [LikeInline]

class LikeAdmin(admin.ModelAdmin):
    model = Like
    list_display = ("user", "get_post")
    def get_post(self, like):
        # get list of likes associated with the post, then count
        post = like.post
        return post.title
    get_post.short_description = "Post"

class FollowerAdmin(admin.ModelAdmin):
    model = Follower
    list_display = ("following", "follower")

class PersonAdmin(admin.ModelAdmin):
    list_display = ("username", "get_followers", "get_following", "get_posts")

    def get_posts(self, person):
        posts = person.post.values_list()
        return len(posts)
    get_posts.short_description = "Posts"

    def get_followers(self, person):
        followers = person.following.values()
        return len(followers)
    get_followers.short_description = "Followers"

    def get_following(self, person):
        following = person.follower.values()
        return len(following)
    get_following.short_description = "Following"
    
    inlines = [FollowerInline, FollowingInline]

admin.site.register(Post, PostAdmin)
admin.site.register(Like, LikeAdmin)
admin.site.register(Follower, FollowerAdmin)
admin.site.register(User, PersonAdmin)