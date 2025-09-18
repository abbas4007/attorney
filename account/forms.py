from django.forms import modelformset_factory
from home.models import ArticleFile, Article, ArticleImage, Category
from django import forms
from captcha.fields import CaptchaField
import logging

logger = logging.getLogger(__name__)






class ArticleFileForm(forms.ModelForm):
    class Meta:
        model = ArticleFile
        fields = ['file']


class ArticleImageForm(forms.ModelForm) :

    class Meta :
        model = ArticleImage
        fields = ['image']


class MultipleFileInput(forms.ClearableFileInput) :
    allow_multiple_selected = True


class MultipleFileField(forms.FileField) :
    def __init__(self, *args, **kwargs) :
        kwargs.setdefault("widget", MultipleFileInput(attrs = {'multiple' : True}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None) :
        if not data and initial :
            return initial

        if not isinstance(data, (list, tuple)) :
            data = [data]

        cleaned_data = []
        for file_data in data :
            if file_data :  # اگر فایل خالی نباشد
                try :
                    cleaned_data.append(super().clean(file_data, initial))
                except forms.ValidationError as e :
                    raise forms.ValidationError(
                        f"خطا در فایل {file_data.name}: {str(e)}"
                    )
        return cleaned_data


class ArticleForm(forms.ModelForm) :
    files = MultipleFileField(
        required = False,
        label = 'فایل‌های ضمیمه',
        help_text = 'می‌توانید چند فایل را همزمان انتخاب کنید'
    )

    images = MultipleFileField(
        required = False,
        label = 'تصاویر گالری',
        help_text = 'می‌توانید چند تصویر را همزمان انتخاب کنید'
    )

    class Meta :
        model = Article
        fields = [
            'title', 'description', 'category', 'thumbnail',
            'author', 'is_special', 'status',
            'video'
        ]
        widgets = {
            'description' : forms.Textarea(attrs = {'class' : 'ckeditor'}),
            'publish' : forms.DateInput(attrs = {'type' : 'date'}),
        }
        labels = {
            'description' : 'محتوا',
        }

    def __init__(self, *args, **kwargs) :
        super().__init__(*args, **kwargs)
        if not self.instance.pk :  # فقط برای ایجاد مقاله جدید
            self.fields['author'].initial = self.initial.get('author')

    def save(self, commit=True) :
        instance = super().save(commit = commit)

        # ذخیره فایل‌های اضافی
        for file in self.cleaned_data.get('files', []) :
            ArticleFile.objects.create(article = instance, file = file)

        # ذخیره تصاویر گالری
        for image in self.cleaned_data.get('images', []) :
            ArticleImage.objects.create(article = instance, image = image)

        return instance

ArticleImageFormSet = modelformset_factory(
    ArticleImage,
    form=ArticleImageForm,
    extra=3
)

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['title', ]





