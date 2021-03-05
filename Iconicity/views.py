from django.shortcuts import render, resolve_url, reverse, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from .models import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, RetrieveAPIView
from django.core import serializers as core_serializers
import json
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render, redirect
from .forms import *
from django.contrib.auth.decorators import login_required
from django.views import View
from django.views.generic import ListView, DeleteView
from django.contrib.auth import logout
from django.http.request import HttpRequest
from django.views.generic import CreateView
from django.core.serializers.json import DjangoJSONEncoder
from django.urls import reverse
from django.db.models import Q
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.http import QueryDict
from .serializers import *
from urllib.request import urlopen
import requests
import collections
from rest_framework.renderers import JSONRenderer

#https://thecodinginterface.com/blog/django-auth-part1/

def getAuthor(id):
    author_profile = core_serializers.serialize("json", UserProfile.objects.filter(uid=id))
    jsonload = json.loads(author_profile)[0]
    raw_id = jsonload['pk']
    jsonload = jsonload['fields']
    temp = str(jsonload['host']) + '/author/' + str(raw_id)
    jsonload['user_id'] = str(jsonload['host']) + '/author/' + str(raw_id)
    jsonload['url'] = jsonload['user_id']
    return Response(jsonload)


# not in use at this moment
class AuthorProfile(APIView):
    # get a author's profile by its id
    def get(self, request, id):
        author_profile = core_serializers.serialize("json", UserProfile.objects.filter(uid=id))
        jsonload = json.loads(author_profile)[0]
        raw_id = jsonload['pk']
        jsonload = jsonload['fields']
        temp = str(jsonload['host']) + '/author/' + str(raw_id)
        jsonload['user_id'] = str(jsonload['host']) + '/author/' + str(raw_id)
        jsonload['url'] = jsonload['user_id']
        return Response(jsonload)

# get all followers this author has
# id is the author's id
def getFollowers(id):
    authorfollow = getAuthor(id).data['follow'] # return followe list of this author
    # now it should be a list of urls.


    print(type(authorfollow))
    print(authorfollow)
    #print(json.loads(authorfollow))

def logout_view(request):
    # in use, support log out
    # http://www.learningaboutelectronics.com/Articles/How-to-create-a-logout-button-in-Django.php
    if request.method == 'POST':
        logout(request)
        return redirect(reverse('login'))


class LoginView(View):
    def get(self, request):
        if not request.user.is_anonymous:
            print("go to main")
            print(request.user)
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


"""TODO:
Question asked by Qianxi:
for the following two lines:

user = authenticate(username=username, password=raw_password)
login(request, user)

we need exception handling.

Finish it and delete this comment block
"""
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
            createUserProfile(scheme, username, User, Github, host)

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
    # get all the posts posted by the current user
    #print("request.host",request.META['HTTP_HOST'])
    postList = list(Post.objects.filter(visibility='PUBLIC'))
    # print(postList)
    new_list, comments = createJsonFromProfile(postList)
    externalPosts = getAllExternalPublicPosts()
    for eachPost in externalPosts:
        eachPost['display_name'] = eachPost['author']['display_name']
    new_list += externalPosts

    #externalPostList = getAllFollowExternalAuthorPosts(request.user)
    #print("extrenal",externalPostList)
    #new_list += externalPostList
    #print(new_list)

    """ Note:
    each json object in externalPostList is different from
    each one in new_list!!!!!!!!!!!!!!!!

    I'll change this by March 5 morning. All posts in our server and
    outside our server will all use the same json format

    Qianxi



    """
    context = {

        'posts': new_list,
        'comments': comments,
        'UserProfile': getUserProfile(request.user),
    }

    return render(request, 'Iconicity/main_page.html', context)


