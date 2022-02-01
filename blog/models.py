import markdown
from django.utils import timezone
from django.utils.html import strip_tags
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Category(models.Model):
    """
    django要求模型必须继承models.Model类
    Category只需要一个简单的分类名name即可
    CharField指定分类名name的数据类型，CharField是字符型
    CharField的max_length参数指定其最大长度，超过这个长度的分类名就不能被存入数据库
    django为我们提供了多种其它的数据类型，如日期时间类型DateTimeField、整数类型IntegerField等等
    django内置的数据类型参见：
    https://docs.djangoproject.com/en/2.2/ref/models/fields/#fields-types
    """
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = '分类'
        verbose_name_plural = verbose_name

    def __str__(self) -> str:
        return self.name


class Tag(models.Model):
    """
    标签Tag
    """
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = '标签'
        verbose_name_plural = verbose_name

    def __str__(self) -> str:
        return self.name


class Post(models.Model):
    """
    文章的数据库表
    """

    # 文章标题
    title = models.CharField('标题',max_length=70)

    # 文章正文，使用TextField
    # 存储比较短的字符串用CharField，存储大段文本用TextField
    body = models.TextField('正文')

    # 文章的创建时间和最后一次修改时间
    created_time = models.DateTimeField('创建时间', default=timezone.now)
    modified_time = models.DateField('修改时间')

    # 文章摘要，可以没有文章摘要，默认情况下，CharField要求必须存入数据，否则报错
    # 指定CharField的blank=True，即可允许空值
    excerpt = models.CharField('摘要',max_length=200, blank=True)

    # 分类与标签，分类与标签的模型已经定义
    # 把文章对应的数据库表和分类、标签对应的数据库表关联起来，关联形式略有不同
    # 规定一篇文章只能对应一个分类，一个分类下可以有多篇文章， 使用ForeignKey，即一对多的关联关系
    # django2.0以后，ForeighKey必须传入一个on_delete参数用来指定当关联的数据被删除时，被关联的数据的行为
    # 这里使用级联删除models.CASCADE，当某个分类被删除时，该分类下全部文章同时被删除
    # ManyToManyField表示多对多的关系
    # 规定文章可以没有标签
    # 参见文档：
    #  https://docs.djangoproject.com/en/2.2/topics/db/models/#relationships
    category = models.ForeignKey(Category, verbose_name='分类', on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, verbose_name='标签', blank=True)

    # 文章作者，这里的User是从django.contrib.auth.models导入的
    # django.contrib.auth是django内置的应用，专门用于处理网站用户的注册、登录等流程
    # User是django为我们写好的用户模型
    # 通过ForeignKey把文章和User关联起来
    # 规定一篇文章只能有一个作者，一个作者可能会写多篇文章，一对多关系
    author = models.ForeignKey(User, verbose_name='作者', on_delete=models.CASCADE)
    views = models.PositiveIntegerField(default=0, editable=False)

    class Meta:
        verbose_name = '文章'
        verbose_name_plural = verbose_name
        ordering = ['-created_time']

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        # 首先实例化一个 Markdown 类，用于渲染 body 的文本。
        # 由于摘要并不需要生成文章目录，所以去掉了目录拓展。
        md = markdown.Markdown(extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
        ])
        # 先将 Markdown 文本渲染成 HTML 文本
        # strip_tags 去掉 HTML 文本的全部 HTML 标签
        # 从文本摘取前 54 个字符赋给 excerpt
        self.excerpt = self.excerpt if self.excerpt is not None else strip_tags(md.convert(self.body))[:54]

        self.modified_time = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        # blog:detail blog应用下的name=detail的视图函数
        # reverse解析视图函数对应的URL规则，返回相应的URL
        return reverse('blog:detail', kwargs={'pk': self.pk})

    def increase_views(self):
        self.views += 1
        self.save(update_fields=['views'])