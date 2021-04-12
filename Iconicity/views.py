from django.shortcuts import render, resolve_url, reverse, get_object_or_404,redirect
from django.http import HttpResponse, HttpResponseRedirect, QueryDict
from .models import *
from .config import *
from django.urls import resolve
from django.http import JsonResponse
from django.core.paginator import Paginator
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib import messages
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
import datetime
from math import ceil
#https://thecodinginterface.com/blog/django-auth-part1/

def ajax(request):
    return render(request,"Iconicity/hello.html")

def logout_view(request):
    # in use, support log out
    # http://www.learningaboutelectronics.com/Articles/How-to-create-a-logout-button-in-Django.php
    if request.method == 'POST':
        logout(request)
        return redirect(reverse('login'))

# citation:https://simpleisbetterthancomplex.com/tutorial/2017/02/18/how-to-create-user-sign-up-view.html#sign-up-with-profile-model

def createPreferenceObject():
    confirm = None
    try:
        confirm = SignUpConfirm.objects.all()
        assert confirm != None and list(confirm) != [],"raise"
    except Exception:
        # means we don't have this settings
        obj = SignUpConfirm()
        obj.save()
        return obj.boolean
    else:
        temp = list(confirm)[0].boolean
        return temp
class PickyAuthenticationForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise ValidationError(
                _("This account is inactive."),
                code='inactive',
            )

class LoginView(View):
    def get(self, request):
        print("get", request)
        if not request.user.is_anonymous and request.user.is_active:
            return redirect(reverse('public'))

        return render(request, 'Iconicity/start.html', { 'login_form':  PickyAuthenticationForm, 'signup_form': SignUpForm(request.POST) })


    def post(self,request):
        print("post", request)
        login_form = PickyAuthenticationForm(request, data=request.POST)
        signup_form = SignUpForm(request.POST)
        if login_form.is_valid():
            print("login")
            try:
                login_form.clean()
            except ValidationError:
                messages.error(request,'Username or password not correct\n or your account is not verified by the admin.')

                return render(
                    request,
                    'Iconicity/start.html',
                    { 'login_form': login_form, 'invalid_creds': True, 'signup_form':signup_form  }
                )

            login(request, login_form.get_user())

            return redirect(reverse('public'))
        
        elif signup_form.is_valid():
            print("sign up")
            boolean = createPreferenceObject()
            print("boolean",boolean)
            user = signup_form.save(commit=False)
            if boolean:
                # this means the signup needs to be activated by the admin
                user.is_active = False
            else:
                user.is_active = True
            print(user.is_active)
            user.save()
            username = signup_form.cleaned_data.get('username')
            raw_password = signup_form.cleaned_data.get('password1')
            User = user
            Github = signup_form.cleaned_data.get('github')
            host = request.get_host()
            scheme = request.scheme
            createUserProfileAndInbox(scheme, username, User, Github, host)
            if user.is_active:
                login(request, user)
                return redirect('public')
            else:
                # messages.error(request,'Your account is not verified by the admin.')
                return render(request, 'Iconicity/start.html', 
                { 'login_form': login_form, 'signup_form':signup_form, 'state': "not_active" })

        # Go back to start.html
        # When the login/signup fails, retrieve data
        login_details = {}
        signup_details = {}

        for i in login_form:
            login_details[str(i.name)] = i.value()

        for i in signup_form:
            signup_details[str(i.name)] = i.value()

        # Login Problem
        if login_details['username'] and login_details['password']:
            print("login problem")
            state = 'login_problem'

        # Signup problem
        if signup_details['email'] or signup_details['password1'] or signup_details['password2'] or signup_details['github']:
            state = 'signup_problem'

        return render(request, 'Iconicity/start.html', 
        { 'login_form': login_form, 'signup_form':signup_form, 'state':state })

# citation:https://simpleisbetterthancomplex.com/tutorial/2017/02/18/how-to-create-user-sign-up-view.html#sign-up-with-profile-model


def signup(request):
    print("signup", request)
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
    return render(request, 'Iconicity/start.html', {'signup_form': form})


