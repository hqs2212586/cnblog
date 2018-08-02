from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser


class UserInfo(AbstractUser):
    """
    用户信息表：
    使用用户认证组件，用户表的字段不够用，需要继承AbstractUser类来定制一个自己的用户表。
    在继承后，不再生成auth_user表，直接使用user_info表
    """
    nid = models.AutoField(primary_key=True)
    telephone = models.CharField(max_length=11, null=True, unique=True)
    avatar = models.FileField(upload_to='avatars/', default="/avatars/default.png")   # 该字段存放每个用户的头像文件
    """
    FileField与ImageField用法类似，这个字段一定要接受一个文件对象。
    接受文件对象，django会做的事情：默认下载文件到项目的根目录；设置upload_to字段后，会下载到项目根目录的avatars目录下（没有该目录则创建一个）
    user_obj的avatar存的是文件的相对路径
    """
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)   # auto_now_add字段：这个创建时间不用赋值，默认用当前时间赋值

    blog = models.OneToOneField(to='Blog', to_field='nid', null=True, on_delete=models.CASCADE)  # 站点表和用户表一对一关系

    def __str__(self):
        return self.username


class Blog(models.Model):
    """
    博客信息表(站点)
    用户和站点一对一关系，
    """
    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name='个人博客标题', max_length=64)
    site_name = models.CharField(verbose_name='站点名称', max_length=64)
    theme = models.CharField(verbose_name='博客主题', max_length=32)

    def __str__(self):
        return self.title


class Category(models.Model):
    """
    博主个人文章分类表：Linux、python、面试心得、鸡汤
    分类表和用户表是多对一的关系，由于用户和站点是一对一，分类表与站点也是多对一的关系
    """
    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name='分类标题', max_length=32)
    blog = models.ForeignKey(verbose_name='所属博客', to='Blog', to_field='nid', on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Tag(models.Model):
    """
    标签
    站点和标签绑定的是一对多的关系
    """
    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name='标签名称', max_length=32)
    blog = models.ForeignKey(verbose_name='所属博客', to='Blog', to_field='nid', on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Article(models.Model):
    """
    文章表
    分类和文章的关系在这里设置为一对多关系（为了与文章和标签关系形成区分）
    用户和文章是一对多的关系
    标签与文章是多对多的关系（用中介模型创建第三张表）
    """
    nid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50, verbose_name='文章标题')
    desc = models.CharField(max_length=255, verbose_name='文章描述')   # 摘要
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)   # 发布时间
    content = models.TextField()  # 文章内容

    comment_count = models.IntegerField(default=0)
    up_count = models.IntegerField(default=0)
    down_count = models.IntegerField(default=0)

    user = models.ForeignKey(verbose_name='作者', to='UserInfo', to_field='nid', on_delete=models.CASCADE)
    category = models.ForeignKey(to='Category', to_field='nid', null=True, on_delete=models.CASCADE)
    tags = models.ManyToManyField(    # 中介模型创建第三张关系表
        to="Tag",
        through='Article2Tag',
        through_fields=('article', 'tag'),
    )

    def __str__(self):
        return self.title


class Article2Tag(models.Model):
    """
    文章和标签关系表
    """
    nid = models.AutoField(primary_key=True)
    article = models.ForeignKey(verbose_name='文章', to="Article", to_field='nid', on_delete=models.CASCADE)
    tag = models.ForeignKey(verbose_name='标签', to="Tag", to_field='nid', on_delete=models.CASCADE)

    class Meta:
        unique_together = [   # 联合唯一，两个字段不能重复
            ('article', 'tag'),
        ]

    def __str__(self):
        v = self.article.title + "---" + self.tag.title
        return v


class ArticleUpDown(models.Model):
    """
    文章点赞表
    哪个用户对哪个文章点赞或点灭
    """
    nid = models.AutoField(primary_key=True)
    user = models.ForeignKey('UserInfo', null=True, on_delete=models.CASCADE)
    article = models.ForeignKey("Article", null=True, on_delete=models.CASCADE)
    is_up = models.BooleanField(default=True)   # True：赞，  False：灭

    class Meta:
        unique_together = [
            ('article', 'user'),
        ]


class Comment(models.Model):
    """
    评论表
    根评论：对文章的评论
    子评论：对评论的评论
    哪一个用户对哪一篇文章在什么时间做了什么评论内容
    nid    user_id  article_id    content    parent_comment_id(null=True)
    1       1           1           111             null
    2       2           1           222             null
    3       3           1           333             null
    4       4           1           444               1
    5       5           1           555               4
    """
    nid = models.AutoField(primary_key=True)
    article = models.ForeignKey(verbose_name='评论文章', to='Article', to_field='nid', on_delete=models.CASCADE)
    user = models.ForeignKey(verbose_name='评论者', to='UserInfo', to_field='nid', on_delete=models.CASCADE)
    content = models.CharField(verbose_name='评论内容', max_length=255)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    # parent_comment = models.ForeignKey("Comment")   # 关联Comment表，本身就在Comment表中，因此是自关联
    parent_comment = models.ForeignKey('self', null=True, on_delete=models.CASCADE)   # 设置null=True,为null的情况不用存值了

    def __str__(self):
        return self.content













