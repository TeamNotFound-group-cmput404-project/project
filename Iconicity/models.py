from django.db import models
import uuid
from django.contrib.auth.models import User

# Create your models here.

"""Reference (move to other locations later)
model: https://docs.djangoproject.com/en/3.1/topics/db/examples/many_to_one/
generate uuid: https://www.geeksforgeeks.org/generating-random-ids-using-uuid-python/
user: https://docs.djangoproject.com/en/3.1/ref/contrib/auth/
"""
class userProfile(models.Model):
    # max length for the user display name
    max_name_length = 30 

    # user type
    user_type = models.CharField(default="author")

    # user id field
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)

    # user name field
    display_name = models.CharField(max_length=max_name_length, default="")

    # user github link
    github = models.URLField(default="")

    # host field
    host = models.URLField(default="")

    # user url
    url = models.URLField(default="")

    def get_id(self):
        return user_id   

class Post(model.Model):
    # reference:
    # https://docs.djangoproject.com/en/3.1/ref/models/fields/

    # post id, it should be a primary key
    post_id = models.UUIDField(primary_key=True, 
                               default=uuid.uuid4, 
                               editable=False)
    # title field
    title = models.CharField(max_length=100, default="")

    # type field, default is post
    type = models.CharField(default="post")

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
                                   choices=(('text/markdown', 'text/markdown'),
                                            ('text/plain', 'text/plain'),
                                            ('application/base64', 'application/base64'),
                                            ('image/png;base64', 'image/png;base64'),
                                            ('image/jpeg;base64', 'image/jpeg;base64')),
                                   default="")

    # content itself
    content = models.TextField(default="")

    # author field, make a foreign key to the userProfile class
    author = models.ForeignKey(userProfile, on_delete=models.CASCADE)

    # categories field
    categories = models.JSONField(default=[])

    # count field
    count = models.IntegerField(default=0)

    size = models.IntegerField(default=0)

    # the first page of comments
    comments = models.URLField(default="")

    # return ~ 5 comments per post
    # should be sorted newest(first) to oldest(last)
    # pay attention here:
    # comments should be a list stores several comments objects,
    # but there's no arrayfield support sqlite3, so use json encode the comment
    # object before store the value.
    comments = models.JSONField(default=[])

    # ISO 8601 TIMESTAMP
    # publish time
    published = models.DateTimeField(default=timezone.now)

    # visibility ["PUBLIC","FRIENDS"]
    visibility = models.CharField(max_length=10, 
                                  choices=("PUBLIC", "FRIENDS"),
                                  default="PUBLIC")

    # unlisted means it is public if you know the post name -- use this for 
    # images, it's so images don't show up in timelines
    unlisted = models.BooleanField(default=False)