def createUserProfile(scheme, Display_name, User, Github, host):
    profile = UserProfile(user=User,
                          display_name=Display_name,
                          github=Github,
                          host=host)


    profile.url = str(scheme) + "://" + str(host) + '/author/' + str(profile.uid)
    profile.save()



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
                print("they are friends")
                temp = getPosts(user, visibility="FRIENDS") # join the post_list
                post_list += temp
            else:
                # one direct
                # only public
                post_list += getPosts(user, visibility="PUBLIC")# join the post_list

    print("current post_List")
    print(post_list)
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
    template = "/Iconicity/my_post.html"
    post_id = request.POST.get('pk')
    if post_id:
        post = get_object_or_404(Post,pk=request.POST.get('pk'))
        print(post_id)
        post.delete()

    return redirect("my_post")


class AddPostView(CreateView):
    model = Post
    template= "/Iconicity/post_form.html"
    # fields = "__all__"
    # Post.author = UserProfile.objects.values()['uid']
    def post(self, request):
        print("posting")
        template = "Iconicity/post_form.html"
        form = PostsCreateForm(request.POST, request.FILES,)
        print(request.FILES)
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
        followee_uid = request.POST.get('followee_uid')
        #c012db46-259f-40aa-b6a6-56d3b83fa705
        curProfile = UserProfile.objects.get(user = request.user)
        # save the new uid into current user's follow:
        # for external uses:
        try:
            followee_profile = UserProfile.objects.get(uid = followee_uid)
        except Exception as e:
            print(e)
            print("Not local")
            # if not local:
            #print("request.host",request.META['HTTP_HOST'])
            full_followee_url = followee_profile.host

            if not followee_profile.host.startswith(str(request.scheme)):
                full_followee_url = str(request.scheme) + "://"  + str(followee_profile.host)

            if followee_profile.host[-1] == "/":
                full_followee_url = full_followee_url + "author/" + str(followee_profile.pk)
            else:
                full_followee_url = full_followee_url + "/author/" + str(followee_profile.pk)


            if curProfile.externalFollows == {}:
                curProfile.externalFollows['urls'] = []
            curProfile.externalFollows['urls'].append(full_followee_url)
        else:
            # if local:
            curProfile.follow.add(followee_profile.user)
        curProfile.save()
        # stay on the same page
        return redirect(request.META.get('HTTP_REFERER'))
    return redirect('main')

def unfollow_someone(request):
    if request.method == 'POST':
        followee_uid = request.POST.get('followee_uid')
        curProfile = UserProfile.objects.get(user = request.user)

        try:
            followee_profile = UserProfile.objects.get(uid = followee_uid)
        except Exception as e:
            print(e)
            print("Not local")
            # for external uses:
            full_followee_url = followee_profile.host
            if not followee_profile.host.startswith(str(request.scheme)):
                full_followee_url = str(request.scheme) + "://"  + str(followee_profile.host)

            if followee_profile.host[-1] == "/":
                full_followee_url = full_followee_url + "author/" + str(followee_profile.pk)
            else:
                full_followee_url = full_followee_url + "/author/" + str(followee_profile.pk)

            if full_followee_url in curProfile.externalFollows['urls']:
                curProfile.externalFollows['urls'].remove(full_followee_url)

        else:
            # local user
            # remove the uid from current user's follow:
            if followee_profile.user in curProfile.follow.all():
                curProfile.follow.remove(followee_profile.user)

            
        curProfile.save()
        # stay on the same page
        return redirect(request.META.get('HTTP_REFERER'))
    return redirect('main')

# by Shway, this view below shows the list of received friend requests:
def friend_requests_received_view(request):
    profile = getUserProfile(request.user)
    requests = FriendRequest.objects.friendRequests_received(profile)
    is_empty = False
    if len(requests) == 0: is_empty = True
    # take actor(sender) of each request
    senders = list(map(lambda x: x.actor, requests))
    context = {
        'senders': senders,
        'is_empty': is_empty}
    return render(request, 'Iconicity/frdRequests.html', context)

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


        '''

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
        print(sender.externalFollows['urls'])'''
        # change the status of the friend request to accepted:
        sender.save()
        receiver.save()
        friend_request = get_object_or_404(FriendRequest, actor = sender, object_author = receiver)
        if friend_request.status == 'sent':
            friend_request.status = 'accepted'
            friend_request.save()
        # stay on the same page
        return redirect(request.META.get('HTTP_REFERER'))
    return redirect('main')

