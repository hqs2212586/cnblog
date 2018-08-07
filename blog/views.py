from django.shortcuts import render, HttpResponse, redirect
# Create your views here.
from django.http import JsonResponse
from django.contrib import auth  # 引入用户认证组件auth模块
from blog.Myforms import UserForm
from blog.models import UserInfo
from blog.utils import validCode
from blog import models
from django.db.models import Avg, Max, Min, Count
from django.db import transaction


def login(request):
    if request.method == "POST":

        response = {"user": None, "msg": None}
        user = request.POST.get("user")
        pwd = request.POST.get("pwd")
        valid_code = request.POST.get("valid_code")
        # 从session中取到值,一个浏览器存一份，不会发生相互干扰
        valid_code_str = request.session.get("valid_code_str")

        if valid_code.upper() == valid_code_str.upper():  # 添加upper()不区分大小写
            user = auth.authenticate(username=user, password=pwd)
            if user:
                # 验证成功，给ajax返回一个值
                auth.login(request, user)  # request.user：当前登录对象
                response["user"] = user.username  # 当前登录用户的名字

            else:
                response["msg"] = "username or password error!"

        else:
            response['msg'] = "valid code error!"
        return JsonResponse(response)  # 字典放进去直接序列化，ajax拿到的就是  格式，不用反序列化了

    return render(request, 'login.html')


def get_validCode_img(request):
    """
    基于PIL模块动态生成响应状态码图片
    :param request:
    :return:
    """
    data = validCode.get_valid_code_imge(request)
    return HttpResponse(data)


def index(request):
    # 拿到当前所有的文章
    article_list = models.Article.objects.all()
    return render(request, "index.html", {"article_list": article_list})


def logout(request):
    auth.logout(request)  # 等同于执行request.session.flush()
    return redirect("/login/")


def register(request):
    if request.is_ajax():  # 也可以使用  if request.method == "POST":
        # 如果是一个Ajax请求
        print(request.POST)  # 所有提交的数据
        form = UserForm(request.POST)  # 创建UserForm对象，传入当前提交的字典
        response = {"user": None, "msg": None}

        if form.is_valid():  # form.is_valid是帮忙校验返回布尔值的,true或false（所有都通过才返回true）
            # 类定义的字段全符合要求，返回true
            response["user"] = form.cleaned_data.get("user")

            # 生成一条用户记录
            user = form.cleaned_data.get("user")
            pwd = form.cleaned_data.get("pwd")
            email = form.cleaned_data.get("email")
            avatar_obj = request.FILES.get("avatar")

            extra = {}  # 空字典
            if avatar_obj:
                extra["avatar"] = avatar_obj  # 传值进空字典
            UserInfo.objects.create_user(username=user, password=pwd, email=email, **extra)  # **extra代表额外的参数

            """
            if avatar_obj:
                # 如果上传了头像，即有值
                # 用户认证组件使用create_user辅助函数创建用户
                user_obj = UserInfo.objects.create_user(username=user, password=pwd, email=email, avatar=avatar_obj)
            else:
                # 如果没有传头像，就用默认的default.png
                user_obj = UserInfo.objects.create_user(username=user, password=pwd, email=email)
            """
        else:
            # 包含错误信息返回false
            print(form.cleaned_data)  # 字段值符合要求的放在cleaned_data
            print(form.errors)  # 字段不符合要求的对应的键作为键，错误信息作为值
            response["msg"] = form.errors

        return JsonResponse(response)

    form = UserForm()  # 实例化form对象
    return render(request, "register.html", {"form": form})  # 注入要传入的是一个字典