@login_required
def mainPagePublic(request):
    # https://docs.djangoproject.com/en/3.1/topics/serialization/
    if request.user.is_anonymous:
        return render(request, 'Iconicity/login.html', { 'form':  AuthenticationForm })
    #string = str(request.scheme) + "://" + str(request.get_host())+"/posts/"
    new_list = [] 
    time_check1 = datetime.datetime.now()
    new_list += PostSerializer(list(Post.objects.all()),many=True).data
    print("new_list",new_list)
    externalPosts = getAllExternalPublicPosts()
    time_check2 = datetime.datetime.now()
    print("timecheck2",time_check2-time_check1)
    
    counter = 0
    for post in externalPosts:
        # https://stackoverflow.com/questions/2323128/convert-string-in-base64-to-image-and-save-on-filesystem-in-python


        if post["id"].endswith("/"):
            
            post["id"] = "%s"%post["id"][:-1]


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
            if os.path.isdir("Iconicity"+folder_path):
                path = folder_path+file_name
            else:
                os.mkdir("Iconicity"+folder_path)
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

        if post['author']['host'] in team10_host_url or team10_host_url in post['author']['host']:
            print("inside")
            post['author_display_name'] = post['author']['displayName']
        
        if post["comments"] is not None:
            for comment in post["comments"]:
                if "comment_author_name" not in comment:
                    comment["comment_author_name"] = comment["author"]["displayName"]

        if team10_host_url in post["id"]:
            if post["id"].endswith("/"):
                like_url = post["id"] + "likes/"
            else:
                like_url = post["id"] + "/likes/"
            temp = requests.get(like_url, auth=HTTPBasicAuth(team10_name, team10_pass))
            like_list = temp.json()['likes']
            post['like_count'] = len(like_list)
        post['post_id'] = post['id'].split('/')[-1]
        print("post_id",post['post_id'])
        counter +=1
    new_list += externalPosts
    for post in new_list:
        if 'image' in post:
            if post['image'] is not None:
                if team10_host_url not in post['author']['host']:
                    imghost = post['origin'].split('.com')[0]
                    abs_imgpath = imghost + '.com' + post['image']
                    post['image'] = abs_imgpath
    time_check15 = datetime.datetime.now()
    
    print("before_reverse_check",time_check15-time_check1)
    # sort the posts from latest to oldest
    #new_list.reverse()

    # Each page shows 5 posts
    number = 5

    # Paginator
    pagen = Paginator(new_list,5)

    # Current page is 1 by default
    curr_page = 1
    first_page = pagen.page(1).object_list

    print("Iterate the new_list:")

    # Get a list of post id
    post_id_list = []
    
    for post in new_list:
        post_id_list.append(str(post['post_id']))
    
    # print(post_id_list)

    # If the main page is requested after commenting of liking
    # try:
    #     request.session['curr_post_id']
    # except:
    #     pass
    # else:
    #     curr_post_id = request.session['curr_post_id']
    #     if curr_post_id:
    #         curr_post_id = request.session['curr_post_id'].split('/')[-1]
    #         print("curr_post_id:", curr_post_id)
    #         if curr_post_id in post_id_list:
    #             index = post_id_list.index(curr_post_id) + 1
    #             print(index)
    #             curr_page = int(ceil(index / number))
    #             first_page = pagen.page(curr_page).object_list
    #             request.session['curr_post_id'] = None
    
    page_range = pagen.page_range
    curProfile = getUserProfile(request.user)
    context = {
        'pagen':pagen,
        'first_page':first_page,
        'page_range':page_range,
        # 'posts': new_list,
        'UserProfile': curProfile,
        'myself': str(request.user),
        # 'curr_page': curr_page,
    }
    if request.method == "POST":
        page_n = request.POST.get('page_n',None)
        results = list(pagen.page(page_n).object_list)
        return JsonResponse({"results":results})
    time_check3 = datetime.datetime.now()
    print("full_time_check",time_check3-time_check1)
    return render(request, 'Iconicity/main_page.html', context)


def createUserProfileAndInbox(scheme, Display_name, User, Github, host):
    profile = UserProfile(user=User,
                          displayName=Display_name,
                          github=Github,
                          host=host)


    profile.url = str(scheme) + "://" + str(host) + '/author/' + str(profile.id)
    
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
        otherUserProfile = UserProfile.objects.filter(url=user['url']).first()
        if otherUserProfile:
            if currentUser in list(otherUserProfile.get_followers()):
                temp = getPosts(otherUserProfile.user, visibility="FRIENDS") # join the post_list
                post_list += temp
            else:
                # one direct
                # only public
                post_list += getPosts(otherUserProfile.user, visibility="PUBLIC")# join the post_list

    return post_list


def getUserProfile(currentUser):
    # return a UserProfile object for the current login user
    return UserProfile.objects.filter(user=currentUser).first()

def getPosts(user, visibility="PUBLIC"):
    assert visibility in ["PUBLIC","FRIENDS"],"Not valid visibility for posts, check getPosts method in views.py"
    if visibility == "PUBLIC":
        # public can only see your public posts
        print("getPosts(PUBLIC): ", user)
        if type(user) is dict: return list(Post.objects.filter(id = user['id'], visibility="PUBLIC"))
        else: return list(Post.objects.filter(author = user, visibility="PUBLIC"))
    elif visibility == "FRIENDS":
        # friends can see all your posts (public + friends posts)
        print("getPosts(FRIENDS): ", user)
        if type(user) is dict: return list(Post.objects.filter(id = user['id']))
        else: return list(Post.objects.filter(author = user))

def getPost(post):
    return Post.objects.filter(post_id=post.post_id).first()

def getComments():
    return json.loads(core_serializers.serialize("json", list(Comment.objects.filter())))

def delete_post(request):
    pk_raw = request.POST.get('pk')
    try:
        the_user_name = auth_user
        the_user_pass = auth_pass
        if team10_host_url in pk_raw:
            the_user_name = team10_name
            the_user_pass = team10_pass
        post = requests.get(pk_raw, auth=HTTPBasicAuth(the_user_name, the_user_pass)).json()
        post_id = post[0]["post_id"]
        if post_id:
            post = get_object_or_404(Post,pk=post_id)
            print(post_id)
            post.delete()
    except Exception as e:
        the_user_name = auth_user
        the_user_pass = auth_pass
        if team10_host_url in pk_raw:
            the_user_name = team10_name
            the_user_pass = team10_pass
        post = requests.get(pk_raw, auth=HTTPBasicAuth(the_user_name, the_user_pass))
        print(e)
        print('post:', post)
    return redirect("mypost")


