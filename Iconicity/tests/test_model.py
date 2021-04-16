from django.test import TestCase
from Iconicity.models import Post,FriendRequest,UserProfile,Comment,Like,Inbox
from django.contrib.auth.models import User
from .test_setup import TestSetUp

class TestModels(TestSetUp):
    def test_model_post_no_pic(self):
        print("test post with no pic")
        User.objects.create(id = 1)
        Post.objects.create(
        post_id = "a0d494d8d315491caec705477ddadf6e",
        title = "1",
        type = "post",
        id = "http://127.0.0.1:8000/author/90a1e228-9139-46f5-8524-83277ecd7e08/posts/a0d494d8-d315-491c-aec7-05477ddadf6e",
        source= "http://127.0.0.1:8000/author/90a1e228-9139-46f5-8524-83277ecd7e08/posts/a0d494d8-d315-491c-aec7-05477ddadf6e",
        origin = "http://127.0.0.1:8000/author/90a1e228-9139-46f5-8524-83277ecd7e08/posts/a0d494d8-d315-491c-aec7-05477ddadf6e",
        description ="",
        contentType = "text/plain",
        content = "nononono",
        categories ={},
        count = 0,
        size = 0,
        external_likes = {},
        published = "2021-04-16 07:20:13.400395",
        visibility = "PUBLIC",
        unlisted = 0,
        image = "",
        host = "",
        author_id = int(1))
        post = Post.objects.get(post_id ="a0d494d8d315491caec705477ddadf6e")
        # test post title
        self.assertEqual(post.title,"1")
        # test post type
        self.assertEqual(post.type,"post")
        # test post visibility
        self.assertEqual(post.visibility,"PUBLIC")
        # test contentType
        self.assertEqual(post.contentType,"text/plain")
    def test_model_post_pic(self):



    def test_model_user_profile(self):
        print("test user profile")
        User.objects.create(id = 1)
        UserProfile.objects.create(
        type = "author",
        id = "90a1e228913946f5852483277ecd7e08",
        displayName = "meilin1",
        github = "http://github.Meilin-Lyu",
        host = "127.0.0.1:8000",
        url = "http://127.0.0.1:8000/author/90a1e228-9139-46f5-8524-83277ecd7e08",
        follow = "{}",
        user_id = 1

        )

    
    def test_friend_request(self):
        print("test friend request")
        User.objects.create(id = 1)
        FriendRequest.objects.create(
            type = "follow",
            summary ="...",
            actor = {},
            object = {}
        )
        print("create successfully")

    def test_comments(self):
        print("test comments object")
        User.objects.create(id = 3)
        Comment.objects.create(
            type = "comment",
            author = {"type": "author", "id": "http://127.0.0.1:8000/author/6feaae52-f1f0-4dd8-bc87-4c93695ca92b", "url": "http://127.0.0.1:8000/author/6feaae52-f1f0-4dd8-bc87-4c93695ca92b", "host": "127.0.0.1:8000", "displayName": "meilin2", "github": "http://github.hi"},
            post = "http://127.0.0.1:8000/author/90a1e228-9139-46f5-8524-83277ecd7e08/posts/a0d494d8-d315-491c-aec7-05477ddadf6e",
        )
        

    def test_like(self):
        print("test like object")
        User.objects.create(id = 1)
        Like.objects.create(
        id =  "49869ba908c44e23a58771107a7447fe",
        type = "like",
        context = "",
        summary = "meilin2 liked your post.",
        author = {"type": "author", "id": "http://127.0.0.1:8000/author/6feaae52-f1f0-4dd8-bc87-4c93695ca92b", "url": "http://127.0.0.1:8000/author/6feaae52-f1f0-4dd8-bc87-4c93695ca92b", "host": "127.0.0.1:8000", "displayName": "meilin2", "github": "http://github.hi"},
        object = "http://127.0.0.1:8000/author/d290560f-50ff-4486-977d-24519f1e0e0b/posts/791a6182-ea75-4d35-8a80-2734f7328d42"

         )

        
    def test_Inbox(self):
        User.objects.create(id = 1)
        Inbox.objects.create(
            id = 1,
            type = "inbox",
            author = "http://127.0.0.1:8000/author/d290560f-50ff-4486-977d-24519f1e0e0b",
            items = [{"type": "comment", "author": {"type": "author", "id": "http://127.0.0.1:8000/author/d290560f-50ff-4486-977d-24519f1e0e0b", "url": "http://127.0.0.1:8000/author/d290560f-50ff-4486-977d-24519f1e0e0b", "host": "127.0.0.1:8000", "displayName": "meilin1", "github": "http://github.hi"}, "published": "2021-04-16T16:25:23.602538Z", "contentType": "", "comment": "2", "id": "http://127.0.0.1:8000/author/d290560f-50ff-4486-977d-24519f1e0e0b/posts/791a6182-ea75-4d35-8a80-2734f7328d42/comments/9abdd88a-953c-431b-950e-18e09dc468d2", "comment_author_name": "meilin1"}, {"type": "comment", "author": {"type": "author", "id": "http://127.0.0.1:8000/author/6feaae52-f1f0-4dd8-bc87-4c93695ca92b", "url": "http://127.0.0.1:8000/author/6feaae52-f1f0-4dd8-bc87-4c93695ca92b", "host": "127.0.0.1:8000", "displayName": "meilin2", "github": "http://github.hi"}, "published": "2021-04-16T16:27:13.025016Z", "contentType": "", "comment": "3", "id": "http://127.0.0.1:8000/author/d290560f-50ff-4486-977d-24519f1e0e0b/posts/791a6182-ea75-4d35-8a80-2734f7328d42/comments/52863e08-ecee-400d-9dbc-94dc3f33acbe", "comment_author_name": "meilin2"}, {"context": "", "summary": "meilin2 liked your post.", "author": {"type": "author", "id": "http://127.0.0.1:8000/author/6feaae52-f1f0-4dd8-bc87-4c93695ca92b", "url": "http://127.0.0.1:8000/author/6feaae52-f1f0-4dd8-bc87-4c93695ca92b", "host": "127.0.0.1:8000", "displayName": "meilin2", "github": "http://github.hi"}, "object": "http://127.0.0.1:8000/author/d290560f-50ff-4486-977d-24519f1e0e0b/posts/791a6182-ea75-4d35-8a80-2734f7328d42", "type": "like"}]
           

        )