def home_site(request, username, **kwargs):
    """
    个人站点视图函数
    :param request:
    :param username:  yuan / alex
    :return:
    """
    print("kwargs", kwargs)

    print("username", username)
    # 去数据库查找该用户是否存在
    # ret = UserInfo.objects.filter(username= username).exists()

    # 拿到当前用户对象
    user = UserInfo.objects.filter(username=username).first()

    # 判断用户是否存在
    if not user:
        # 用户不存在返回404页面
        return render(request, "not_found.html")

    # 查询当前站点对象
    blog = user.blog

    article_list = models.Article.objects.filter(user=user)
    if kwargs:
        condition = kwargs.get("condition")
        param = kwargs.get("param")  # 2012-12

        if condition=="category":
            article_list = article_list.filter(category__title=param)
        elif condition=="tag":
            article_list = article_list.filter(tags__title=param)
        else:
            year, month = param.split("-")
            article_list = article_list.filter(create_time__year=year, create_time__month=month)


    # 查看当前用户或当前站点所对应的所有文章
    # 方法1：基于对象查询
    # article_list = user.article_set.all()
    # 方法2：基于双下划线查询
    # article_list = models.Article.objects.filter(user=user)

    # 每一个后的表模型.objects.values("pk").annotate(聚合函数(关联表__统计字段)).values()
    # 查询每一个分类名称及对应的文章数(最简单的分组查询)
    ret = models.Category.objects.values("pk").annotate(c=Count("article__title")).values("title", "c")
    print(ret)  # <QuerySet [{'title': 'yuan的鸡汤', 'c': 1}, {'title': 'Dubbo', 'c': 1}, {'title': '前端', 'c': 1}]>

    # 查询当前站点的每一个分类名称以及对应的文章数
    cate_list = models.Category.objects.filter(blog=blog).values("pk").annotate(c=Count("article__title")).values_list(
        "title", "c")
    print(cate_list)  # <QuerySet [{'title': 'yuan的鸡汤', 'c': 1}, {'title': 'Dubbo', 'c': 1}]>

    # 查询当前站点的每一个标签名称及对应的文章数
    tag_list = models.Tag.objects.filter(blog=blog).values("pk").annotate(c=Count("article")).values_list("title", "c")
    print(tag_list)

    # 查询当前站点每一个年月的名称及对应的文章数
    # ret = models.Article.objects.extra(select={"is_recent": "create_time > '2017-09-05'"}).values("title", "is_recent")
    # print(ret) # <QuerySet [{'is_recent': 1, 'title': '追求优秀，才是合格的程序员'}, {'is_recent': 1, 'title': 'Dubbo负载均衡与集群容错机制'}, {'is_recent': 1, 'title': 'vue相关'}]>

    # ret = models.Article.objects.extra(select={"y_m_d_date": "date_format(create_time, '%%Y-%%m-%%d')"}).values("title", "y_m_d_date").annotate(c=Count("nid")).values("y_m_d_date", "c")
    # print(ret)

    # date_list = models.Article.objects.filter(user=user).extra(select={"y_m_date": "date_format(create_time, '%%Y-%%m')"}).values("y_m_date").annotate(c=Count("nid")).values("y_m_date", "c")
    # print(date_list)   # <QuerySet [{'y_m_date': '2018-08', 'c': 2}]>

    # 改用values_list，得到字典
    date_list = models.Article.objects.filter(user=user).extra(
        select={"y_m_date": "date_format(create_time, '%%Y-%%m')"}).values("y_m_date").annotate(
        c=Count("nid")).values_list(
        "y_m_date", "c")
    print(date_list)  # <QuerySet [('2018-08', 2)]>

    # 方式二
    from django.db.models.functions import TruncMonth
    ret = models.Article.objects.filter(user=user).annotate(month=TruncMonth("create_time")).values("month").annotate(
        c=Count("nid")).values_list("month", "c")
    print("ret---->", ret)  # ret----> <QuerySet [(datetime.datetime(2018, 8, 1, 0, 0), 2)]>

    return render(request, "home_site.html",
                  {"username": username, "blog": blog, "article_list": article_list, "cate_list": cate_list, "tag_list": tag_list,
                   "date_list": date_list})


def get_classification_data(username):
    user = UserInfo.objects.filter(username=username).first()
    blog = user.blog

    cate_list = models.Category.objects.filter(blog=blog).values("pk").annotate(c=Count("article__title")) \
        .values_list("title", "c")

    tag_list = models.Tag.objects.filter(blog=blog).values("pk").annotate(c=Count("article")) \
        .values_list("title", "c")

    date_list = models.Article.objects.filter(user=user).extra(
        select={"y_m_date": "date_format(create_time, '%%Y-%%m')"}) \
        .values("y_m_date").annotate(c=Count("nid")).values_list("y_m_date", "c")
    return {"blog": blog, "cate_list": cate_list, "tag_list": tag_list, "date_list": date_list}