class AddPostView(CreateView):
    model = Post
    template= "/Iconicity/post_form.html"
    # fields = "__all__"
    # Post.author = UserProfile.objects.values()['id']
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
            form.save()
            form.origin = (str(request.scheme) + "://"
                                               + str(request.get_host())
                                               + '/author/'
                                               + str(userProfile.pk)
                                               + '/posts/'
                                               + str(form.post_id))
            form.source = form.origin
            form.id = form.source
            form.save()
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
        followee_displayName = request.POST.get('followee_displayName')
        followee_id = request.POST.get('followee_id')
        followee_url = request.POST.get('followee_url')
        # get current user profile
        curProfile = UserProfile.objects.get(user = request.user)
        summary = curProfile.displayName + " wants to follow " + followee_displayName
        # save the new uid into current user's follow attribute:
        try: # local
            followee_profile = UserProfile.objects.get(id = followee_id)
            # create a new friend request locally
            actor = GETProfileSerializer(curProfile).data
            object = GETProfileSerializer(followee_profile).data
            curProfile.add_follow(object) # add the followee to current profile follow
            newFrdRequest = FriendRequest(type = 'follow', summary = summary, actor = actor, object = object)
            # send the friend request to the local inbox:
            newFrdRequest = FriendRequestSerializer(newFrdRequest).data
            cur_inbox = Inbox.objects.get(author=followee_url)
            cur_inbox.items.append(newFrdRequest)
            cur_inbox.save()
        except Exception as e: # external
            # cannot get the profile with followee_id locally
            print("Not local")
            # create a new friend request with the receiver the (external) followee_id
            actor = GETProfileSerializer(curProfile).data # prepare to send
            object_obj = UserProfile(type = 'follow', id = followee_id, displayName = followee_displayName,
                github = followee_github, host = followee_host, url = followee_url)
            object = GETProfileSerializer(object_obj).data
            curProfile.add_follow(object) # add the followee to current profile follow
            # construct the new friend request:
            newFrdRequest = FriendRequest(type = "follow", summary = summary, actor = actor, object = object)
            # serialize the new friend request:
            #frd_request_serialized = FriendRequestSerializer(newFrdRequest).data
            frd_request_serialized = FriendRequestSerializer(newFrdRequest).data
            # API from the other server
            full_followee_url = ''
            if followee_id.startswith('http'): full_followee_url = followee_id
            else: full_followee_url = str(request.scheme) + "://" + followee_id
            # should send to inbox:
            if full_followee_url[-1] == '/': full_followee_url += "inbox/"
            else: full_followee_url += '/inbox/'
            # post the friend request to the external server's inbox
            print("this is the full followee_url: ", full_followee_url)
            # send the requests:

            '''
            post_data = requests.post(full_followee_url, data={"obj":json.dumps(frd_request_serialized)},
                auth=HTTPBasicAuth(auth_user, auth_pass))
            '''

            post_data = requests.post(full_followee_url, json = frd_request_serialized,
                auth=HTTPBasicAuth(auth_user, auth_pass))
            print("data responded: ", post_data)
        curProfile.save()
        # stay on the same page
        return redirect(request.META.get('HTTP_REFERER'))
    return redirect('public')

# by Shway, the follow function, to add someone to your follow list:
def unfollow_someone(request):
    if request.method == 'POST':
        followee_id = request.POST.get('followee_id')
        curProfile = UserProfile.objects.get(user = request.user)
        # remove the uid from current user's follow:
        print(followee_id)
        curProfile.remove_follow_by_id(followee_id)
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
        followee_displayName = request.POST.get('followee_displayName')
        followee_id = request.POST.get('followee_id')
        followee_url = request.POST.get('followee_url')
        # get current user profile
        curProfile = UserProfile.objects.get(user = request.user)
        # save the new uid into current user's follow attribute:
        try: # local
            followee_profile = UserProfile.objects.get(id = followee_id)
            # create a new friend request locally
            object = GETProfileSerializer(followee_profile).data
            curProfile.add_follow(object) # add the followee to current profile follow
        except Exception as e: # external
            # cannot get the profile with followee_id locally
            print("Not local")
            object_obj = UserProfile(type = 'follow', id = followee_id, displayName = followee_displayName,
                github = followee_github, host = followee_host, url = followee_url)
            object = GETProfileSerializer(object_obj).data
            curProfile.add_follow(object) # add the followee to current profile follow
        # enumerate all possibilities of schemes
        full_id = str(curProfile.host) + '/author/' + str(curProfile.id)
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
        for item in cur_inbox.items:
            if item != {} and (item['type'] == 'follow' and (item['actor']['id'] == followee_id or
                item['actor']['id'] == followee_url)):
                cur_inbox.items.remove(item)
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
    full_id = str(profile.host) + '/author/' + str(profile.id)
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
    inbox_size = len(cur_inbox.items)
    print("inbox_view cur_inbox: ", cur_inbox.items)
    content = cur_inbox.items

    is_all_empty = False
    if inbox_size == 0: is_all_empty = True
    # put information to the context
    context = {
        'is_all_empty': is_all_empty,
        'inbox': content}
    return render(request, 'Iconicity/inbox.html', context)

# by Shway, to remove a follow notification from the inbox
def remove_inbox_follow(request):
    if request.method == 'POST':
        # receive data from front-end
        followee_host = request.POST.get('followee_host')
        followee_github = request.POST.get('followee_github')
        followee_displayName = request.POST.get('followee_displayName')
        followee_id = request.POST.get('followee_id')
        followee_url = request.POST.get('followee_url')
        # save the new uid into current user's follow attribute:
        curProfile = getUserProfile(request.user)
        print("inbox_view current profile: ", curProfile)
        # enumerate all possibilities of schemes
        full_id = str(curProfile.host) + '/author/' + str(curProfile.id)
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
        for item in cur_inbox.items:
            if item != {} and (item['type'] == 'follow' and (item['actor']['id'] == followee_id or
                item['actor']['id'] == followee_url)):
                cur_inbox.items.remove(item)
        cur_inbox.save()
        curProfile.save()
        # stay on the same page
        return redirect(request.META.get('HTTP_REFERER'))
    return redirect('public')

