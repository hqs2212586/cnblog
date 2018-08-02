# -*- coding:utf-8 -*-
__author__ = 'Qiushi Huang'

from django import forms
from django.forms import widgets
from blog.models import UserInfo
from django.core.exceptions import ValidationError


class UserForm(forms.Form):
    user = forms.CharField(max_length=32,
                           error_messages={"required": "该字段不能为空"},
                           label="用户名",
                           widget=widgets.TextInput(attrs={"class": "form-control"},)
                           )
    pwd = forms.CharField(max_length=32,
                          label="密码",
                          widget=widgets.PasswordInput(attrs={"class": "form-control"}, )
                          )
    re_pwd = forms.CharField(max_length=32,
                             label="确认密码",
                             widget=widgets.PasswordInput(attrs={"class": "form-control"},)
                             )
    email = forms.EmailField(max_length=32,
                             label="邮箱",
                             widget=widgets.EmailInput(attrs={"class": "form-control"},)
                             )

    # 局部钩子
    def clean_user(self):
        val = self.cleaned_data.get("user")
        user = UserInfo.objects.filter(username=val).first()
        if not user:
            return val
        else:
            raise ValidationError("该用户已注册！")

    # 全局钩子
    def clean(self):
        pwd = self.cleaned_data.get("pwd")
        re_pwd = self.cleaned_data.get("re_pwd")

        if pwd and re_pwd:
            # 如果两个都有值
            if pwd == re_pwd:
                # 验证成功
                return self.cleaned_data
            else:
                # 验证失败
                raise ValidationError("两次密码不一致！")
        else:
            # 如果任有一个没有值则不做处理
            return self.cleaned_data
