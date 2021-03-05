from .models import *
from rest_framework import serializers
from django.contrib.auth.models import User
import datetime
from urllib import request
import json

# https://www.django-rest-framework.org
class PostSerializer(serializers.ModelSerializer):

    post_id = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()
    count = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    source = serializers.SerializerMethodField()
    origin = serializers.SerializerMethodField()
    contentType = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('post_id', 'title', 'type', 'source', 'origin', 'description', 'contentType',
        'author', 'content', 'visibility', 'categories', 'unlisted','image','like',
        'count', 'size', 'published', 'author', 'host')


    def get_post_id(self, obj):
        return obj.post_id

    def get_author(self, obj):
        return GETProfileSerializer(UserProfile.objects.filter(user=obj.author).first()).data

    def get_count(self, obj):
        return obj.count

    def get_size(self, obj):
        return obj.size

    def get_source(self, obj):
        return str(obj.host) + 'posts/' + str(obj.post_id)

    def get_origin(self, obj):
        return str(obj.host) + 'posts/' + str(obj.post_id)

    def get_contentType(self, obj):
        return obj.contentType

    def get_description(self,obj):
        if len(obj.content)>50:
            return obj.content[:50]
        else:
            return obj.content

class GETProfileSerializer(serializers.ModelSerializer):
    uid = serializers.SerializerMethodField("get_uid")
    display_name = serializers.SerializerMethodField("get_name")
    host = serializers.SerializerMethodField()
    github = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    class Meta:
        model = UserProfile
        fields = ('user_type', 'uid','display_name','host','github','url')

    def get_uid(self, obj):
        if type(obj) == dict:
            return str(obj['host']) + '/author/' + str(obj['uid'])
        return str(obj.host) + '/author/' + str(obj.uid)

    def get_name(self, obj):
        return obj.display_name

    def get_host(self, obj):
        return obj.host

    def get_github(self, obj):
        return obj.github

    def get_url(self,obj):
        if type(obj) == dict:
            return str(obj['host']) + '/author/' + str(obj['uid'])
        return str(obj.host) + '/author/' + str(obj.uid)

class CommentSerializer(serializers.ModelSerializer):
    comment = serializers.SerializerMethodField() # content
    id = serializers.SerializerMethodField('get_comment_id') #comment_id
    author = serializers.SerializerMethodField() #user_id

    class Meta:
        model = Comment
        fields = ('author','comment','contentType','published','id', 'post_id')

    def get_comment(self, obj):
        return obj.content

    def get_comment_id(self, obj):
        return obj.comment_id

    def get_author(self, obj):
        # Reference:
        # https://www.kancloud.cn/thinkphp/python-guide/39426

        with request.urlopen(obj.user_id) as f:
            data = f.read().decode('utf-8')
            data = json.loads(data)
            return data

# By: Shway Wang
'''
class FriendRequestSerializer(serializers.ModelSerializer):
    type = models.CharField(max_length=10, default="Follow")
    summary = models.TextField(default="")
    actor = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="actor")
    object_author = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="object_author")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    class Meta:
        model = FriendRequest
        fields = ('actor', 'object_author', 'status')
'''
    
