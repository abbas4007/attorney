from django.db import models
from django.utils.html import format_html
from django.utils import timezone
from account.models import User
from django.urls import reverse
from extensions.utils import jalali_converter
import re
from django_quill.fields import QuillField
from ckeditor.fields import RichTextField


# Create your models here.
class ArticleManager(models.Manager):
    def published(self):
        return self.filter(status='p')


class CategoryManager(models.Manager):
    def active(self):
        return self.filter(status=True)


class Category(models.Model):
    title = models.CharField(max_length=200, verbose_name="عنوان دسته‌بندی")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="آدرس دسته‌بندی",blank=True,null=True)
    status = models.BooleanField(default=True, verbose_name="آیا نمایش داده شود؟")
    position = models.IntegerField(verbose_name="پوزیشن")

    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی ها"

    def __str__(self):
        return self.title

    objects = CategoryManager()

def slugify_fa(text, max_length=50):
    # حذف کاراکترهای غیرمجاز (فقط حروف/اعداد فارسی و لاتین + فاصله)
    text = re.sub(r'[^\w\s\u0600-\u06FF]', '', text)

    # حذف فاصله‌های اضافی
    text = re.sub(r'\s+', ' ', text).strip()

    # جایگزینی فاصله با خط تیره
    slug = text.replace(" ", "-")

    # جلوگیری از خط‌تیره‌های پشت‌سرهم
    slug = re.sub(r'-+', '-', slug)

    # محدود کردن طول
    return slug[:max_length]

class Article(models.Model):
    STATUS_CHOICES = (
        ('d', 'پیش‌نویس'),
        ('p', "منتشر شده"),
        ('i', "در حال بررسی"),
        ('b', "برگشت داده شده"),
    )
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='articless', verbose_name="نویسنده")
    title = models.CharField(max_length=200, verbose_name="عنوان مقاله")
    slug = models.CharField(max_length=100, unique=True, verbose_name="آدرس مقاله")
    category = models.ManyToManyField(Category, verbose_name="دسته‌بندی", related_name="articles")
    description = RichTextField(verbose_name="محتوا")
    thumbnail = models.ImageField(upload_to="image", verbose_name="تصویر مقاله", blank=True, null=True)
    publish = models.DateTimeField(default=timezone.now, verbose_name="زمان انتشار")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_special = models.BooleanField(default=False, verbose_name="مقاله ویژه")
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, verbose_name="وضعیت")
    video = models.FileField(blank=True, null=True, verbose_name='ویدیو')

    class Meta:
        verbose_name = "مقاله"
        verbose_name_plural = "مقالات"
        ordering = ['-publish']

    def __str__(self):
        return self.title

    @property
    def description_text(self) :
        # فقط متن خالی از تگ HTML
        from django.utils.html import strip_tags
        return strip_tags(self.description.html)

    def save(self, *args, **kwargs):
        if not self.slug:  # فقط وقتی slug وارد نشده
            base_slug = slugify_fa(self.title)
            slug = base_slug
            counter = 1
            # تا وقتی تکراریه یه عدد به آخرش اضافه کن
            while Article.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("account:home")

    def jpublish(self):
        return jalali_converter(self.publish)
    jpublish.short_description = "زمان انتشار"

    def thumbnail_tag(self):
        return format_html("<img width=100 height=75 style='border-radius: 5px;' src='{}'>".format(self.thumbnail.url))
    thumbnail_tag.short_description = "عکس"

    def category_to_str(self):
        return "، ".join([category.title for category in self.category.active()])
    category_to_str.short_description = "دسته‌بندی"

class ArticleImage(models.Model) :
    article = models.ForeignKey(Article, on_delete = models.CASCADE, related_name = 'images')
    image = models.ImageField(upload_to = 'article_images/',blank = True,null = True)

    def __str__(self) :
        return f"Image for {self.article.title}"


class ArticleManager(models.Manager):
    def published(self):
        return self.filter(status='p')

class ArticleHit(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)


class ArticleFile(models.Model) :
    article = models.ForeignKey(Article, on_delete = models.CASCADE, related_name = 'files')
    file = models.FileField(upload_to = 'article_files/',blank=True, null=True)
    name = models.CharField(max_length = 50,blank=True, null=True)


    def __str__(self) :
        return f"{self.article.title} - {self.file.name}"


class Parvandeh(models.Model):
    title = models.CharField(max_length=200, verbose_name="عنوان ")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="آدرس ")
    description = models.TextField(verbose_name="محتوا")
    thumbnail = models.ImageField(upload_to="image", verbose_name="تصویر ",blank = True,null = True)
    publish = models.DateTimeField(default=timezone.now, verbose_name="زمان انتشار")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "پرونده"
        verbose_name_plural = "پرونده ها"

    def __str__(self):
        return self.title