# Shway, the private post view page
class SendPrivatePostView(CreateView):
    model = Post
    template= "/Iconicity/private_post_form.html"
    def post(self, request):
        # receive data from front-end
        receiver_host = request.GET.get('receiver_host')
        receiver_github = request.GET.get('receiver_github')
        receiver_displayName = request.GET.get('receiver_displayName')
        receiver_id = request.GET.get('receiver_id')
        receiver_url = request.GET.get('receiver_url')
        form = PostsCreateForm(request.POST, request.FILES)
        if form.is_valid():
            form = form.save(commit=False)
            form.author = request.user
            userProfile = UserProfile.objects.get(user=request.user)
            form.origin = (str(request.scheme) + "://"
                                               + str(request.get_host())
                                               + '/author/'
                                               + str(userProfile.pk)
                                               + '/posts/'
                                               + str(form.post_id))
            form.source = form.origin
            form.id = form.source
            # to get rid of the UUID and replace with its string form:
            form.post_id = str(form.post_id)
            # get the serialized private post:
            serializedPost = PostSerializer(form).data

            try:
                # test to see if local:
                UserProfile.objects.get(id = receiver_id)
                # send the private post to the local inbox:
                receiver_inbox = Inbox.objects.get(author = receiver_url)
                receiver_inbox.items.append(serializedPost)
                receiver_inbox.save()
            except Exception as e:
                # cannot get the profile with followee_id locally
                print("Not local")
                # API from the other server
                full_receiver_url = ''
                if receiver_id.startswith('http'): full_receiver_url = receiver_id
                else: full_receiver_url = str(request.scheme) + "://" + receiver_id
                # should send to inbox:
                if full_receiver_url[-1] == '/': full_receiver_url += "inbox/"
                else: full_receiver_url += '/inbox/'
                # send the private post to the external server's inbox
                post_data = requests.post(full_receiver_url, json = serializedPost,
                    auth = HTTPBasicAuth(auth_user, auth_pass))
                print("data responded: ", post_data)
            return redirect('all_profiles')

        else:
            form = PostsCreateForm(request.POST)
            context = {'form': form, 'receiver_host': receiver_host, 'receiver_github': receiver_github,
            'receiver_displayName': receiver_displayName, 'receiver_id': receiver_id, 'receiver_url': receiver_url}
            return render(request, template, context)

    def get(self, request):
        # receive data from front-end
        receiver_host = request.GET.get('receiver_host')
        receiver_github = request.GET.get('receiver_github')
        receiver_displayName = request.GET.get('receiver_displayName')
        receiver_id = request.GET.get('receiver_id')
        receiver_url = request.GET.get('receiver_url')
        # make the context object
        context = {'form': PostsCreateForm, 'receiver_host': receiver_host, 'receiver_github': receiver_github,
        'receiver_displayName': receiver_displayName, 'receiver_id': receiver_id, 'receiver_url': receiver_url}
        # get current user profile
        curProfile = UserProfile.objects.get(user = request.user)
        return render(request, 'Iconicity/private_post_form.html', context)

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
        my_profile = UserProfile.objects.get(user = user) # type is a query set!
        follow_list_processed = set()
        # whom I am following locally
        follow_list = my_profile.get_followers()

        for i in follow_list:
            follow_list_processed.add(i['url'])

        print("this is the follow list: ", follow_list_processed)
        context['follows'] = follow_list_processed

        # if there are no profiles other than the current user:
        context['is_empty'] = False # initially not empty
        if len(self.get_queryset()) == 0:
            context['is_empty'] = True
        return context

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
    like_obj.summary = "%s liked your post."%(current_user_profile.displayName)
    like_obj.author = GETProfileSerializer(current_user_profile).data

    like_obj.object = pk_raw
    the_user_name = auth_user
    the_user_pass = auth_pass
    
    if team10_host_url in pk_raw:
        the_user_name = team10_name
        the_user_pass = team10_pass
    print("team10",team10_host_url)
    print("pk_raw",pk_raw)
    print(the_user_name)
    print(the_user_pass)
    post_info = requests.get(pk_raw, auth=HTTPBasicAuth(the_user_name, the_user_pass)).json()

    if isinstance(post_info, list) or isinstance(post_info, tuple):
        post_info = post_info[0]
    post_author_url = post_info['author']['url']
    full_inbox_url = post_author_url
    if post_author_url[-1] != "/":
        full_inbox_url += "/"
    full_inbox_url += 'inbox/'
    print("inbox url",full_inbox_url)


    print("like object",like_obj.object)
    
    like_serializer = LikeSerializer(like_obj).data
    the_user_name = auth_user
    the_user_pass = auth_pass
    if team10_host_url in pk_raw:
        the_user_name = team10_name
        the_user_pass = team10_pass
    if team10_host_url not in pk_raw:
        print(json.dumps(like_serializer))
        response = requests.post(full_inbox_url,
                                json = like_serializer, 
                                auth=HTTPBasicAuth(the_user_name, the_user_pass))
    else:
        print("team10")
        print(the_user_name,the_user_pass)
        print(json.dumps(like_serializer))
        print(full_inbox_url)
        temp12 = json.loads(json.dumps(like_serializer))
        temp12['type'] = 'Like'
        print("sendout",temp12)
        response = requests.post(full_inbox_url,
                                json = like_serializer, 
                                auth=HTTPBasicAuth(the_user_name, the_user_pass))
        print("response",response)
        
    # author/{AUTHOR_ID}/posts/{POST_ID}/comments/ endpoint

    # print("like inbox response",response)
    # FROM: https://stackoverflow.com/questions/49721830/django-redirect-with-additional-parameters
    request.session['curr_post_id'] = pk_raw
    print(pk_raw)
    # END FROM
    return redirect(redirect_path)



