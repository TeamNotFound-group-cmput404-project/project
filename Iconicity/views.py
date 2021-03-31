from django.shortcuts import render, resolve_url, reverse, get_object_or_404,redirect
from django.http import HttpResponse, HttpResponseRedirect, QueryDict
from .models import *
from .config import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, RetrieveAPIView
from django.core import serializers as core_serializers
import json, os
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .forms import *
from django.contrib.auth.decorators import login_required
from django.views import View
from django.views.generic import ListView, DeleteView, CreateView
from django.http.request import HttpRequest
from django.core.serializers.json import DjangoJSONEncoder
from django.urls import reverse
from django.db.models import Q
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from .serializers import *
from urllib.request import urlopen
import requests
import collections
from rest_framework.renderers import JSONRenderer
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from requests.auth import HTTPBasicAuth
import base64
import uuid
#https://thecodinginterface.com/blog/django-auth-part1/


def logout_view(request):
    # in use, support log out
    # http://www.learningaboutelectronics.com/Articles/How-to-create-a-logout-button-in-Django.php
    if request.method == 'POST':
        logout(request)
        return redirect(reverse('login'))


class LoginView(View):
    def get(self, request):
        if not request.user.is_anonymous:
            return redirect(reverse('public'))

        return render(request, 'Iconicity/login.html', { 'form':  AuthenticationForm })

    def post(self,request):
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            try:
                form.clean()
            except ValidationError:
                return render(
                    request,
                    'Iconicity/login.html',
                    { 'form': form, 'invalid_creds': True }
                )

            login(request, form.get_user())

            return redirect(reverse('public'))

        return render(request, 'Iconicity/login.html', { 'form': form })

# citation:https://simpleisbetterthancomplex.com/tutorial/2017/02/18/how-to-create-user-sign-up-view.html#sign-up-with-profile-model


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            User = authenticate(username=username, password=raw_password)
            Github = form.cleaned_data.get('github')
            host = request.get_host()
            scheme = request.scheme
            createUserProfileAndInbox(scheme, username, User, Github, host)

            login(request, User)
            return redirect('public')
    else:
        form = SignUpForm()
    return render(request, 'Iconicity/signup.html', {'form': form})


@login_required
def mainPagePublic(request):
    # https://docs.djangoproject.com/en/3.1/topics/serialization/
    if request.user.is_anonymous:
        return render(request, 'Iconicity/login.html', { 'form':  AuthenticationForm })
    #string = str(request.scheme) + "://" + str(request.get_host())+"/posts/"
    new_list = [] 
    new_list += PostSerializer(list(Post.objects.all()),many=True).data


    externalPosts = getAllExternalPublicPosts()


    for post in externalPosts:
        # https://stackoverflow.com/questions/2323128/convert-string-in-base64-to-image-and-save-on-filesystem-in-python

        if post["contentType"] == "text/plain":
            # means the content part is all plain text, not image
            try:
                image_field = post['image']

            except Exception:
                # means this post has no image field, set image field to None.
                post['image'] = ""

            else:
                pass

        elif post["contentType"] =="image/png;base64":
            # means it's a image in the content
            # means this post has no image field, probably this is from external server.
            # in this case, we will save the image to local and use the absolute
            # path to set a new image field.
            
            post_id = [i for i in post['id'].split('/') if i][-1]
            file_name = post_id+".png"
            folder_path = "/media/images/"
            path = folder_path+file_name
            # first, check this image exists.
            
            if os.path.exists("Iconicity"+path):
                post['image'] = path
            else:
                print("create new file")
                # then write the dump file to an image file.
                with open("Iconicity"+path, "wb") as fh:
                    fh.write(base64.decodebytes(str.encode(post['content'])))
                post['image'] = path
        if post['author']['host'] in team10_host_url:

            post['author_display_name'] = post['author']['displayName']

    new_list += externalPosts

        
    new_list.reverse()

    # by Shway:

    curProfile = getUserProfile(request.user)
    '''
    externalFollowNames = []
    the_user_name = auth_user
    the_user_pass = auth_pass
    if host_url == team10_host_url:
        the_user_name = team10_name
        the_user_pass = team10_pass
        full_url += "s"
    '''
    '''
    for i in curProfile.get_external_follows():
        externalFollowNames += requests.get(i, auth=HTTPBasicAuth(the_user_name, the_user_pass)).json()['display_name']
    '''
    context = {
        'posts': new_list,
        'UserProfile': curProfile,
        #'externalFollowNames': externalFollowNames,
        'myself': str(request.user),
    }
    return render(request, 'Iconicity/main_page.html', context)


def createUserProfileAndInbox(scheme, Display_name, User, Github, host):
    profile = UserProfile(user=User,
                          display_name=Display_name,
                          github=Github,
                          host=host)


    profile.url = str(scheme) + "://" + str(host) + '/author/' + str(profile.uid)
    
    inbox_obj = Inbox()
    inbox_obj.author = profile.url
    inbox_obj.items = []
    profile.save()
    inbox_obj.save()


def getAllFollowAuthorPosts(currentUser):
    userProfile = UserProfile.objects.filter(user=currentUser).first()
    post_list = []
    allFollowedAuthors = list(userProfile.get_followers())

    for user in allFollowedAuthors:
        # check whether they are friends.
        # means a two-direct-follow
        otherUserProfile = UserProfile.objects.filter(user=user).first()
        if otherUserProfile:
            if currentUser in list(otherUserProfile.get_followers()):
                temp = getPosts(user, visibility="FRIENDS") # join the post_list
                post_list += temp
            else:
                # one direct
                # only public
                post_list += getPosts(user, visibility="PUBLIC")# join the post_list

    return post_list


def getUserProfile(currentUser):
    # return a UserProfile object for the current login user
    return UserProfile.objects.filter(user=currentUser).first()

def getPosts(user, visibility="PUBLIC"):
    assert visibility in ["PUBLIC","FRIENDS"],"Not valid visibility for posts, check getPosts method in views.py"
    if visibility == "PUBLIC":
        # public can only see your public posts
        return list(Post.objects.filter(author=user.id, visibility="PUBLIC"))
    elif visibility == "FRIENDS":
        # friends can see all your posts (public + friends posts)
        return list(Post.objects.filter(author=user.id))

def getPost(post):
    return Post.objects.filter(post_id=post.post_id).first()

def getComments():
    return json.loads(core_serializers.serialize("json", list(Comment.objects.filter())))

def delete_post(request):
    pk_raw = request.POST.get('pk')
    try:
        post = requests.get(pk_raw, auth=HTTPBasicAuth(auth_user, auth_pass)).json()
        post_id = post[0]["post_id"]
        if post_id:
            post = get_object_or_404(Post,pk=post_id)
            print(post_id)
            post.delete()
    except Exception as e:
        post = requests.get(pk_raw, auth=HTTPBasicAuth(auth_user, auth_pass))
        print(e)
        print('post:', post)
    return redirect("mypost")


