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
    def get_all_available_profiles(self, sender):
        # sender is of type User
        profiles = UserProfile.objects.all().exclude(user = sender) # all other profiles except for me
        my_profile = UserProfile.objects.get(user = sender) # my profile
        # below are requests that are related to the current user:
        queryset = FriendRequest.objects.filter(Q(actor=my_profile) | Q(object_author=my_profile))
        #print(queryset)
        accepted = set()
        for frdReq in queryset:
            if frdReq.status == 'accepted':
                accepted.add(frdReq.receiver)
                accepted.add(frdReq.sender)
        #print(accepted)
        available = [p for p in profiles if profiles not in accepted]
        #print(available)
        return available

    def get_all_profiles(self, exception):
        # curUser is of type User
        return UserProfile.objects.all().exclude(user = exception)

class UserProfile(models.Model):
    # max length for the user display name
    max_name_length = 30

    # user type
    user_type = models.CharField(max_length=10, default="author")

    # user id field
    uid = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False)

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # user name field
    display_name = models.CharField(max_length=max_name_length, default="")

    # user github link
    github = models.URLField(default="")

    # host field
    host = models.URLField(default="")

    # user url
    url = models.URLField(default="")

    # I'm following / friend
    follow = models.ManyToManyField(User, related_name='following', blank=True)

    # Who i'm following on other servers.
    # Should be a dict of urls
    externalFollows = models.JSONField(default=dict)

    objects = UserProfileManager()
    
    def get_external_follows(self):
        # return a list of urls of the external followed authors.
        if self.externalFollows == {} or self.externalFollows == []:
            return []
        else:
            return self.externalFollows['urls']

    # By: Shway
    def get_followers(self):
        return self.follow.all()

    def get_number_of_followers(self):
        return self.follow.all().count()

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
                                   choices=[('text/markdown', 'text/markdown'),
                                            ('text/plain', 'text/plain'),
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

    # count field
    count = models.IntegerField(default=0)

    size = models.IntegerField(default=0)

    like = models.ManyToManyField(User, related_name="blog_posts")

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
        return self.like.count()

    def get_absolute_url(self):
        return reverse("main_page",kwargs ={'pk':self.pk})

    def __str__(self):
        return '%s' % (self.title)

# By Shway:
STATUS_CHOICES = (
    ('sent', 'sent'),
    ('accepted', 'accepted'),
)

class FriendRequestManager(models.Manager):
    def friendRequests_received(self, receiver):
        return FriendRequest.objects.filter(object_author=receiver, status='sent')

    #FriendRequest.objects.friendRequests_received(curUserProfile)

class FriendRequest(models.Model):
    # Type is set to follow
    type = models.CharField(max_length=10, default="Follow")

    # Summary of following info
    summary = models.TextField(default="")

    # Sender of this friend request:
    actor = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="actor")

    # Reciever of this friend request:
    object_author = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="object_author")

    # By: Shway
    # For the receiver to choose to accept or reject:
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    objects = FriendRequestManager()

    def __str__(self):
        return f"{self.actor}-->{self.object_author}: {self.summary}, status: {self.status}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    type = models.CharField(max_length=10, default="comment")
    author = models.ForeignKey(User, on_delete=models.CASCADE, default=User)
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

class LikeSingle(models.Model):
    """
    looks like:
    {
        id: (primary key)
        type:liked
        context:...
        summary:...
        author: object
        post_object:url
    }
    different from the spec
    If you need to save a list of liked objs in other class
    just query some liked objects, encode into json format
    then the model can use this liked list. Same thing for comments.
    """
    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False)
    type = models.CharField(max_length=10, default="Like")
    context = models.URLField(default="")
    summary = models.TextField(default="")

    # foreign key to the author
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    post_object = models.URLField(default="")

class Inbox(models.Model):
    type = models.CharField(max_length=10, default="inbox")
    author = models.URLField(default="")
    # stores a list of Post items to display,
    # better consider converting your Post list to json
    # if you wish to get the item list, just parse it then you will get
    items = models.JSONField(default=dict)

class ExternalServer(models.Model):
    host = models.URLField(default="",primary_key=True,)

    def get_host(self):
        return self.host