def repost(request):
    # should pass back the post from the frontend
    pk_raw = request.POST.get('pk')
    the_user_name = auth_user
    the_user_pass = auth_pass
    if team10_host_url in pk_raw:
        the_user_name = team10_name
        the_user_pass = team10_pass
    print("repost pk_raw: ", pk_raw)
    get_json_response = requests.get(pk_raw, auth=HTTPBasicAuth(the_user_name, the_user_pass))
    temp = get_json_response.text
    # modified by Shway to fit team 10:
    post = None
    if team10_host_url in pk_raw: post = json.loads(temp)
    else: post = json.loads(temp)[0]
    print("response_dict",post)
    ordinary_dict = {'title': post['title'], 'content': post['content'], 'visibility':'PUBLIC', 'contentType': post['contentType']}
    query_dict = QueryDict('', mutable=True)
    query_dict.update(ordinary_dict)
    post_form = PostsCreateForm(query_dict)
    img_path = None
    if team10_host_url not in pk_raw:
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
        post_form.id = post['id']
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
        post_form.id = post_form.source
        post_form.save()
        print("post_form image", post_form.image)

    else:
        print(post_form.errors)
    return redirect('public')

def repost_to_friend(request):
    # should pass back the post from the frontend
    pk_raw = request.POST.get('pk')
    print(pk_raw)
    the_user_name = auth_user
    the_user_pass = auth_pass
    if team10_host_url in pk_raw:
        the_user_name = team10_name
        the_user_pass = team10_pass
    get_json_response = requests.get(pk_raw, auth=HTTPBasicAuth(the_user_name, the_user_pass))
    print(json.loads(get_json_response.text))

    # modified here by Shway
    post = None
    if team10_host_url in pk_raw: post = json.loads(get_json_response.text)
    else: post = json.loads(get_json_response.text)[0]

    ordinary_dict = {'title': post['title'], 'content': post['content'], 'visibility':'FRIENDS', 'contentType': post['contentType']}
    query_dict = QueryDict('', mutable=True)
    query_dict.update(ordinary_dict)
    post_form = PostsCreateForm(query_dict)
    img_path = None
    if team10_host_url not in pk_raw:
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
        post_form.id = post['id']
        userProfile = UserProfile.objects.get(user=request.user)
        post_form.source = (str(request.scheme) + "://"
                                            + str(request.get_host())
                                            + '/author/'
                                            + str(userProfile.pk)
                                            + '/posts/'
                                            + str(post_form.post_id))
        post_form.id = post_form.source
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


def mypost(request):

    if request.user.is_anonymous:
        return render(request,
                      'Iconicity/login.html',
                      { 'form':  AuthenticationForm })
    # get all the posts posted by the current user
    postList = getPosts(request.user, visibility="FRIENDS")
    new_list = []
    new_list += PostSerializer(postList, many=True).data
    # print("mypost: ", new_list)
    for post in new_list:
        if 'image' in post:
            if post['image'] is not None:
                if "socialdistributionproject" not in post['author']['host']:
                    imghost = post['origin'].split('.com')[0]
                    abs_imgpath = imghost + '.com' + post['image']
                    post['image'] = abs_imgpath

    number = 5
    pagen = Paginator(new_list,5)
    curr_page = 1
    first_page = pagen.page(1).object_list
    page_range = pagen.page_range
    
    github_username = getUserProfile(request.user).github.split("/")[-1]
    post_id_list = []
    for post in new_list:
        post_id_list.append(str(post['post_id']))

    # try:
    #     request.session['curr_post_id']
    # except:
    #     pass
    # else:
    #     curr_post_id = request.session['curr_post_id']
    #     if curr_post_id:
    #         curr_post_id = request.session['curr_post_id'].split('/')[-1]
    #         print("curr_post_id:", curr_post_id)
    #         if curr_post_id in post_id_list:
    #             index = post_id_list.index(curr_post_id) + 1
    #             print(index)
    #             curr_page = int(ceil(index / number))
    #             first_page = pagen.page(curr_page).object_list
    #             request.session['curr_post_id'] = None

    context = {
        # 'posts': new_list,
        'pagen':pagen,
        'first_page':first_page,
        'page_range':page_range,
        'UserProfile': getUserProfile(request.user),
        'github_username': github_username,
        # 'curr_page': curr_page,
    }
    if request.method == "POST":
        page_n = request.POST.get('page_n',None)
        results = list(pagen.page(page_n).object_list)
        return JsonResponse({"results":results})
    return render(request, 'Iconicity/my_post.html', context)