class AddPostView(CreateView):
    model = Post
    template= "/Iconicity/post_form.html"
    # fields = "__all__"
    # Post.author = UserProfile.objects.values()['uid']
    def post(self, request):
        print("posting")
        template = "Iconicity/post_form.html"
        form = PostsCreateForm(request.POST, request.FILES,)
        print(form['image']) 
        # print(request.FILES)
        if form.is_valid():
            print("posting...")
            form = form.save(commit=False)
            form.author = request.user
            userProfile = UserProfile.objects.get(user=request.user)
            # https://iconicity-test-a.herokuapp.com/author/b168fc3-a41f-4537-adbe-9e698420574f/posts/aee8e63f-5792-439e-87f3-3239cce3df98
            form.save()
            form.origin = (str(request.scheme) + "://"
                                               + str(request.get_host())
                                               + '/author/'
                                               + str(userProfile.pk)
                                               + '/posts/'
                                               + str(form.post_id))
            form.source = form.origin
            form.save()
            print(form.image)
            return redirect('public')

        else:
            print(form.errors)
            form = PostsCreateForm(request.POST)

        context = {
            'form': form,
        }
        return render(request, template, context)

    def get(self, request):
        print("getting")
        return render(request, 'Iconicity/post_form.html', { 'form':  PostsCreateForm })


# By Shway, the friend requests related stuff(including following):
# by Shway, the follow function, to add someone to your follow list:
def follow_someone(request):
    if request.method == 'POST':
        # receive data from front-end
        followee_host = request.POST.get('followee_host')
        followee_github = request.POST.get('followee_github')
        followee_display_name = request.POST.get('followee_display_name')
        followee_uid = request.POST.get('followee_uid')
        print("uid ", followee_uid)
        print("host ", followee_host)
        print("gihtub ", followee_github)
        print("display_name ", followee_display_name)
        # get current user profile
        curProfile = UserProfile.objects.get(user = request.user)
        # save the new uid into current user's follow attribute:
        try: # local
            followee_profile = UserProfile.objects.get(uid = followee_uid)
            summary = curProfile.display_name + " wants to follow " + followee_display_name
            # create a new friend request locally
            newFrdRequest = FriendRequest.objects.create(actor=curProfile, object=followee_profile, summary = summary)
            curProfile.follow.add(followee_profile.user)
        except Exception as e: # external
            # cannot get the profile with followee_uid locally
            print("Not local")
            # First, add the uid into local database:
            if curProfile.externalFollows == {}:
                curProfile.externalFollows['urls'] = []
            curProfile.externalFollows['urls'].append(followee_uid)
            # Second, send the remote post request:
            # create a new friend request with the receiver the (external) followee_uid
            summary = curProfile.display_name + " wants to follow " + followee_display_name

            # serialized current profile
            '''
            actor = {"type":"author", "id":str(curProfile.uid), "host":str(curProfile.host),
            	"displayName":str(curProfile.display_name),
                "url":str(curProfile.url), "github": str(curProfile.github)}
            '''
            # form the freind request data stream
            '''
            object = {"type":"author", "id":followee_uid, "host":followee_host,
            	"displayName":followee_display_name,
                "url":followee_uid, "github": followee_github}
            print("this is followee_uid:  ", followee_uid)
            '''

            actor = json.dumps(GETProfileSerializer(curProfile).data)
            print("follow someone's actor serialized: ", actor)
            # API from the other server
            full_followee_url = ''
            if followee_uid.startswith('http'): full_followee_url = followee_uid
            else: full_followee_url = str(request.scheme) + "://" + followee_uid
            # request the user profile with the full followee_url:
            object_profile = json.loads(requests.get(full_followee_url, auth=HTTPBasicAuth(auth_user, auth_pass)).text)
            # construct the new friend request:
            new_frdRequest = FriendRequest(type = "Follow", summary = summary, actor = actor, 
                status = 'sent', object = json.dumps(object_profile))
            # serialize the new friend request:
            frd_request_serialized = FriendRequestSerializer(new_frdRequest).data

            '''
            frd_request_context = {"type": "Follow", "summary": summary,
            						"actor": json.dumps(actor), "object": json.dumps(object)}
            '''
            # should send to inbox:
            if full_followee_url[-1] == '/': full_followee_url += "inbox"
            else: full_followee_url += '/inbox'
            # post the friend request to the external server's inbox
            print("this is the full followee_url: ", full_followee_url)
            post_data = requests.post(full_followee_url, data=frd_request_serialized,
                auth=HTTPBasicAuth(auth_user, auth_pass))
            print("data responded: ", post_data)
        curProfile.save()
        # stay on the same page
        return redirect(request.META.get('HTTP_REFERER'))
    return redirect('public')

# by Shway, the follow function, to add someone to your follow list:
def unfollow_someone(request):
    if request.method == 'POST':
        followee_uid = request.POST.get('followee_uid')
        curProfile = UserProfile.objects.get(user = request.user)
        followee_profile = None
        try: # local
            followee_profile = UserProfile.objects.get(uid = followee_uid)
            # remove the uid from current user's follow:
            if followee_profile.user in curProfile.follow.all():
                curProfile.follow.remove(followee_profile.user)
        except Exception as e: # external
            print("Not local")
            if followee_uid in curProfile.externalFollows['urls']:
                curProfile.externalFollows['urls'].remove(followee_uid)
        curProfile.save()
        # stay on the same page
        return redirect(request.META.get('HTTP_REFERER'))
    return redirect('public')

# by Shway, to follow some one back and delete the follow from inbox:
def follow_back(request):
    if request.method == 'POST':
        # receive data from front-end
        followee_host = request.POST.get('followee_host')
        followee_github = request.POST.get('followee_github')
        followee_display_name = request.POST.get('followee_display_name')
        followee_uid = request.POST.get('followee_uid')
        print("uid ", followee_uid)
        print("host ", followee_host)
        print("gihtub ", followee_github)
        print("display_name ", followee_display_name)
        # get current user profile
        curProfile = UserProfile.objects.get(user = request.user)
        # save the new uid into current user's follow attribute:
        try: # local
            followee_profile = UserProfile.objects.get(uid = followee_uid)
            summary = curProfile.display_name + " wants to follow " + followee_display_name
            # create a new friend request locally
            newFrdRequest = FriendRequest.objects.create(actor=curProfile, object=followee_profile, summary = summary)
            curProfile.follow.add(followee_profile.user)
        except Exception as e: # external
            # cannot get the profile with followee_uid locally
            print("Not local")
            # First, add the uid into local database:
            if curProfile.externalFollows == {}:
                curProfile.externalFollows['urls'] = []
            curProfile.externalFollows['urls'].append(followee_uid)
            # Second, delete from inbox:
            # save the new uid into current user's follow attribute:
            profile = getUserProfile(request.user)
            print("inbox_view current profile: ", profile)
            # enumerate all possibilities of schemes
            full_id = str(profile.host) + '/author/' + str(profile.uid)
            if full_id.startswith('https://'):
                full_id = full_id[len('https://'):]
            elif full_id.startswith('http://'):
                full_id = full_id[len('http://'):]
            print("full_id",full_id)
            cur_inbox = Inbox.objects.filter(author=full_id)
            if len(cur_inbox) == 0:
                temp = "https://" + full_id
                cur_inbox = Inbox.objects.filter(author=temp)
                if len(cur_inbox) == 0:
                    temp = "http://" + full_id
                    cur_inbox = Inbox.objects.filter(author=temp)
                    if len(cur_inbox) == 0:
                        print("did not find any inbox with id: ", full_id)
                        return render(request, 'Iconicity/inbox.html', {'is_all_empty': True})
            cur_inbox = cur_inbox[0] # to get from a query set...
            for i in cur_inbox.items['Follow']:
                if followee_uid == json.loads(i['actor'])['uid']:
                    cur_inbox.items['Follow'].remove(i)
            cur_inbox.save()
            curProfile.save()
        # stay on the same page
        return redirect(request.META.get('HTTP_REFERER'))
    return redirect('public')

