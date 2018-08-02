from django.contrib import admin

# Register your models here.
from blog import models


admin.site.register(models.UserInfo)   # 用户信息表
admin.site.register(models.Blog)
admin.site.register(models.Category)
admin.site.register(models.Tag)
admin.site.register(models.Article)    # 文章表
admin.site.register(models.ArticleUpDown)   # 文章点赞表
admin.site.register(models.Article2Tag)
admin.site.register(models.Comment)   # 评论表
