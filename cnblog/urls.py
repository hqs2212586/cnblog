"""cnblog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,re_path
from django.views.static import serve
from blog import views
from cnblog import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login),
    path('index/', views.index),
    path('logout/', views.logout),
    re_path('^$', views.index),   # http://127.0.0.1:8000  直接访问首页
    path('get_validCode_img/', views.get_validCode_img),
    path('register/', views.register),

    path('digg/', views.digg),  # 点赞
    path('comment/', views.comment),  # 评论
    path("get_comment_tree/", views.get_comment_tree),   # 评论树

    # media配置
    # 匹配以media开头的任意路径
    re_path(r"media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),

    # 个人站点url
    # 正则规则：\w：匹配数字、字母、下划线   \W：匹配除数字、字母、下划线以外的任意字符
    # '(?P<name>...)' 分组匹配  {"username": alex}
    re_path('^(?P<username>\w+)$', views.home_site),

    # 有名分组
    re_path('^(?P<username>\w+)/(?P<condition>tag|category|archive)/(?P<param>.*)/$', views.home_site),

    # 文章详情页
    re_path('^(?P<username>\w+)/articles/(?P<article_id>\d+)$', views.article_detail),
]