# by Shway, this view below shows the list of received friend requests:
def inbox_view(request):
    profile = getUserProfile(request.user)
    print("inbox_view current profile: ", profile)
    # enumerate all possibilities of schemes
    full_id = str(profile.host) + '/author/' + str(profile.uid)
    if full_id.startswith('https://'):
        full_id = full_id[len('https://'):]
    elif full_id.startswith('http://'):
        full_id = full_id[len('http://'):]
    print("full_id",full_id)
    cur_inbox = Inbox.objects.filter(author=full_id)
    if len(cur_inbox) == 0:
        temp = "https://" + full_id
        cur_inbox = Inbox.objects.filter(author=temp)
        if len(cur_inbox) == 0:
            temp = "http://" + full_id
            cur_inbox = Inbox.objects.filter(author=temp)
            if len(cur_inbox) == 0:
                print("did not find any inbox with id: ", full_id)
                return render(request, 'Iconicity/inbox.html', {'is_all_empty': True})
    cur_inbox = cur_inbox[0] # to get from a query set...
    print("found inbox with the id: ", full_id)
    # to see if the result is empty
    follows_size = len(cur_inbox.items['Follow'])
    # jsonify the actors and objects:
    
    for attribute in cur_inbox.items['Follow']:
    	attribute['actor'] = json.loads(attribute['actor'])
    	attribute['object'] = json.loads(attribute['object'])
    
    print("inbox_view cur_inbox: ", cur_inbox.items['Follow'])

    posts_size = len(cur_inbox.items['Post'])
    likes_size = len(cur_inbox.items['Like'])
    print("here are the sizes: ", follows_size, posts_size, likes_size)
    print('here are the contents: ', cur_inbox.items['Follow'], cur_inbox.items['Post'], cur_inbox.items['Like'])
    inbox_size = follows_size + posts_size + likes_size
    is_all_empty = False
    is_follows_empty = False
    is_posts_empty = False
    is_likes_empty = False
    if follows_size == 0: is_follows_empty = True
    if posts_size == 0: is_posts_empty = True
    if likes_size == 0: is_likes_empty = True
    if inbox_size == 0: is_all_empty = True
    print("Here are the determinations: ", is_follows_empty, is_posts_empty, is_likes_empty)
    # put information to the context
    context = {
        'is_follows_empty': is_follows_empty,
        'is_posts_empty': is_posts_empty,
        'is_likes_empty': is_likes_empty,
        'is_all_empty': is_all_empty,
        'likes': cur_inbox.items['Like'],
        'follows': cur_inbox.items['Follow'],
        'posts': cur_inbox.items['Post'],}
    return render(request, 'Iconicity/inbox.html', context)

# by Shway, to remove a follow notification from the inbox
def remove_inbox_follow(request):
    if request.method == 'POST':
        # receive data from front-end
        followee_host = request.POST.get('followee_host')
        followee_github = request.POST.get('followee_github')
        followee_display_name = request.POST.get('followee_display_name')
        followee_uid = request.POST.get('followee_uid')
        print("uid ", followee_uid)
        print("host ", followee_host)
        print("gihtub ", followee_github)
        print("display_name ", followee_display_name)
        # get current user profile
        curProfile = UserProfile.objects.get(user = request.user)
        # save the new uid into current user's follow attribute:
        profile = getUserProfile(request.user)
        print("inbox_view current profile: ", profile)
        # enumerate all possibilities of schemes
        full_id = str(profile.host) + '/author/' + str(profile.uid)
        if full_id.startswith('https://'):
            full_id = full_id[len('https://'):]
        elif full_id.startswith('http://'):
            full_id = full_id[len('http://'):]
        print("full_id",full_id)
        cur_inbox = Inbox.objects.filter(author=full_id)
        if len(cur_inbox) == 0:
            temp = "https://" + full_id
            cur_inbox = Inbox.objects.filter(author=temp)
            if len(cur_inbox) == 0:
                temp = "http://" + full_id
                cur_inbox = Inbox.objects.filter(author=temp)
                if len(cur_inbox) == 0:
                    print("did not find any inbox with id: ", full_id)
                    return render(request, 'Iconicity/inbox.html', {'is_all_empty': True})
        cur_inbox = cur_inbox[0] # to get from a query set...
        for i in cur_inbox.items['Follow']:
            if followee_uid == json.loads(i['actor'])['uid']:
                cur_inbox.items['Follow'].remove(i)
        cur_inbox.save()
        curProfile.save()
        # stay on the same page
        return redirect(request.META.get('HTTP_REFERER'))
    return redirect('public')

'''
# by Shway, accept friend request function view:
def accept_friend_request(request):
    if request.method == 'POST':
        uid = request.POST.get('accept_uid')
        sender = UserProfile.objects.get(uid = uid)
        receiver = UserProfile.objects.get(user = request.user)
        # save the new friend's uid into current user's follow and vice versa:
        sender.follow.add(receiver.user)
        #sender.externalFollows.append(receiver.host) # external connectivity
        receiver.follow.add(sender.user)
        # if sender.externalFollows like {}, we should add key value pair
        # assume all local:
        if sender.externalFollows == {}:
            sender.externalFollows['urls'] = []
        # if sender.externalFollows like {"urls":[]}, we can append
        full_recv_url = receiver.host
        if not receiver.host.startswith(str(request.scheme)):
            full_recv_url = str(request.scheme) + "://"  + str(receiver.host)
        if receiver.host[-1] == "/":
            full_recv_url = full_recv_url + "author/" + str(receiver.pk)
        else:
            full_recv_url = full_recv_url + "/author/" + str(receiver.pk)
        if not sender.host.startswith(str(request.scheme)):
            full_sender_url = str(request.scheme) + "://" + str(sender.host)
        if sender.host[-1] == "/":
            full_sender_url = full_sender_url + "author/" + str(sender.pk)
        else:
            full_sender_url = full_sender_url + "/author/" + str(sender.pk)
        sender.externalFollows['urls'].append(full_recv_url) # external connectivity
        if receiver.externalFollows == {}:
            receiver.externalFollows["urls"] = []
        receiver.externalFollows['urls'].append(full_sender_url) # external connectivity
        sender.save()
        receiver.save()
        print("reveiver",receiver.externalFollows["urls"])
        print(sender.externalFollows['urls'])
        # change the status of the friend request to accepted:
        sender.save()
        receiver.save()
        friend_request = FriendRequest.objects.get(actor = sender, object = receiver)
        if friend_request.status == 'sent':
            friend_request.status = 'accepted'
            friend_request.save()
        # stay on the same page
        return redirect(request.META.get('HTTP_REFERER'))
    return redirect('main')
'''

