from django.shortcuts import render, HttpResponse, redirect
# Create your views here.
from django.http import JsonResponse
from django.contrib import auth   # 引入用户认证组件auth模块
from blog.Myforms import UserForm
from blog.models import UserInfo
from blog.utils import validCode
from blog import models


def login(request):
    if request.method == "POST":

        response = {"user": None, "msg": None}
        user = request.POST.get("user")
        pwd = request.POST.get("pwd")
        valid_code = request.POST.get("valid_code")
        # 从session中取到值,一个浏览器存一份，不会发生相互干扰
        valid_code_str = request.session.get("valid_code_str")

        if valid_code.upper() == valid_code_str.upper():   # 添加upper()不区分大小写
            user = auth.authenticate(username=user, password=pwd)
            if user:
                # 验证成功，给ajax返回一个值
                auth.login(request, user)   # request.user：当前登录对象
                response["user"] = user.username   # 当前登录用户的名字

            else:
                response["msg"] = "username or password error!"

        else:
            response['msg'] = "valid code error!"
        return JsonResponse(response)   # 字典放进去直接序列化，ajax拿到的就是  格式，不用反序列化了

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
    auth.logout(request)   # 等同于执行request.session.flush()
    return redirect("/login/")


def register(request):
    if request.is_ajax():  # 也可以使用  if request.method == "POST":
        # 如果是一个Ajax请求
        print(request.POST)   # 所有提交的数据
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
            print(form.errors)   # 字段不符合要求的对应的键作为键，错误信息作为值
            response["msg"] = form.errors

        return JsonResponse(response)

    form = UserForm()   # 实例化form对象
    return render(request, "register.html", {"form": form})  # 注入要传入的是一个字典


def home_site(request, username):
    """
    个人站点视图函数
    :param request:
    :param username:  yuan / alex
    :return:
    """
    print("username", username)
    # 去数据库查找该用户是否存在
    ret = UserInfo.objects.filter(username= username).exists()

    # 判断用户是否存在
    if not ret:
        # 用户不存在返回404页面
        return render(request, "not_found.html")


    return render(request, "home_site.html")