# by Shway, reject friend request function view:
def reject_friend_request(request):
    if request.method == 'POST':
        uid = request.POST.get('reject_uid')
        sender = UserProfile.objects.get(uid = uid)
        receiver = UserProfile.objects.get(user = request.user)
        friend_request = get_object_or_404(FriendRequest, actor = sender, object_author = receiver)
        friend_request.delete()
        # stay on the same page
        return redirect(request.META.get('HTTP_REFERER'))
    return redirect('main')

# by Shway, this view below shows the list of profiles of all those availble to follow
# or to be friend with:
def avail_userProfile_list_view(request):
    user = request.user
    profiles = UserProfile.objects.get_all_available_profiles(user)
    context = {'profiles': profiles}
    return render(request, 'Iconicity/avail_profile_list.html', context)

# by Shway, this view below shows the list of all profiles except for the current user
class UserProfileListView(ListView):
    model = UserProfile
    template_name = 'Iconicity/all_profile_list.html'
    context_object_name = 'profiles'
    # override:
    def get_queryset(self):
        # get all profiles except for current user
        return UserProfile.objects.get_all_profiles(exception = self.request.user)
    # override:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = User.objects.get(username__iexact = self.request.user)
        my_profile = UserProfile.objects.get(user = user)
        # whom I want to follow
        pending_requests = FriendRequest.objects.filter(Q(actor = my_profile) & Q(status = 'sent'))
        # whom wants to follow me
        inbox_requests = FriendRequest.objects.filter(Q(object_author = my_profile) & Q(status = 'sent'))
        # friend relations requests
        accepted_requests = FriendRequest.objects.filter(
            (Q(object_author = my_profile) | Q(actor = my_profile)) & Q(status = 'accepted'))
        # listify the above two results:
        follow_list = set()
        pending_requests_list = set()
        inbox_requests_list = set()
        accepted_list = set()
        for i in my_profile.follow.all():
            follow_list.add(i)
        for i in pending_requests:
            pending_requests_list.add(i.object_author.user)
        for i in inbox_requests:
            inbox_requests_list.add(i.actor.user)
        for i in accepted_requests:
            accepted_list.add(i.actor.user)
            accepted_list.add(i.object_author.user)
        context['follows'] = follow_list
        context['pending_requests'] = pending_requests_list
        context['inbox_requests'] = inbox_requests_list
        context['accepted_requests'] = accepted_list
        # if there are no profiles other than the current user:
        context['is_empty'] = False # initially not empty
        if len(self.get_queryset()) == 0:
            context['is_empty'] = True
        return context

# by Shway, view function for sending friend requests
def send_friend_request(request):
    if request.method == 'POST':
        uid = request.POST.get('profile_uid')
        sender = UserProfile.objects.get(user=request.user)
        receiver = UserProfile.objects.get(uid=uid)
        friendRequest = FriendRequest.objects.create(actor=sender, object_author=receiver, status='sent')
        # stay on the same page
        return redirect(request.META.get('HTTP_REFERER'))
    # go to main page if the user did not use the "POST" method
    return redirect('main')

# by Shway, view function for removing a friend
def remove_friend(request):
    if request.method == 'POST':
        uid = request.POST.get('profile_uid')
        sender = UserProfile.objects.get(user=request.user)
        receiver = UserProfile.objects.get(uid=uid)
        # delete the friend request involving current user and the past in user with uid specified
        friendRequest = FriendRequest.objects.get(
            (Q(actor=sender) & Q(object_author=receiver)) | (Q(actor=receiver) & Q(object_author=sender)))
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

    post = get_object_or_404(Post, pk=request.POST.get('pk'))
    post.like.add(request.user)
    post.count = post.count_like()
    post.save()
    return redirect(redirect_path)