# modified by Shway:
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
        allFollowers = userProfile.get_followers()
        if allFollowers != []:
            # now it should be a list of urls of the external followers
            # should like [url1, url2]

            for user in allFollowers:
                if len(UserProfile.objects.filter(url = user['id'])) == 0: # if external

                    full_url = user['url']
                    if user['url'][-1]=="/":
                        full_url += "posts/"
                    else:
                        full_url += "/posts/"
                    the_user_name = auth_user
                    the_user_pass = auth_pass
                    if team10_host_url in full_url:
                        the_user_name = team10_name
                        the_user_pass = team10_pass
                    temp = requests.get(full_url, auth=HTTPBasicAuth(the_user_name, the_user_pass))

                    responseJsonlist = temp.json()

                    if team10_host_url in full_url:
                        post = responseJsonlist['posts']
                    else:
                        post = responseJsonlist

                    new_one = []
                    for i in post:
                        if i['visibility'] != "PUBLIC":
                            continue
                        else:
                            new_one.append(i)
                    post_list += new_one
    
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
            full_url = host_url + "posts/"
        else:
            full_url = host_url + "/posts/"
        the_user_name = auth_user
        the_user_pass = auth_pass
        if team10_host_url in host_url:
            the_user_name = team10_name
            the_user_pass = team10_pass
        print("getAllExternalPublicPosts full_url: ", full_url)
        temp = requests.get(full_url, auth=HTTPBasicAuth(the_user_name, the_user_pass))
        if team10_host_url in host_url:
            posts = temp.json()['posts']
        else:
            posts = temp.json()
        print("getAllExternalPublicPosts posts: ", posts)
        new_one = []
        for i in posts:
            if i['visibility'] != "PUBLIC":
                continue
            else:
                new_one.append(i)

        allPosts += new_one
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
        if team10_host_url in host_url:
            the_user_name = team10_name
            the_user_pass = team10_pass
            full_url += "s/"
        temp = requests.get(full_url, auth=HTTPBasicAuth(the_user_name, the_user_pass))
        if temp.status_code < 400:
            if team10_host_url in host_url:
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
        userProfile = UserProfile.objects.get(pk = author_id)
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
    print(getAllFollowExternalAuthorPosts(request.user))
    for post in new_list:
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
        if post['author']['host'] in team10_host_url or team10_host_url in post['author']['host']:
            print("inside")
            post['author_display_name'] = post['author']['displayName']
                
        if post["comments"] is not None:
            for comment in post["comments"]:
                if "comment_author_name" not in comment:
                    comment["comment_author_name"] = comment["author"]["displayName"]

        if team10_host_url in post["id"]:
            if post["id"].endswith("/"):
                like_url = post["id"] + "likes/"
            else:
                like_url = post["id"] + "/likes/"
            print("before getting team 10 likes")
            temp = requests.get(like_url, auth = HTTPBasicAuth(team10_name, team10_pass))
            print("after getting team 10 likes")
            like_list = temp.json()['likes']
            post['like_count'] = len(like_list)

    for post in new_list:
        if 'image' in post:
            if post['image'] is not None:
                if "socialdistributionproject" not in post['author']['host']:
                    imghost = post['origin'].split('.com')[0]
                    abs_imgpath = imghost + '.com' + post['image']
                    post['image'] = abs_imgpath

    # sort the posts from latest to oldest
    # new_list.reverse()

    # Each page shows 5 posts
    number = 5

    # Paginator
    pagen = Paginator(new_list,5)

    # Current page is 1 by default
    curr_page = 1
    first_page = pagen.page(1).object_list

    print("Iterate the new_list:")

    # Get a list of post id
    post_id_list = []
    for post in new_list:
        if team10_host_url not in post['id']:
            post_id_list.append(str(post['post_id']))
    
    # print(post_id_list)

    # If the main page is requested after commenting of liking
    # try:
    #     request.session['curr_post_id']
    # except:
    #     pass
    # else:
    #     curr_post_id = request.session['curr_post_id']
    #     if curr_post_id:
    #         curr_post_id = request.session['curr_post_id'].split('/')[-1]
    #         print("curr_post_id:", curr_post_id)
    #         if curr_post_id in post_id_list:
    #             index = post_id_list.index(curr_post_id) + 1
    #             print(index)
    #             curr_page = int(ceil(index / number))
    #             first_page = pagen.page(curr_page).object_list
    #             request.session['curr_post_id'] = None

    page_range = pagen.page_range
    context = {
        'pagen':pagen,
        'first_page':first_page,
        'page_range':page_range,
        # 'posts': new_list,
        'UserProfile': userProfile,
        'myself': str(request.user),
        # 'curr_page': curr_page,
    }
    if request.method == "POST":
        page_n = request.POST.get('page_n',None)
        results = list(pagen.page(page_n).object_list)
        return JsonResponse({"results":results})
    return render(request,'Iconicity/follow.html', context)

def getUserFriend(currentUser):
    userProfile = getUserProfile(currentUser)
    friendList = []
    # get all local followers of our user which our user also follows
    allFollowedAuthors = list(userProfile.get_followers())
    for user in allFollowedAuthors:
        # check whether they are friends.
        # means a two-direct-follow
        if len(UserProfile.objects.filter(url=user['url'])) != 0:
            otherUserProfile = UserProfile.objects.filter(url=user['url']).first()
            friends = otherUserProfile.get_followers()
            for userInfo in friends:
                if userProfile.url == userInfo['url']:
                    print("getUserFriend: ", otherUserProfile.user)
                    friendList.append(otherUserProfile.user)
                    break
    return friendList

# modified by Shway
def getExternalUserFriends(currentUser):
    userProfile = getUserProfile(currentUser)
    friendUrlList = []
    # now check external followers. check whether they are bi-direction.
    allFollowers = list(userProfile.get_followers()) # a list of followers

    for user in allFollowers:
        if len(UserProfile.objects.filter(url = user['url'])) == 0: # if external
            full_url = user['url']
            if user['url'][-1] == "/":
                full_url += "followers/"
            else:
                full_url += "/followers/"
            # now check whether you are also his/hers followee.
            the_user_name = auth_user
            the_user_pass = auth_pass
            if team10_host_url in full_url:
                the_user_name = team10_name
                the_user_pass = team10_pass
            print('url: ', full_url)
            print('user name: ', the_user_name)
            try:
                raw = requests.get(full_url, auth=HTTPBasicAuth(the_user_name, the_user_pass))

                print('raw: ', raw)
                friends = raw.json()
            except Exception as e:
                print("error in other servers' API")
            else:
                for userInfo in friends['items']:
                    if userProfile.url == userInfo['url']:
                        friendUrlList.append(user['url'])
                        break
    print("getExternalUserFriends: ", friendUrlList)
    return friendUrlList