def article_detail(request, username, article_id):

    user = UserInfo.objects.filter(username=username).first()
    blog = user.blog

    article_obj = models.Article.objects.filter(pk=article_id).first()

    comment_list = models.Comment.objects.filter(article_id=article_id)

    return render(request, "article_detail.html", locals())

    # context = get_classification_data(username)
    # return render(request, "article_detail.html", context)


import json
from django.http import JsonResponse

from django.db.models import F   # F函数

def digg(request):
    """
    点赞视图函数
    :param request:
    :return:
    """
    print(request.POST)
    # <QueryDict: {'csrfmiddlewaretoken': ['hBlBWfxGFhDXaqDCfkSMFhKd6ZhZsbuqM8TEj3upzwe2NynenybodHgQyFHQAvZ0'],
    #               'is_up': ['true'], 'article_id': ['1']}>

    article_id = request.POST.get("article_id")
    # is_up = request.POST.get("is_up")    # 拿到的是一个字符串 "true"
    is_up = json.loads(request.POST.get("is_up"))   # 反序列化，拿到一个bool值

    # 点赞人即当前登录人
    user_id = request.user.pk

    # 用户只要在点赞表存有记录就不能再存了
    obj = models.ArticleUpDown.objects.filter(user_id=user_id, article_id=article_id).first()

    response = {"state": True}
    if not obj:
        # 创建一条新记录
        ard = models.ArticleUpDown.objects.create(user_id=user_id, article_id=article_id, is_up=is_up)

        queryset = models.Article.objects.filter(pk=article_id)
        if is_up:
            queryset.update(up_count=F("up_count")+1)
        else:
            queryset.update(down_count=F("down_count")+1)
    else:
        # 重复点赞提示,告诉ajax已经推荐过了
        response["state"] = False
        response["handled"] = obj.is_up   # True：推荐过了， Flase: 踩过了

    return JsonResponse(response)   # 返回response字典


def comment(request):
    print(request.POST)

    article_id = request.POST.get("article_id")
    pid = request.POST.get("pid")
    content = request.POST.get("content")
    user_id = request.user.pk

    # 为了发送邮件拿到文章对象
    article_obj = models.Article.objects.filter(pk=article_id).first()

    # 事务操作：生成记录和评论数更新同进同退
    with transaction.atomic():
        # 在数据库生成一条评论对象  父评论为空是根评论，不为空则是子评论
        comment_obj = models.Comment.objects.create(user_id=user_id, article_id=article_id, content=content, parent_comment_id=pid)
        # 文章评论数更新
        models.Article.objects.filter(pk=article_id).update(comment_count=F("comment_count")+1)

    response = {}
    # create_time是一个datetime.datetime对象，在json序列化时不能对对象进行json序列化，必须进行strftime的转换
    response["create_time"] = comment_obj.create_time.strftime("%Y-%m-%d %X")
    # 评论人
    response["username"] = request.user.username
    # 内容
    response["content"] = content

    # 发送邮件
    from django.core.mail import send_mail
    from cnblog import settings
    # send_mail(
    #     "您的文章%s新增了一条评论内容" % article_obj.title,
    #     content,
    #     settings.EMAIL_HOST_USER,   # 发送方
    #     ["443614404@qq.com"]   # 接收方
    # )

    import threading

    t = threading.Thread(target=send_mail, args=(
        "您的文章%s新增了一条评论内容" % article_obj.title,
        content,
        settings.EMAIL_HOST_USER,  # 发送方
        ["443614404@qq.com"]  # 接收方
    ))
    t.start()


    # 父评论对象评论人和评论内容
    response["parent_username"] = comment_obj.parent_comment.user.username
    response["parent_content"] = comment_obj.parent_comment.content

    return JsonResponse(response)


def get_comment_tree(request):
    article_id = request.GET.get("article_id")
    # 过滤出文章对应的评论，挑出主键值、评论内容、父评论id，拿到的是一个queryset，结构类似一个列表里面装着一个个字典
    # 但是queryset并不是一个列表，可以用list()函数将其转换为列表
    ret = list(models.Comment.objects.filter(article_id=article_id).order_by("pk").values("pk", "content", "parent_comment_id"))

    # JsonResponse对非字典的数据进行序列化，必须设置一个参数safe=False
    return JsonResponse(ret, safe=False)