def repost(request):
    # should pass back the post from the frontend
    post = get_object_or_404(Post, pk=request.POST.get('pk'))
    ordinary_dict = {'title': post.title, 'content': post.content, 'image':post.image, 'visibility':'PUBLIC'}
    query_dict = QueryDict('', mutable=True)
    query_dict.update(ordinary_dict)
    post_form = PostsCreateForm(query_dict)
    if post_form.is_valid():
        post_form = post_form.save(commit=False)
        post_form.source = (str(request.scheme) + "://"
                                           + str(request.get_host())
                                           + '/author/'
                                           + str(post.author)
                                           + '/posts/'
                                           + str(post.post_id))
        post_form.author = request.user
        post_form.save()
    else:
        print(post_form.errors)
    return redirect('main_page')

def repost_to_friend(request):
    # should pass back the post from the frontend
    post = get_object_or_404(Post, pk=request.POST.get('pk'))
    ordinary_dict = {'title': post.title, 'content': post.content, 'image':post.image, 'visibility':'FRIEND'}
    query_dict = QueryDict('', mutable=True)
    query_dict.update(ordinary_dict)
    print(query_dict)
    post_form = PostsCreateForm(query_dict)
    if post_form.is_valid():
        post_form = post_form.save(commit=False)
        post_form.source = (str(request.scheme) + "://"
                                           + str(request.get_host())
                                           + '/author/'
                                           + str(post.author)
                                           + '/posts/'
                                           + str(post.post_id))
        post_form.author = request.user
        post_form.save()
    else:
        print(post_form.errors)
    return redirect('main_page')

def update_post_view(request):
    pk=request.POST.get('pk')
    if (pk):
        print('Step 1')
        post = get_object_or_404(Post, pk=request.POST.get('pk'))
        post_form = PostUpdateForm(instance = post)
        print(type(post))
        context = {
        'post':post,
        'post_form':post_form,
        }
    post_id = request.POST.get('pid')
    if (post_id):
        print('Step 2')
        post = get_object_or_404(Post, pk=request.POST.get('pid'))
        post_form = PostUpdateForm(request.POST, request.FILES)

        if post_form.is_valid():
            # https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Forms
            # RenewbookForm
            post.title = post_form.cleaned_data['title']
            post.content = post_form.cleaned_data['content']
            post.image = post_form.cleaned_data['image']
            post.visibility = post_form.cleaned_data['visibility']
            post.save()
            return redirect('my_post')
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

def createJsonFromProfile(postList):
    # return (posts and comments) in json format
    new_list = []
    comments = getComments()

    if postList !=[]:
        obj = core_serializers.serialize("json", postList)
        post_json = json.loads(obj)
        for i in post_json:
            fields = i['fields']
            fields['pk'] = i['pk']
            author_name = User.objects.filter(id=fields['author']).first().username

            # print(User.objects.filter(id=fields['author']).first())
            fields['display_name'] = author_name

            fields['comments'] = {}
            for comment in comments:
                if comment['fields']["post"] == fields["pk"]:
                    fields['comments'][comment['pk']] = (comment['fields']['comment'])
                    comment['comment_author_name'] = Comment.objects.filter(author=comment["fields"]["author"]).first()

            new_list.append(fields)

    return new_list, comments

