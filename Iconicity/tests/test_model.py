from django.test import TestCase
from Iconicity.models import Post,FriendRequest,UserProfile,Comment
from django.contrib.auth.models import User
from .test_setup import TestSetUp

class TestModels(TestSetUp):
    def test_model_post(self):
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


    def test_model_user_profile(self):
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
        User.objects.create(id = 1)
        FriendRequest.objects.create(
            type = "follow",
            summary ="...",
            actor = {},
            object = {}
        )

    def test_comments(self):
        User.objects.create(id = 1)
        Comment.objects.create(
            type = "comment",
            author = "Meilin2",
            post = "http://127.0.0.1:8000/author/90a1e228-9139-46f5-8524-83277ecd7e08/posts/a0d494d8-d315-491c-aec7-05477ddadf6e",
            




        )
        


        
       