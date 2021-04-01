from django.db import models
import uuid
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from django.forms.models import model_to_dict
from django.db.models import Q
# Create your models here.
# Author, Followers, FriendRequest, Post, Comments, Likes, Liked, Inbox,
"""Reference (move to other locations later)
model: https://docs.djangoproject.com/en/3.1/topics/db/examples/many_to_one/
generate uuid: https://www.geeksforgeeks.org/generating-random-ids-using-uuid-python/
user: https://docs.djangoproject.com/en/3.1/ref/contrib/auth/
friend requests: https://www.youtube.com/watch?v=7-VNMGmEN54&list=PLgjw1dR712joFJvX_WKIuglbR1SNCeno1&index=10
"""

# By: Shway
class UserProfileManager(models.Manager):
    def get_all_profiles(self, exception):
        # curUser is of type User
        return UserProfile.objects.all().exclude(user = exception)

class UserProfile(models.Model):
    # max length for the user display name
    max_name_length = 30

    # user type
    type = models.CharField(max_length=10, default="author")

    # user id field
    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False)

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # user name field
    displayName = models.CharField(max_length=max_name_length, default="")

    # user github link
    github = models.URLField(default="")

    # host field
    host = models.URLField(default="")

    # user url
    url = models.URLField(default="")

    # I'm following / friend
    #follow = models.ManyToManyField(User, related_name='following', blank=True)
    follow = models.JSONField(default=dict, max_length=500)

    objects = UserProfileManager()

    # By: Shway
    def add_follow(self, item):
        # here the item should be a json string
        if self.follow == {}:
            self.follow['type'] = 'followers'
            self.follow['items'] = []
        self.follow['items'].append(item)

    def remove_follow_by_id(self, id):
        # here the item should be a json string
        for item in self.follow['items']:
            if (item['id'] == id or item['url'] == id or
                item['id'].split('/')[-1] == id or
                item['url'].split('/')[-1] == id):
                self.follow['items'].remove(item)

    def get_followers(self):
        # need to parse each item to use
        if self.follow == {}:
            self.follow['type'] = 'followers'
            self.follow['items'] = []
        return self.follow['items']

    def get_number_of_followers(self):
        if self.follow == {}:
            self.follow['type'] = 'followers'
            self.follow['items'] = []
        return len(self.follow['items'])

    def __str__(self):
        return str(self.user)


class Post(models.Model):
    # reference:
    # https://docs.djangoproject.com/en/3.1/ref/models/fields/

    # post id, it should be a primary key
    post_id = models.UUIDField(primary_key=True,
                               default=uuid.uuid4,
                               editable=False)

    # title field
    title = models.CharField(max_length=100, default="")

    # type field, default is post
    type = models.CharField(max_length=10, default="post")

    # id field
    id = models.URLField(default="")

    # source field, default is ""
    # where did you get this post from?
    source = models.URLField(default="")

    # origin field
    # where is it actually from
    origin = models.URLField(default="")

    # description
    # a brief description of the post
    description = models.CharField(max_length=250, default="")

    # contentType field, support different kinds of type choices
    contentType = models.CharField(max_length=40,
                                   choices=[('text/plain', 'text/plain'),
                                            ('text/markdown', 'text/markdown'),
                                            ('application/base64', 'application/base64'),
                                            ('image/png;base64', 'image/png;base64'),
                                            ('image/jpeg;base64', 'image/jpeg;base64')],
                                   default="")

    # content itself
    content = models.TextField(default="")

    # author field, make a foreign key to the userProfile class
    author = models.ForeignKey(User, on_delete=models.CASCADE, default=User)

    # categories field
    categories = models.JSONField(default=dict)

    # count field : total number of comments for this post
    count = models.IntegerField(default=0)

    size = models.IntegerField(default=0)

    like = models.ManyToManyField(User, related_name="blog_posts")

    external_likes = models.JSONField(default=dict,max_length=5000)

    # return ~ 5 comments per post
    # should be sorted newest(first) to oldest(last)
    # pay attention here:
    # comments should be a list stores several comments objects,
    # but there's no arrayfield support sqlite3, so use json encode the comment
    # object before store the value.
    # comments = models.JSONField(default=dict)

    # ISO 8601 TIMESTAMP
    # publish time
    published = models.DateTimeField(default=timezone.now)

    # visibility ["PUBLIC","FRIENDS"]
    visibility = models.CharField(max_length=10,
                                  choices=[("PUBLIC", "PUBLIC"),("FRIENDS","FRIENDS")],
                                  default="PUBLIC")

    # unlisted means it is public if you know the post name -- use this for
    # images, it's so images don't show up in timelines
    unlisted = models.BooleanField(default=False)


    image = models.ImageField(null=True, blank=True, upload_to="images/")

    host = models.URLField(default="")
    def count_like(self):
        if self.external_likes != {}:
            return self.like.count() + len(self.external_likes['urls'])
        return self.like.count()

    def add_external_like(self, url):
        if self.external_likes == {}:
            self.external_likes['urls'] = []
        if url in self.external_likes['urls']:
            return
        else:
            self.external_likes['urls'].append(url)

    def get_absolute_url(self):
        return reverse("main_page",kwargs ={'pk':self.pk})

    def __str__(self):
        return '%s' % (self.title)