# by Shway, reject friend request function view:
'''
def reject_friend_request(request):
    if request.method == 'POST':
        uid = request.POST.get('reject_uid')
        sender = UserProfile.objects.get(uid = uid)
        receiver = UserProfile.objects.get(user = request.user)
        friend_request = get_object_or_404(FriendRequest, actor = sender, object_author = receiver)
        friend_request = FriendRequest.objects.get(actor = sender, object = receiver)
        friend_request.delete()
        # stay on the same page
        return redirect(request.META.get('HTTP_REFERER'))
    return redirect('main')
'''

# by Shway, this view below shows the list of all profiles except for the current user
class UserProfileListView(ListView):
    model = UserProfile
    template_name = 'Iconicity/all_profile_list.html'
    context_object_name = 'profiles'
    # override:
    def get_queryset(self):
        # get all profiles except for current user from both local host and remote hosts:
        local = UserProfile.objects.get_all_profiles(exception = self.request.user)
        remote = getAllExternalAuthors()
        return remote + list(local)
    # override:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        # my profile
        my_profile = UserProfile.objects.filter(user = user)[0] # type is a query set!
        '''
        # whom I want to follow
        pending_requests = FriendRequest.objects.filter(Q(actor = my_profile.user) & Q(status = 'sent'))
        # whom wants to follow me
        inbox_requests = FriendRequest.objects.filter(Q(object = my_profile.user) & Q(status = 'sent'))
        # friend relations requests
        accepted_requests = FriendRequest.objects.filter(
            (Q(object = my_profile.user) | Q(actor = my_profile.user)) & Q(status = 'accepted'))
        '''
        # listify and setify the above two results:
        '''
        pending_requests_list = set()
        inbox_requests_list = set()
        accepted_list = set()
        '''
        follow_list_processed = set()
        # whom I am following locally
        follow_list = my_profile.get_followers()
        # whom I am following externally
        external_follows_list = my_profile.get_external_follows()
        print("whom I am following: ", external_follows_list)

        '''
        for i in follow_list:
            if not(i.github == '' or i.github == None):
                follow_list_processed.add(i)
        '''

        '''
        for i in pending_requests:
            pending_requests_list.add(i.object.user)
        for i in inbox_requests:
            inbox_requests_list.add(i.actor.user)
        for i in accepted_requests:
            accepted_list.add(i.actor.user)
            accepted_list.add(i.object_author.user)
        '''
        context['follows'] = follow_list_processed
        context['external_follows'] = external_follows_list
        '''
        context['pending_requests'] = pending_requests_list
        context['inbox_requests'] = inbox_requests_list
        context['accepted_requests'] = accepted_list
        '''
        # if there are no profiles other than the current user:
        context['is_empty'] = False # initially not empty
        if len(self.get_queryset()) == 0:
            context['is_empty'] = True
        return context

# by Shway, view function for sending friend requests
'''
def send_friend_request(request):
	if request.method == 'POST':
		uid = request.POST.get('profile_uid')
		sender = UserProfile.objects.get(user=request.user) # current user is the sender
		try:
			receiver = UserProfile.objects.get(uid=uid)
			# create a new friend request
			FriendRequest.objects.create(actor=sender, object=receiver, status='sent')
		except Exception as e: # external friend request
			print(e)
			# First, add the uid into local database:
            if curProfile.externalFollows == {}:
                curProfile.externalFollows['urls'] = []
            curProfile.externalFollows['urls'].append(followee_uid)
            # Second create a new UserPfile and a new friend request:
            receiver = UserProfile(user=User,
                          display_name=Display_name,
                          github=Github,
                          host=host)
    		receiver.url = str(scheme) + "://" + str(host) + '/author/' + str(receiver.uid)

            FriendRequest.objects.create(actor=sender, object=receiver, status='sent')
            # Third, send the remote post request:
            # create a new friend request with the receiver the (external) followee_uid
            summary = curProfile.display_name + " wants to follow " + followee_display_name
            # serialized current profile
            serialized_actor = GETProfileSerializer(curProfile)
            # form the freind request data stream
            object = json.dumps({"type":"author", "id":followee_uid, "host":followee_host, "displayName":followee_display_name,
                "url":followee_uid, "github": followee_github})
            frd_request_context = {"type": "Friend", "summary": summary, "actor": serialized_actor, "object": object}
            full_followee_url = followee_uid
            # add the request scheme if there isn't any
            if not full_followee_url.startswith(str(request.scheme)):
                full_followee_url = str(request.scheme) + "://"  + str(full_followee_url)
            # should send to inbox:
            if full_followee_url[-1] == '/': full_followee_url += "inbox"
            else: full_followee_url += '/inbox'
            # post the friend request to the external server's inbox
            print(full_followee_url)
            post_data = requests.post(full_followee_url, data=frd_request_context)
            print("data responded: ", post_data)
		curProfile.save()
		# stay on the same page
		return redirect(request.META.get('HTTP_REFERER'))
	# go to main page if the user did not use the "POST" method
	return redirect('main')
'''