def mypost(request):
    if request.user.is_anonymous:
        return render(request,
                      'Iconicity/login.html',
                      { 'form':  AuthenticationForm })
    # get all the posts posted by the current user

    postList = getPosts(request.user, visibility="FRIENDS")
    new_list, comments = createJsonFromProfile(postList)

    context = {
        'posts': new_list,
        'comments': comments,
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
        print(externalAuthorUrls)
        if externalAuthorUrls != []:
            # now it should be a list of urls of the external followers
            # should like [url1, url2]

            for each_url in externalAuthorUrls:
                full_url = each_url
                if each_url[-1]=="/":
                    full_url += "posts/"
                else:
                    full_url += "/posts/"
                temp = requests.get(full_url)
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
    for host_url in externalHosts:
        if host_url[-1] == "/":
            full_url = host_url + "posts"
        else:
            full_url = host_url + "/posts"
        temp = requests.get(full_url)
        posts = temp.json()

        allPosts += posts
    return allPosts


class AllAuthors(APIView):
    def get(self, request):
        # Get all local authors
        userProfile = UserProfile.objects.all()
        temp = GETProfileSerializer(userProfile,many=True).data
        return Response(temp)


class AuthorById(APIView):
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
    new_list, comments = createJsonFromProfile(postList)
    temp = getAllFollowExternalAuthorPosts(request.user)
    for eachPost in temp:
        eachPost['display_name'] = eachPost['author']['display_name']
    new_list += temp

    context = {
        'posts': new_list,
        'comments': comments,
        'UserProfile': userProfile,
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
    print(externalFollowers)
    for each_url in externalFollowers:
        full_url = each_url

        if each_url[-1] == "/":
            full_url += "followers/"
        else:
            full_url += "/followers/"

        # now check whether you are also his/hers followee.
        temp = requests.get(full_url)
        friends = temp.json()['externalFollows']
        if userProfile.url in friends:
            friendUrlList.append(each_url)

        
    # return a list of urls
    print("friendUrlList",friendUrlList)
    return friendUrlList

def friends(request):
    if request.user.is_anonymous:
        return render(request, 'Iconicity/login.html', { 'form':  AuthenticationForm })
    # get all the posts posted by the current user
    postList = []
    friends_test = getUserFriend(request.user)
    tmp_list = []
    for friend_id in getUserFriend(request.user):
        tmp_list += getPosts(friend_id, visibility="FRIENDS")

    new_list, comments = createJsonFromProfile(tmp_list)
    externalFriends = getExternalUserFriends(request.user)
    if externalFriends and externalFriends !=[]:
        for each_url in externalFriends:
            full_url = each_url

            if each_url[-1] == "/":
                full_url += "friendposts/"
            else:
                full_url += "/friendposts/"
            posts = requests.get(full_url).json()
            postList += posts
    postList += new_list  
    context = {
        'posts': postList,
        'comments': comments,
        'UserProfile': getUserProfile(request.user),
    }

    return render(request,'Iconicity/friends.html', context)

class Posts(APIView):
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
    def get(self, request, post_id):
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


class AllPostsByAuthor(APIView):
    def get(self, request, author_id):
        authorProfile = UserProfile.objects.get(pk=author_id)
        posts = Post.objects.filter(author=authorProfile.user).all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)


class ExternalFollowersByAuthor(APIView):
    def get(self, request, author_id):
        authorProfile = UserProfile.objects.get(pk=author_id)
        print(ExternalFollowersSerializer(authorProfile).data)
        return Response(ExternalFollowersSerializer(authorProfile).data)

class FriendPostsByAuthor(APIView):
    def get(self, request, author_id):
        print(type(request))
        authorProfile = UserProfile.objects.get(pk=author_id)
        friendPosts = Post.objects.filter(author=authorProfile.user)
        return Response(PostSerializer(friendPosts, many=True).data)
        posts = Post.objects.filter(author=authorProfile.user).all()
        return Response(ExternalFollowersSerializer(authorProfile).data)

class AddCommentView(CreateView):
    model = Comment
    template = "Iconicity/comment_form.html"
    def post(self, request):
        print("posting")
        template = "Iconicity/comment_form.html"
        form = CommentsCreateForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.author = request.user
            form.author_id = request.user.id
            form = form.save()
            return redirect('public')
            
        else:
            print(form.errors)
            form = CommentsCreateForm(request.POST)
        
        context = {
            'form': form,
        }
        return render(request, template, context)

    def get(self, request):
        print("getting")
        return render(request, 'Iconicity/comment_form.html', { 'form':  CommentsCreateForm })

