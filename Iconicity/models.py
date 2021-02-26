from django.db import models
import uuid
from django.contrib.auth.models import User
from django.utils import timezone
# Create your models here.

"""Reference (move to other locations later)
model: https://docs.djangoproject.com/en/3.1/topics/db/examples/many_to_one/
generate uuid: https://www.geeksforgeeks.org/generating-random-ids-using-uuid-python/
user: https://docs.djangoproject.com/en/3.1/ref/contrib/auth/
"""
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
    follow = models.JSONField(default=dict)

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
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    # categories field
    categories = models.JSONField(default=dict)

    # count field
    count = models.IntegerField(default=0)

    size = models.IntegerField(default=0)


    # return ~ 5 comments per post
    # should be sorted newest(first) to oldest(last)
    # pay attention here:
    # comments should be a list stores several comments objects,
    # but there's no arrayfield support sqlite3, so use json encode the comment
    # object before store the value.
    comments = models.JSONField(default=dict)

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

    # https://stackoverflow.com/questions/15874233/output-django-queryset-as-json
    def as_dict(self):
        return {
            "post_id":post_id,
            "title":title,
            "type":type,
            "source":source,
            "origin":origin,
            "description":description,
            "contentType":contentType,
            "content":content,
            "author":author,
            "categories":categories,
            #"count":count,
            "comments":comments,
            "published":published,
            "visibility":visibility,
            "unlisted":unlisted }


class FriendRequest(models.Model):
    type = models.CharField(max_length=10, default="Follow")
    summary = models.TextField(default="")
    actor = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="actor")
    object_author = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="object_author")

class Comment(models.Model):
    type = models.CharField(max_length=10, default="comment")
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
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
    # a list of Post. 
    items = models.JSONField(default=dict)