'''
# by Shway, view function for removing a friend
def remove_friend(request):
    if request.method == 'POST':
        uid = request.POST.get('profile_uid')
        sender = UserProfile.objects.get(user=request.user)
        receiver = UserProfile.objects.get(uid=uid)
        # delete the friend request involving current user and the past in user with uid specified
        friendRequest = FriendRequest.objects.get(
            (Q(actor=sender) & Q(object=receiver)) | (Q(actor=receiver) & Q(object=sender)))
        friendRequest.delete()
        # want to also unfollow both, but it is done by the function beneath this one
        # stay on the same page
        return redirect(request.META.get('HTTP_REFERER'))
    return redirect('main')

# by Shway, whenever a friend request is deleted, want to also delete
# from follow lists of actor and object_author
@receiver(pre_delete, sender=FriendRequest)
def pre_delete_remove_from_follow(sender, instance, **kwargs):
    sender = instance.actor
    receiver = instance.object_author
    sender.follow.remove(receiver.user)
    if receiver.host in sender.externalFollows:
        sender.externalFollows.remove(receiver.host) # external connectivity
    receiver.follow.remove(sender.user)
    if sender.host in receiver.externalFollows:
        receiver.externalFollows.remove(sender.host) # external connectivity
    sender.save()
    receiver.save()
'''
'''
def like_view(request):
    redirect_path = '/public'
    if request.path == "/friends/like":
        redirect_path = "/friends"
    elif request.path == "/mypost/like":
        redirect_path = "/mypost"
    elif request.path == "/public/like":
        redirect_path = "/public"
    elif request.path == "/following/like":
        redirect_path = "/following"

    # here two cases:
    # 1. if this post is on our server, then pk works
    # 2. if this post is not on our server, then url works
    pk_raw = request.POST.get('pk')
    current_user_profile = UserProfile.objects.get(user=request.user)
    current_url = current_user_profile.url
    post = None
    changed = False

    #print(request.POST.data)
    if '/' in pk_raw:
        try:
            pk_new = [i for i in pk_raw.split('/') if i][-1]
            print(pk_new)
            post = Post.objects.get(pk=pk_new)
        except Exception as e:
            # means that this is not on our server
            print("pk_raw")
            print(e)
            get_json_response = requests.get(pk_raw, auth=HTTPBasicAuth(auth_user, auth_pass))
            response_dict = json.loads(get_json_response.text)[0]
            print("response_dict",response_dict)
            post_external_like = response_dict["external_likes"]
            if post_external_like == {}:
                post_external_like['urls'] = []

            # Means that this post has already been liked by you.
            # We remove this like from the list, means unlike the post
            if current_url in post_external_like['urls']:
                print("This user has clicked on like on this post before")
                post_external_like['urls'].remove(current_url)
            else:
                # You haven't clicked on the like button before, so append it to 
                # this post's external like list.
                post_external_like['urls'].append(current_url)
            print(post_external_like['urls'])
            response = requests.post(pk_raw,
                data={"external_likes":json.dumps({"urls":post_external_like['urls']})}, 
                auth=HTTPBasicAuth(auth_user, auth_pass))
            print("like response",response)

        else:
            # means that this post is on our server
            if request.user in list(post.like.all()):
                changed = False
            else:
                changed = True
                post.like.add(request.user)
                post.like_count = post.count_like()
                post.save()

        
    else:
        # Pass in primary key, this post is on our system.
        post = get_object_or_404(Post, pk=request.POST.get('pk'))
        if request.user in list(post.like.all()):
            changed = False
        else:
            changed = True
            post.like.add(request.user)
            post.like_count = post.count_like()
            post.save()

    # Send something to its inbox

    if changed:
        like_obj = Like()
        like_obj.summary = "%s liked your post."%(current_user_profile.display_name)
        like_obj.author = GETProfileSerializer(current_user_profile).data

        like_obj.object = pk_raw
        print("like object",like_obj.object)
        inbox_url = (str(request.scheme) + "://"
                                        + str(request.get_host())
                                        + '/author/'
                                        + str(current_user_profile.pk)
                                        + '/inbox')
        like_serializer = LikeSerializer(like_obj).data

        response = requests.post(inbox_url,
                                data={"like_obj":json.dumps(like_serializer)}, 
                                auth=HTTPBasicAuth(auth_user, auth_pass))
        print("like inbox response",response)


    return redirect(redirect_path)
'''
def like_view(request):
    redirect_path = '/public'
    if request.path == "/friends/like":
        redirect_path = "/friends"
    elif request.path == "/mypost/like":
        redirect_path = "/mypost"
    elif request.path == "/public/like":
        redirect_path = "/public"
    elif request.path == "/following/like":
        redirect_path = "/following"

    # here two cases:
    # 1. if this post is on our server, then pk works
    # 2. if this post is not on our server, then url works
    pk_raw = request.POST.get('pk')
    current_user_profile = UserProfile.objects.get(user=request.user)
    like_obj = Like()
    like_obj.summary = "%s liked your post."%(current_user_profile.display_name)
    like_obj.author = GETProfileSerializer(current_user_profile).data

    like_obj.object = pk_raw
    post_info = requests.get(pk_raw, auth=HTTPBasicAuth(auth_user, auth_pass)).json()[0]

    post_author_url = post_info['author']['url']
    full_inbox_url = post_author_url
    if post_author_url[-1] != "/":
        full_inbox_url += "/"
    full_inbox_url += 'inbox'
    print("inbox url",full_inbox_url)


    print("like object",like_obj.object)
    
    like_serializer = LikeSerializer(like_obj).data

    response = requests.post(full_inbox_url,
                            data={"obj":json.dumps(like_serializer)}, 
                            auth=HTTPBasicAuth(auth_user, auth_pass))
    print("like inbox response",response)
    return redirect(redirect_path)



def repost(request):
    # should pass back the post from the frontend
    pk_raw = request.POST.get('pk')
    get_json_response = requests.get(pk_raw, auth=HTTPBasicAuth(auth_user, auth_pass))
    post = json.loads(get_json_response.text)[0]
    print("response_dict",post)
    ordinary_dict = {'title': post['title'], 'content': post['content'], 'visibility':'PUBLIC', 'contentType': post['contentType']}
    query_dict = QueryDict('', mutable=True)
    query_dict.update(ordinary_dict)
    post_form = PostsCreateForm(query_dict)
    img_path = post['image']
    if img_path is not None:
        img_path_dict = img_path.split("/")
        new_path = ""
        for i in range(2, len(img_path_dict)):
            new_path = new_path + "/" + img_path_dict[i]
    
    if post_form.is_valid():
        post_form = post_form.save(commit=False)
        post_form.origin = post['origin']
        post_form.author = request.user
        if img_path is not None:
            post_form.image = new_path
        post_form.origin = post['origin']
        userProfile = UserProfile.objects.get(user=request.user)
        post_form.source = (str(request.scheme) + "://"
                                            + str(request.get_host())
                                            + '/author/'
                                            + str(userProfile.pk)
                                            + '/posts/'
                                            + str(post_form.post_id))
        post_form.save()
        print("post_form image", post_form.image)

    else:
        print(post_form.errors)
    return redirect('public')

def repost_to_friend(request):
    # should pass back the post from the frontend
    pk_raw = request.POST.get('pk')
    print(pk_raw)
    get_json_response = requests.get(pk_raw, auth=HTTPBasicAuth(auth_user, auth_pass))
    print(json.loads(get_json_response.text))
    post = json.loads(get_json_response.text)[0]

    ordinary_dict = {'title': post['title'], 'content': post['content'], 'visibility':'FRIENDS', 'contentType': post['contentType']}
    query_dict = QueryDict('', mutable=True)
    query_dict.update(ordinary_dict)
    post_form = PostsCreateForm(query_dict)
    img_path = post['image']
    if img_path is not None:
        img_path_dict = img_path.split("/")
        new_path = ""
        for i in range(2, len(img_path_dict)):
            new_path = new_path + "/" + img_path_dict[i]
    if post_form.is_valid():
        post_form = post_form.save(commit=False)
        post_form.author = request.user
        if img_path is not None:
            post_form.image = new_path
        post_form.origin = post['origin']
        userProfile = UserProfile.objects.get(user=request.user)
        post_form.source = (str(request.scheme) + "://"
                                            + str(request.get_host())
                                            + '/author/'
                                            + str(userProfile.pk)
                                            + '/posts/'
                                            + str(post_form.post_id))
        post_form.save()
    else:
        print(post_form.errors)
    return redirect('public')