def friends(request):
    if request.user.is_anonymous:
        return render(request, 'Iconicity/login.html', { 'form':  AuthenticationForm })
    # get all the posts posted by the current user
    postList = []
    friends_test = getUserFriend(request.user)
    print("friends friends test: ", friends_test)
    tmp_list = []
    for user in friends_test:
        tmp_list += getPosts(user, visibility="FRIENDS")

    new_list = PostSerializer(tmp_list, many=True).data
    postList += new_list
    externalFriends = getExternalUserFriends(request.user)
    print("friends externalUserFriends: ", externalFriends)
    if externalFriends and externalFriends !=[]:
        for each_url in externalFriends:
            full_url = each_url

            if each_url[-1] == "/":
                full_url += "friendposts/"
            else:
                full_url += "/friendposts/"

            the_user_name = auth_user
            the_user_pass = auth_pass
            if team10_host_url in each_url:
                the_user_name = team10_name
                the_user_pass = team10_pass
            posts = requests.get(full_url, auth=HTTPBasicAuth(auth_user, auth_pass)).json()
            print("friends posts: ", posts)
            postList += posts
    
    for post in postList:
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
        if post['author']['host'] in team10_host_url or team10_host_url in post['author']['host']:
            print("inside")
            post['author_display_name'] = post['author']['displayName']
                
        if post["comments"] is not None:
            for comment in post["comments"]:
                if "comment_author_name" not in comment:
                    comment["comment_author_name"] = comment["author"]["displayName"]

        if team10_host_url in post["id"]:
            if post["id"].endswith("/"):
                like_url = post["id"] + "likes/"
            else:
                like_url = post["id"] + "/likes/"
            temp = requests.get(like_url, auth=HTTPBasicAuth(team10_name, team10_pass))
            like_list = temp.json()['likes']
            post['like_count'] = len(like_list)

    for post in postList:
        if post['image'] is not None:
            if "socialdistributionproject" not in post['author']['host']:
                imghost = post['origin'].split('.com')[0]
                abs_imgpath = imghost + '.com' + post['image']
                post['image'] = abs_imgpath
    userProfile = getUserProfile(request.user)

    # sort the posts from latest to oldest
    postList.reverse()

    # Each page shows 5 posts
    number = 5

    # Paginator
    pagen = Paginator(postList,5)

    # Current page is 1 by default
    curr_page = 1
    first_page = pagen.page(1).object_list

    print("Iterate the postList:")

    # Get a list of post id
    post_id_list = []
    for post in postList:
        post_id_list.append(str(post['post_id']))
    
    # print(post_id_list)

    # If the main page is requested after commenting of liking
    try:
        request.session['curr_post_id']
    except:
        pass
    else:
        curr_post_id = request.session['curr_post_id']
        if curr_post_id:
            curr_post_id = request.session['curr_post_id'].split('/')[-1]
            print("curr_post_id:", curr_post_id)
            if curr_post_id in post_id_list:
                index = post_id_list.index(curr_post_id) + 1
                print(index)
                curr_page = int(ceil(index / number))
                first_page = pagen.page(curr_page).object_list
                request.session['curr_post_id'] = None
    print("friends first_page: ", first_page)
    page_range = pagen.page_range
    context = {
        # 'posts': postList,
        'pagen':pagen,
        'first_page':first_page,
        'page_range':page_range,
        'UserProfile': userProfile,
        'myself': str(userProfile.url),
        # 'curr_page': curr_page,
    }
    if request.method == "POST":
        page_n = request.POST.get('page_n',None)
        results = list(pagen.page(page_n).object_list)
        return JsonResponse({"results":results})
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
        data_json = request.data
        print("data_json", data_json)
        local_author_profile = UserProfile.objects.get(pk=author_id)
        try:
            inbox_obj = Inbox.objects.get(author=local_author_profile.url)
            print("inbox_obj: ", inbox_obj)
            if data_json['type'] == "like":
                print("likelikelikelikelikelikelikelikelikelikelikelikelikelikelike")
                # if the type is “like” then add that like to the author’s inbox
                post_url = data_json["object"]
                print("url",post_url)
                post_id = [i for i in post_url.split('/') if i][-1]
                print("id",post_id)
                post_obj = Post.objects.get(pk=post_id)
                
                if request.META['HTTP_HOST'] in data_json['author']['url']:
                    # means it's local like author              
                    # means add this man's id to the like list.
                    if post_obj.external_likes == {}:
                        post_obj.external_likes['urls'] = []
                    external_author_url = data_json["author"]["url"]
                    post_obj.external_likes['urls'].append(external_author_url)
                    print("external",post_obj.external_likes['urls'])
                    print("new like user",local_author_profile.user)
                    #post_obj.like.add(local_author_profile.user)
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
                    print("here2", post_obj)
                    return Response(InboxSerializer(inbox_obj).data,status=201)
                else:
                    # means it's a external author
                    external_author_url = data_json["author"]["url"]
                    if post_obj.external_likes == {}:
                        post_obj.external_likes['urls'] = []
                    if post_obj.external_likes == {"urls":[]} or data_json["author"]["url"] not in post_obj.external_likes['urls']:
                        # means add this man's id to the external like list.
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
                print("postpostpostpostpostpostpostpostpostpostpostpostpostpostpostpostpost")
                # if the type is “post” then add that post to the author’s inbox
                # add a post to the author_id's inbox
                inbox_obj.items.append(data_json)
                inbox_obj.save()
                return Response(InboxSerializer(inbox_obj).data,status=200)

            elif data_json['type'] == "follow":
                print("followfollowfollowfollowfollowfollowfollowfollowfollowfollowfollowfollow")
                # need to load the actor and object into objects:
                inbox_obj.items.append(data_json)
                inbox_obj.save()
                return Response(InboxSerializer(inbox_obj).data,status=200)

            elif data_json['type'] == 'comment':
                print("commentcommentcommentcommentcommentcommentcommentcommentcommentcomment")
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
        print("AllPostsByAuthor: ", author_id)
        authorProfile = UserProfile.objects.get(pk=author_id)
        posts = Post.objects.filter(author=authorProfile.user).all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

