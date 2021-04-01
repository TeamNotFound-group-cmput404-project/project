# Iconicity

Install necessary libraries:
================================
pip install django-filter;<br/>
pip install markdown;<br/>
pip install djangorestframework;<br/>
pip install asgiref==3.3.1;<br/>
pip install certifi==2020.12.5;<br/>
pip install chardet==4.0.0;<br/>
pip install dj-database-url==0.5.0;<br/>
pip install Django==3.1.6;<br/>
pip install django-crispy-forms==1.11.1;<br/>
pip install django-filter==2.4.0;<br/>
pip install django-on-heroku==1.1.2;<br/>
pip install djangorestframework==3.12.2;<br/>
pip install gunicorn==20.0.4;<br/>
pip install idna==2.10;<br/>
pip install importlib-metadata==3.4.0;<br/>
pip install Markdown==3.3.3;<br/>
pip install Pillow==8.1.0;<br/>
pip install psycopg2-binary==2.8.6;<br/>
pip install pytz==2021.1;<br/>
pip install requests==2.25.1;<br/>
pip install sqlparse==0.4.1;<br/>
pip install typing-extensions==3.7.4.3;<br/>
pip install urllib3==1.26.3;<br/>
pip install whitenoise==5.2.0;<br/>
pip install zipp==3.4.0;<br/>
pip install django-cors-headers;<br/>
Or you can:<br/>
pip install -r requirements.txt<br/>

<!-- * Install necessary libraries :
pip install django
pip install gunicorn django-on-heroku
pip install django-crispy-forms
pip install requests
pip install Pillow
pip install djangorestframework
pip install django-filter
pip install markdown;
-->

Specification:
================
 https://github.com/abramhindle/CMPUT404-project-socialdistribution/blob/master/project.org

Heroku Application URL:
================
https://iconicity-part2.herokuapp.com/

User Guideline:
==================
* Iconicity is blog posting website hosted on Heroku
* To login, enter username and password then click sign in<br/>
If you do not have an account, click sign up button to go to sign up page<br/>
* After login, your profile is on the left side of the main page,
to update, click "profile" then go to edit profile page then click update.<br/>
* Your friends list is on the right side of the main page.<br/>
* To create a post, click "create post" in the main page, then enter your content. To comment any post, click "add comment" to add comment under the post. To like any post, click "like" under the post. To repost, click "repost" under the post.<br/>
* To view your posts, click "my post" button on nav-bar.To edit your post, click edit button under your post. To delete your post, click delete button under your post.<br/>
* To serch user, search the username in the search bar, after you hit the search button, a list of user will appear. You can choose to follow, add to friend or view profile.<br/>
* To check your notification, click the notification button in the nav-bar, then you can see the friend requests you received.<br/>
* To view the posts from users you are following, click following in the nav-bar.<br/>
* To view the psots from your friends, click the friends button in the nav-bar.<br/>
* To logout, click the logout button on the top right corner.<br/>

Citation:
==============
main_base.html is based on https://www.w3schools.com/w3css/tryit.asp?filename=tryw3css_templates_social&stacked=h From https://www.w3schools.com/<br/>

image display in main_base.html(line6-line8) in main_base.html is refer to https://stackoverflow.com/questions/12368910/html-display-image-after-selecting-filename From Stackoverflow by ygssoni https://stackoverflow.com/users/1591101/ygssoni<br/>

form.py is refer to https://simpleisbetterthancomplex.com/tutorial/2017/02/18/how-to-create-user-sign-up-view.html By Vitor Freitas 
and https://www.youtube.com/watch?v=CQ90L5jfldw&list=RDCMUCCezIgC97PvUuR4_gbFUs5g&index=9 By Corey Schafer https://www.youtube.com/channel/UCCezIgC97PvUuR4_gbFUs5g<br/>

model.py is refer to 
model: https://docs.djangoproject.com/en/3.1/topics/db/examples/many_to_one/ by https://www.djangoproject.com/
generate uuid: https://www.geeksforgeeks.org/generating-random-ids-using-uuid-python/ by https://www.geeksforgeeks.org/
user: https://docs.djangoproject.com/en/3.1/ref/contrib/auth/
friend requests: https://www.youtube.com/watch?v=7-VNMGmEN54&list=PLgjw1dR712joFJvX_WKIuglbR1SNCeno1&index=10 by Pyplane https://www.youtube.com/channel/UCQtHyVB4O4Nwy1ff5qQnyRw<br/>

get_author() in serializer.py is refer to https://www.kancloud.cn/thinkphp/python-guide/39426 by https://www.kancloud.cn/thinkphp/python-guide/39196<br/>

serializer.py is refer to https://www.django-rest-framework.org<br/>
getAuthor() in views.py us refer to "Django Authentication Part 1: Sign Up, Login, Logout" https://thecodinginterface.com/blog/django-auth-part1/ by https://thecodinginterface.com/<br/>


login_view() is refer to "How to Create a Logout Page in Django" http://www.learningaboutelectronics.com/Articles/How-to-create-a-logout-button-in-Django.php by http://www.learningaboutelectronics.com/<br/>

signup() is refer to https://simpleisbetterthancomplex.com/tutorial/2017/02/18/how-to-create-user-sign-up-view.html#sign-up-with-profile-model<br/>

mainPagePublic() is refer to "How to Create User Sign Up View" https://docs.djangoproject.com/en/3.1/topics/serialization/ by https://simpleisbetterthancomplex.com/<br/>

AddPostView() is refer to https://iconicity-test-a.herokuapp.com/author/b168fc3-a41f-4537-adbe-9e698420574f/posts/aee8e63f-5792-439e-87f3-3239cce3df98<br/>

update_post_view() is refer to "Django Tutorial Part 9: Working with forms" https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Forms by https://developer.mozilla.org/en-US/<br/>

getAllFollowExternalAuthorPosts() is refer to https://stackoverflow.com/questions/12965203/how-to-get-json-from-webpage-into-python-script by Anurag Uniyal
 https://stackoverflow.com/users/6946/anurag-uniyal<br/>

AddCommentView() is refer to https://www.youtube.com/watch?v=hZrlh4qU4eQ.<br/>

Comment sections in comment_form.html, main_page.html, friends.html, follow.html, my_post.html is refer to https://www.youtube.com/watch?v=hZrlh4qU4eQ.<br/>

post_form.html is refer to https://www.youtube.com/watch?v=m3efqF9abyg. <br/>


RestAPI
========


Contributors / Licensing
========================

Generally everything is LICENSE'D under the Apache 2 license by Meilin Lyu.

All text is licensed under the CC-BY-SA 4.0 http://creativecommons.org/licenses/by-sa/4.0/deed.en_US

Contributors:

    Meilin Lyu
    Zhiqi Zhou
    Qianxi Li
    Hongru Qi
    Shuwei Wang