def update_post_view(request):
    post_url = request.POST.get('pk')
    if (post_url):
        print('Step 1')
        pk = [i for i in post_url.split('/') if i][-1]
        post = get_object_or_404(Post, pk=pk)
        print("post:",post.image)
        post_form = PostUpdateForm(instance = post)
        print("post_form: ", post_form)
        for key in post_form['image']:
            print('-----------------')
            print(key)
        context = {
        'post':post,
        'post_form':post_form,
        }
    post_update_url = request.POST.get('pid')
    if (post_update_url):
        print('Step 2')
        print('post_update_url', post_update_url)
        post_id = [i for i in post_update_url.split('/') if i][-1]
        print('post_id', post_id)
        post = get_object_or_404(Post, pk=post_id)
        post_form = PostUpdateForm(request.POST, request.FILES)

        if post_form.is_valid():
            # https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Forms
            # RenewbookForm
            post.title = post_form.cleaned_data['title']
            post.content = post_form.cleaned_data['content']
            if (post_form.cleaned_data['image']):
                post.image = post_form.cleaned_data['image']
            post.visibility = post_form.cleaned_data['visibility']
            post.save()
            return redirect('mypost')
    return render(request,'Iconicity/update_post.html', context)

def profile(request):
    userProfile = getUserProfile(request.user)

    if request.method =="POST":

        user_form = UserUpdateForm(request.POST,instance = request.user)

        profile_form = ProfileUpdateForm(request.POST,instance = request.user.userprofile)

        if user_form.is_valid() and profile_form.is_valid():

            user_form.save()
            profile_form.save()
            return redirect('public')

    else:
        user_form = UserUpdateForm(instance = request.user)
        profile_form = ProfileUpdateForm(instance = request.user.userprofile)

    context = {
    'UserProfile': userProfile,
    'user_form':user_form,
    'profile_form':profile_form,
    }
    return render(request,'Iconicity/profile.html', context)

def public(request):
    return render(request,'Iconicity/public.html')

def mypost(request):

    if request.user.is_anonymous:
        return render(request,
                      'Iconicity/login.html',
                      { 'form':  AuthenticationForm })
    # get all the posts posted by the current user
    postList = getPosts(request.user, visibility="FRIENDS")
    new_list = []
    new_list += PostSerializer(postList, many=True).data
    new_list.reverse()
    context = {
        'posts': new_list,
        'UserProfile': getUserProfile(request.user),
    }
    return render(request, 'Iconicity/my_post.html', context)

def getAllFollowExternalAuthorPosts(currentUser):
    # https://stackoverflow.com/questions/12965203/how-to-get-json-from-webpage-into-python-script
    # https://vast-shore-25201.herokuapp.com/author/543a1266-23f5-4d60-a9a2-068ac0cb5686
    post_list = []
    try:
        userProfile = UserProfile.objects.get(user=currentUser)
    except Exception as e:
        print(e)
        return []
    if userProfile:
        #print("in")
        externalAuthorUrls = userProfile.get_external_follows()
        if externalAuthorUrls != []:
            # now it should be a list of urls of the external followers
            # should like [url1, url2]

            for each_url in externalAuthorUrls:
                full_url = each_url
                if each_url[-1]=="/":
                    full_url += "posts/"
                else:
                    full_url += "/posts/"
                temp = requests.get(full_url, auth=HTTPBasicAuth(auth_user, auth_pass))
                responseJsonlist = temp.json()

                post_list += responseJsonlist

    return post_list


def getAllConnectedServerHosts():
    # return a list [hosturl1, hosturl2...]
    return [i.get_host() for i in list(ExternalServer.objects.all())]

def getAllPublicPostsCurrentUser():
    userProfile = UserProfile.objects.all()
    allAuthors = json.dumps(GETProfileSerializer(userProfile,many=True).data)


def getAllExternalPublicPosts():
    externalHosts = getAllConnectedServerHosts()
    allPosts = []
    full_url = ''
    for host_url in externalHosts:
        if host_url[-1] == "/":
            full_url = host_url + "posts"
        else:
            full_url = host_url + "/posts"
        the_user_name = auth_user
        the_user_pass = auth_pass
        if host_url == team10_host_url:
            the_user_name = team10_name
            the_user_pass = team10_pass
        
        temp = requests.get(full_url, auth=HTTPBasicAuth(the_user_name, the_user_pass))
        if host_url == team10_host_url:
            posts = temp.json()['posts']
        else:
            posts = temp.json()

        allPosts += posts
    return allPosts

# by Shway, to get all remote authors from all connected servers:
def getAllExternalAuthors():
    externalHosts = getAllConnectedServerHosts()
    allAuthors = []
    full_url = ''
    for host_url in externalHosts:
        if host_url[-1] == "/":
            full_url = host_url + "author"
        else:
            full_url = host_url + "/author"
        # for connecting to other teams:
        the_user_name = auth_user
        the_user_pass = auth_pass
        if host_url == team10_host_url:
            the_user_name = team10_name
            the_user_pass = team10_pass
            full_url += "s"
        print("getAllExternalAuthors full url: ", full_url)
        temp = requests.get(full_url, auth=HTTPBasicAuth(the_user_name, the_user_pass))
        if host_url == team10_host_url:
            authors = temp.json()['authors']
        else:
            authors = temp.json()
        allAuthors += authors
    return allAuthors