class FriendRequest(models.Model):
    # Type is set to follow
    type = models.CharField(max_length=10, default="follow")

    # Summary of following info
    summary = models.TextField(default="")

    # Sender of this friend request:
    actor = models.JSONField(default=dict, max_length=500)

    # Reciever of this friend request:
    object = models.JSONField(default=dict, max_length=500)


class Comment(models.Model):
    #post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    type = models.CharField(max_length=10, default="comment")
    #author = models.ForeignKey(User, on_delete=models.CASCADE, default=User)
    author = models.JSONField(default=dict,max_length=500) # author is the creator of this comment, not post author
    post = models.URLField(default="")
    # ISO 8601 TIMESTAMP
    # publish time
    published = models.DateTimeField(default=timezone.now)
    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False)
    comment = models.TextField(default="")
    # contentType field, support different kinds of type choices
    contentType = models.CharField(max_length=40,
                                   choices=(('text/markdown', 'text/markdown'),
                                            ('text/plain', 'text/plain'),
                                            ('application/base64', 'application/base64'),
                                            ('image/png;base64', 'image/png;base64'),
                                            ('image/jpeg;base64', 'image/jpeg;base64')),
                                   default="")

    def __str__(self):
        return '%s' % (self.author)

    def get_absolute_url(self):
        return reverse("main_page")

class Like(models.Model):
    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False)
    type = models.CharField(max_length=10, default="like")
    context = models.URLField(default="")
    summary = models.TextField(default="")

    # foreign key to the author
    author = models.JSONField(default=dict,max_length=500)
    object = models.JSONField(default=dict,max_length=500)

# by: Shway Wang:
class InboxManager(models.Manager):
    def add_new_item_to_author_inbox(self, item, url):
        if len(Inbox.objects.filter(author = url)) == 0:
            Inbox.objects.filter(author = url)[0].author = url
        print("model here: ", Inbox.objects.filter(author = url)[0].author)
        print("item: ", item)
        Inbox.objects.filter(author = url)[0].items.append(item)
        print("model here: ", Inbox.objects.filter(author = url)[0].items)


class Inbox(models.Model):
    type = models.CharField(max_length=10, default="inbox")
    author = models.URLField(default="")
    # stores a list of mixed items to display,
    # better consider converting your Post list to json
    # if you wish to get the item list, just parse it then you will get
    items = models.JSONField(default=list,max_length=10000)
    

class ExternalServer(models.Model):
    host = models.URLField(default="",primary_key=True,)

    def get_host(self):
        return self.host