class ExternalFollowersByAuthor(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, author_id):
        print("ExternalFollowersByAuthor: ", author_id)
        authorProfile = UserProfile.objects.get(pk=author_id)
        return Response(FollowersSerializer(authorProfile).data)

class FriendPostsByAuthor(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, author_id):
        authorProfile = UserProfile.objects.get(pk = author_id)
        friendPosts = Post.objects.filter(author = authorProfile.user)
        print("FriendPostsByAuthor friendPosts: ", friendPosts)
        return Response(PostSerializer(friendPosts, many = True).data)

def post_comments(request):
    ppid = request.POST.get('ppid')
    #if ppid is None: ppid = request.POST.get('pk')
    if ppid:
        
        context = {'form123': CommentsCreateForm(), "url": ppid}
        return render(request, 'Iconicity/comment_form.html', context)


    pk_raw = request.POST.get('pk')
    for key, value in request.POST.items():
        print('%s: %s' % (key, value) ) 
    print("ppid: ", ppid)

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
                    comment_obj = Comment()
                    comment_obj.comment = form.cleaned_data['comment']
                    comment_obj.author = author_json
                    comment_obj.post = pk_raw
                    # modified here by Shway:
                    # comment_obj.contentType = 'text/markdown'
                    comment_serializer = CommentSerializer(comment_obj).data
                    #comment_serializer['post_id'] = comment_serializer['id']
                    print("post_comments comment_serializer: ", comment_serializer)
                    the_user_name = auth_user
                    the_user_pass = auth_pass
                    if team10_host_url in pk_raw:
                        the_user_name = team10_name
                        the_user_pass = team10_pass
                    print('post_comments pk_raw: ', pk_raw)
                    if pk_raw[-1] == "/":
                        response = requests.post(pk_raw+"comments/",
                            json = comment_serializer, 
                            auth = HTTPBasicAuth(the_user_name, the_user_pass))
                    else:
                        response = requests.post(pk_raw+"/comments/",
                            json = comment_serializer, 
                            auth = HTTPBasicAuth(the_user_name, the_user_pass))

                    print("response",response)

                    the_user_name = auth_user
                    the_user_pass = auth_pass
                    if team10_host_url in pk_raw:
                        the_user_name = team10_name
                        the_user_pass = team10_pass
                    post_info = requests.get(pk_raw,
                                        auth=HTTPBasicAuth(the_user_name, the_user_pass)).json()
                    if isinstance(post_info,list) or isinstance(post_info,tuple):
                        post_info = post_info[0]
                    post_author_url = post_info['author']['url']
                    full_inbox_url = post_author_url
                    if post_author_url[-1] != "/":
                        full_inbox_url += "/"
                    full_inbox_url += 'inbox/'
                    
                    
                    comment_obj = Comment()
                    comment_obj.comment = form.cleaned_data['comment']
                    comment_obj.author = author_json
                    comment_obj.post = pk_raw
                    # modified here by Shway:
                    # comment_obj.contentType = 'text/markdown'
                    comment_serializer = CommentSerializer(comment_obj).data
                    the_user_name = auth_user
                    the_user_pass = auth_pass
                    if team10_host_url in pk_raw:
                        the_user_name = team10_name
                        the_user_pass = team10_pass
 
                    response = requests.post(full_inbox_url,
                            json = comment_serializer, 
                            auth=HTTPBasicAuth(the_user_name, the_user_pass))

                    # FROM: https://stackoverflow.com/questions/49721830/django-redirect-with-additional-parameters
                    request.session['curr_post_id'] = pk_raw
                    # END FROM
                    print("request.session: ", request.session)
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
                    full_inbox_url += 'inbox/'
                    print(author_json)
                    print(type(author_json))
                    comment_obj = Comment()
                    comment_obj.comment = form.cleaned_data['comment']
                    comment_obj.author = author_json
                    comment_obj.post = pk_raw
                    comment_serializer = CommentSerializer(comment_obj).data
                    print(comment_serializer)
                    the_user_name = auth_user
                    the_user_pass = auth_pass
                    if team10_host_url in pk_raw:
                        the_user_name = team10_name
                        the_user_pass = team10_pass
                    if team10_host_url not in pk_raw:
                        response = requests.post(full_inbox_url,
                                json = comment_serializer, 
                                auth = HTTPBasicAuth(the_user_name, the_user_pass))
                    else:
                        response = requests.post(full_inbox_url,
                                json = comment_serializer, 
                                auth = HTTPBasicAuth(the_user_name, the_user_pass))

                    # FROM: https://stackoverflow.com/questions/49721830/django-redirect-with-additional-parameters
                    request.session['curr_post_id'] = pk_raw
                    # END FROM
                    print("request.session: ", request.session.items())
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
        # modified here by Shway
        comment.author = request.data['author']
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