class AllAuthors(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        # Get all local authors
        userProfile = UserProfile.objects.all()
        temp = GETProfileSerializer(userProfile,many=True).data
        return Response(temp)


class AuthorById(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, author_id):
        userProfile = UserProfile.objects.get(pk=author_id)
        serializer = GETProfileSerializer(userProfile)
        return Response(serializer.data)

def following(request):

    if request.user.is_anonymous:
        return render(request, 'Iconicity/login.html', { 'form':  AuthenticationForm })
    userProfile = getUserProfile(request.user)
    # get all the posts posted by the current user
    postList = getAllFollowAuthorPosts(request.user)
    new_list = []
    new_list += PostSerializer(postList, many=True).data

    new_list += getAllFollowExternalAuthorPosts(request.user)
    for post in new_list:
        if post['image'] is not None:
            abs_imgpath = str(request.scheme) + "://" + post['author']['host'] + post['image']
            post['image'] = abs_imgpath
    new_list.reverse()
    context = {
        'posts': new_list,
        'UserProfile': userProfile,
        'myself': str(request.user),
    }
    return render(request,'Iconicity/follow.html', context)

def getUserFriend(currentUser):
    userProfile = getUserProfile(currentUser)
    friendList = []
    # get all local followers of our user
    allFollowedAuthors = list(userProfile.get_followers())
    for user in allFollowedAuthors:
        # check whether they are friends.
        # means a two-direct-follow
        otherUserProfile = UserProfile.objects.filter(user=user).first()
        if otherUserProfile and (currentUser in list(otherUserProfile.get_followers())):
            print("they are friends")
            friendList.append(user)


    return friendList

def getExternalUserFriends(currentUser):
    userProfile = getUserProfile(currentUser)
    friendUrlList = []
    # now check external followers. check whether they are bi-direction.
    externalFollowers = userProfile.get_external_follows() # a list of urls

    for each_url in externalFollowers:
        full_url = each_url

        if each_url[-1] == "/":
            full_url += "followers/"
        else:
            full_url += "/followers/"

        # now check whether you are also his/hers followee.
        temp = requests.get(full_url, auth=HTTPBasicAuth(auth_user, auth_pass))
        friends = temp.json()['externalFollows']
        if userProfile.url in friends:
            friendUrlList.append(each_url)

    return friendUrlList

def friends(request):
    if request.user.is_anonymous:
        return render(request, 'Iconicity/login.html', { 'form':  AuthenticationForm })
    # get all the posts posted by the current user
    postList = []
    friends_test = getUserFriend(request.user)
    tmp_list = []
    for friend_id in friends_test:
        tmp_list += getPosts(friend_id, visibility="FRIENDS")

    new_list = PostSerializer(tmp_list, many=True).data
    externalFriends = getExternalUserFriends(request.user)
    if externalFriends and externalFriends !=[]:
        for each_url in externalFriends:
            full_url = each_url

            if each_url[-1] == "/":
                full_url += "friendposts/"
            else:
                full_url += "/friendposts/"
            posts = requests.get(full_url, auth=HTTPBasicAuth(auth_user, auth_pass)).json()
            postList += posts
    postList += new_list  
    for post in postList:
        if post['image'] is not None:
            abs_imgpath = str(request.scheme) + "://" + post['author']['host'] + post['image']
            post['image'] = abs_imgpath
    userProfile = getUserProfile(request.user)
    postList.reverse()
    context = {
        'posts': postList,
        'UserProfile': userProfile,
        'myself': str(userProfile.url)
    }

    return render(request,'Iconicity/friends.html', context)

class Posts(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        # get all posts with visibility == "PUBLIC"
        '''
        if request.user.is_authenticated:
            posts = Post.objects.filter(visibility = "PUBLIC").all()
            serializer = PostSerializer(posts, many=True)
            return Response(serializer.data)
        else:
            # the user is unauthorized
            return HttpResponse('Unauthorized', status=401)
        '''

        posts = Post.objects.filter(visibility = "PUBLIC").all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

class PostById(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, post_id, author_id):
        posts = Post.objects.filter(pk=post_id).all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)
        '''
        if request.user.is_authenticated:
            posts = Post.objects.filter(pk=post_id).all()
            serializer = PostSerializer(posts, many=True)
            return Response(serializer.data)
        else:
            # the user is unauthorized
            return HttpResponse('Unauthorized', status=401)'''

    def post(self, request, post_id, author_id):
        '''
        update an existed post
        Usage:
        pass in a json file like {"title":"123", "count":2341}, 
        these two fields in the post model will be set to the new values 
        in the above dict.
        '''
        post = Post.objects.get(pk=post_id)
        for each in request.data.items():
            if each[0] == "external_likes":
                setattr(post, each[0], json.loads(each[1]))
            else:
                setattr(post, each[0],each[1])

        post.save(update_fields=[each[0] for each in request.data.items()])
        serializer = PostSerializer(post, many=False)

        return Response(serializer.data)

    def delete(self, request, post_id, author_id):
        Post.objects.get(pk=post_id).delete()
        return Response([],status="HTTP_204_NO_CONTENT")

    def put(self, request, post_id, author_id):
        pass

class Inboxs(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, author_id):
        User = UserProfile.objects.get(pk=author_id)
        inbox = Inbox.objects.get(author=User.url)
        return Response(InboxSerializer(inbox).data)

    def post(self, request, author_id):

        data_json = json.loads(request.POST.get('obj'))
        print("data_json",data_json)
        local_author_profile = UserProfile.objects.get(pk=author_id)
        try:
            inbox_obj = Inbox.objects.get(author=local_author_profile.url)
            print("inbox_obj: ", inbox_obj)
            if data_json['type'] == "Like":
                # if the type is “like” then add that like to the author’s inbox
                post_url = data_json["object"]
                print("url",post_url)
                post_id = [i for i in post_url.split('/') if i][-1]
                print("id",post_id)
                post_obj = Post.objects.get(pk=post_id)
                
                if request.META['HTTP_HOST'] in data_json['author']['url']:
                    # means it's local like author              
                    # means add this man's id to the like list.
                    post_obj.like.add(local_author_profile.user)
                    like_obj = Like()
                    like_obj.context= data_json["context"]
                    like_obj.object = data_json["object"]
                    like_obj.summary = data_json["summary"]
                    like_obj.author = data_json["author"]
                    like_obj.save()
                    post_obj.save()
                    like_json = LikeSerializer(like_obj).data
                    inbox_obj.items.append(like_json)
                    inbox_obj.save()
                    print("here2")
                    return Response(InboxSerializer(inbox_obj).data,status=201)
                else:
                    # means it's a external author
                    external_author_url = data_json["author"]["url"]
                    if post_obj.external_likes == {} or post_obj.external_likes == {"urls":[]} or data_json["author"]["url"] not in post_obj.external_likes['urls']:
                        # means add this man's id to the external like list.
                        post_obj.external_likes['urls'] = []
                        post_obj.external_likes['urls'].append(external_author_url)
                        like_obj = Like()
                        like_obj.context= data_json["context"]
                        like_obj.object = data_json["object"]
                        like_obj.summary = data_json["summary"]
                        like_obj.author = data_json["author"]
                        like_obj.save()
                        post_obj.save()
                        like_json = LikeSerializer(like_obj).data
                        inbox_obj.items.append(like_json)
                        inbox_obj.save()
                        return Response(InboxSerializer(inbox_obj).data,status=201)
                    else:
                        # means this man liked the post before
                        # we should make him unlike this post
                        post_obj.external_likes['urls'].remove(external_author_url)
                        post_obj.save()
                        return Response(InboxSerializer(inbox_obj).data,status=204)
            
            elif (data_json['type'] == "post" or data_json['type'] == "Post"):
                # if the type is “post” then add that post to the author’s inbox
                # add a post to the author_id's inbox
                inbox_obj.items.append(data_json)
                inbox_obj.save()
                return Response(InboxSerializer(inbox_obj).data,status=200)

            elif data_json['type'] == "Follow": 
                # if the type is “Follow” then add that follow is added to the author’s inbox to approve later
                inbox_obj.items.append(data_json)
                inbox_obj.save()
                return Response(InboxSerializer(inbox_obj).data,status=200)

            elif data_json['type'] == 'comment':
                inbox_obj.items.append(data_json)
                inbox_obj.save()
                return Response(InboxSerializer(inbox_obj).data,status=200)
            else:
                print("Inbox operation not handled")
        except Exception as e:
            print("Error happened: ", e)

    def delete(self, request, author_id):
        # clear the inbox
        # i.e. clear three lists inside the inbox object
        currentUser = UserProfile.objects.get(pk=author_id)

        inbox = Inbox.objects.get(author=currentUser.url)
        inbox.items = []
        inbox.save()
        return Response(InboxSerializer(inbox).data,status=200)

class AllPostsByAuthor(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, author_id):
        authorProfile = UserProfile.objects.get(pk=author_id)
        posts = Post.objects.filter(author=authorProfile.user).all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

class ExternalFollowersByAuthor(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, author_id):
        authorProfile = UserProfile.objects.get(pk=author_id)
        return Response(ExternalFollowersSerializer(authorProfile).data)

class FriendPostsByAuthor(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, author_id):
        authorProfile = UserProfile.objects.get(pk=author_id)
        friendPosts = Post.objects.filter(author=authorProfile.user)
        return Response(PostSerializer(friendPosts, many=True).data)

def post_comments(request):
    ppid = request.POST.get('ppid')
    if ppid:
        
        context = {'form123': CommentsCreateForm(), "url": ppid}
        return render(request, 'Iconicity/comment_form.html', context)


    pk_raw = request.POST.get('pk')
    currentUserProfile = UserProfile.objects.get(user=request.user)
    author_json = requests.get(currentUserProfile.url, auth=HTTPBasicAuth(auth_user, auth_pass)).json()

    post = None
    pk_new = None
    print("pk_raw",pk_raw)
    if pk_raw:
        if '/' in pk_raw:
            try:
                pk_new = [i for i in pk_raw.split('/') if i][-1]
                post = Post.objects.get(pk=pk_new)
            except Exception as e:
                # means that this is not on our server
                print("not on server")

                post_id = pk_raw
                form = CommentsCreateForm(request.POST)
                if form.is_valid():
                    #form = form.save(commit=False)
                    #form.post = post_id
                    #form.author = currentUserProfile.url
                    #form.save()
                    
                    if pk_raw[-1] == "/":
                        response = requests.post(pk_raw+"comments",
                            data={"comment":form.cleaned_data['comment'],"author":json.dumps(author_json)}, 
                            auth=HTTPBasicAuth(auth_user, auth_pass))


                    else:
                        response = requests.post(pk_raw+"/comments",
                            data={"comment":form.cleaned_data['comment'],"author":json.dumps(author_json)}, 
                            auth=HTTPBasicAuth(auth_user, auth_pass))
                    print("response",response)
                    post_info = requests.get(pk_raw,
                                        auth=HTTPBasicAuth(auth_user, auth_pass)).json()[0]
                    post_author_url = post_info['author']['url']
                    full_inbox_url = post_author_url
                    if post_author_url[-1] != "/":
                        full_inbox_url += "/"
                    full_inbox_url += 'inbox'
                    print("url",full_inbox_url)
                    
                    comment_obj = Comment()
                    comment_obj.comment = form.cleaned_data['comment']
                    comment_obj.author = author_json
                    comment_obj.post = pk_raw
                    comment_serializer = CommentSerializer(comment_obj).data
                    
                    response = requests.post(full_inbox_url,
                            data={"obj":json.dumps(comment_serializer)}, 
                            auth=HTTPBasicAuth(auth_user, auth_pass))
                    print("response",response)
                    return redirect('public')
                    
                else:
                    print(form.errors)
                    form = CommentsCreateForm(request.POST)
                
                context = {
                    'form123': form,
                    'post':post
                }
                
                return render(request, template, context)
            else:
                print("on our server")
                # means that this post is on our server
                context = {
                    'form123':  CommentsCreateForm(request.POST),
                    'post':post,
                }
                template = "Iconicity/comment_form.html"
                form = CommentsCreateForm(request.POST)
                if form.is_valid():
                    newform = form.save(commit=False)
                    newform.post = pk_raw
                    newform.author = author_json
                    #form.author_id = request.user.id
                    newform.save()
                    post_info = requests.get(pk_raw,
                                        auth=HTTPBasicAuth(auth_user, auth_pass)).json()[0]
                    post_author_url = post_info['author']['url']
                    full_inbox_url = post_author_url
                    if post_author_url[-1] != "/":
                        full_inbox_url += "/"
                    full_inbox_url += 'inbox'
                    print(author_json)
                    print(type(author_json))
                    comment_obj = Comment()
                    comment_obj.comment = form.cleaned_data['comment']
                    comment_obj.author = author_json
                    comment_obj.post = pk_raw
                    comment_serializer = CommentSerializer(comment_obj).data
                    print(comment_serializer)

                    response = requests.post(full_inbox_url,
                            data={"obj":json.dumps(comment_serializer)}, 
                            auth=HTTPBasicAuth(auth_user, auth_pass))
                    return redirect('public')
                    
                else:
                    print(form.errors)
                    form = CommentsCreateForm(request.POST)
                
                context = {
                    'form123': form,
                }
                return render(request, template, context)


class Comments(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id, author_id):
        # POST if you post an object of “type”:”comment”, 
        # it will add your comment to the post
        print("inpost")
        comment = Comment()

        comment.post = (str(request.scheme) + "://"
                                           + str(request.get_host())
                                           + '/author/'
                                           + str(author_id)
                                           + '/posts/'
                                           + str(post_id))
        # only two things need to be pass through request are the comment content
        # and the url of the author that write the comment on your post. 
        comment.comment = request.data['comment']
        comment.author = json.loads(request.data['author'])
        comment.save()
        return Response([],status=201)


        

    def get(self, request, post_id, author_id):
        # GET get comments of the post
        print("in comments")
        post = (str(request.scheme) + "://"
                                    + str(request.get_host())
                                    + '/author/'
                                    + str(author_id)
                                    + '/posts/'
                                    + str(post_id))
        comments = list(Comment.objects.filter(post=post))
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

class Likes(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, post_id, author_id):
        post = (str(request.scheme) + "://"
                            + str(request.get_host())
                            + '/author/'
                            + str(author_id)
                            + '/posts/'
                            + str(post_id))
        likes = list(Like.objects.filter(object=post))
        serializer = LikeSerializer(likes,many=True)
        return Response(serializer.data)
