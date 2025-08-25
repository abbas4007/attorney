# forms.py
from botocore.exceptions import ValidationError
from django import forms
from django.forms import modelformset_factory
from django.db import transaction
from home.models import Vakil, ArticleFile, Comision, Article, Riyasat, ArticleImage, Category, Karamooz
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django import forms
from .models import ContactMessage
from captcha.fields import CaptchaField
import jdatetime
import logging

logger = logging.getLogger(__name__)



class ContactForm(forms.ModelForm):
    captcha = CaptchaField(label = "کد امنیتی")

    class Meta :
        model = ContactMessage
        fields = ['full_name', 'phone', 'subject', 'message', 'captcha']
        widgets = {
            'message' : forms.Textarea(attrs = {'rows' : 5}),
        }

class ImageForm(forms.ModelForm):
    class Meta:
        model = Vakil
        fields = ['thumbnail']
        widgets = {
            'thumbnail': forms.FileInput(attrs={'class': 'form-control'})
        }


    def save(self, commit=True) :
        vakil = super().save(commit = False)
        if commit :
            vakil.save()
        return vakil


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
            'author', 'is_special', 'status', 'tags',
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
class ComisionForm(forms.ModelForm):
    class Meta:
        model = Comision
        fields = ['name', 'vakils', 'chairman']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['chairman'].queryset = Vakil.objects.none()

        if 'vakils' in self.data:
            try:
                vakil_ids = self.data.getlist('vakils')
                self.fields['chairman'].queryset = Vakil.objects.filter(id__in=vakil_ids)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['chairman'].queryset = self.instance.vakils.all()


class RaeesForm(forms.ModelForm):
    class Meta:
        model = Riyasat
        fields = ['vakil', 'role']

    def __init__(self, *args, **kwargs) :
        super().__init__(*args, **kwargs)
        self.fields['vakil'].queryset = Vakil.objects.all()

class VakilForm(forms.ModelForm):
    class Meta:
        model = Vakil
        fields = '__all__'
        exclude = ['city_slug']

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['title', ]


class VakilCreateForm(forms.ModelForm):
    # فیلدهای اضافی برای دریافت تاریخ شمسی
    day = forms.IntegerField(label='روز', min_value=1, max_value=31)
    month = forms.IntegerField(label='ماه', min_value=1, max_value=12)
    year = forms.IntegerField(label='سال', min_value=1300, max_value=1500)

    class Meta:
        model = Vakil
        exclude = ['expire_date']  # چون با دست پرش می‌کنیم

    def clean(self):
        cleaned_data = super().clean()
        day = cleaned_data.get('day')
        month = cleaned_data.get('month')
        year = cleaned_data.get('year')

        try:
            j_date = jdatetime.date(year, month, day)
            g_date = j_date.togregorian()
            cleaned_data['expire_date'] = g_date
        except Exception as e:
            raise forms.ValidationError("تاریخ وارد شده نامعتبر است.")

        return cleaned_data

    def save(self, commit=True) :
        instance = super().save(commit = False)
        instance.expire_date = self.cleaned_data['expire_date']

        print(f"Attempting to save instance: {instance.__dict__}")  # دیباگ

        if commit :
            try :
                with transaction.atomic() :
                    instance.save()
                    print("Instance saved successfully!")  # دیباگ
                    if hasattr(self, 'save_m2m') :
                        self.save_m2m()
                    return instance
            except Exception as e :
                logger.error(f"Save failed: {str(e)}", exc_info = True)
                print(f"Save error: {str(e)}")  # دیباگ
                raise
        return instance



class KarAmoozCreateForm(forms.ModelForm) :
    day = forms.IntegerField(
        label = 'روز',
        min_value = 1,
        max_value = 31,
        required = False,  # ← اضافه شد
        widget = forms.NumberInput(attrs = {'class' : 'form-control', 'placeholder' : 'روز'})
    )
    month = forms.IntegerField(
        label = 'ماه',
        min_value = 1,
        max_value = 12,
        required = False,  # ← اضافه شد
        widget = forms.NumberInput(attrs = {'class' : 'form-control', 'placeholder' : 'ماه'})
    )
    year = forms.IntegerField(
        label = 'سال',
        min_value = 1300,
        max_value = 1500,
        required = False,  # ← اضافه شد
        widget = forms.NumberInput(attrs = {'class' : 'form-control', 'placeholder' : 'سال'})
    )

    class Meta :
        model = Karamooz
        exclude = ['expire_date']
        error_messages = {
            'mobile' : {
                'invalid' : "شماره موبایل باید ۱۱ رقمی و با صفر شروع شود."
            },
            'code' : {
                'invalid' : "شماره پروانه باید عددی باشد."
            }
        }

    def __init__(self, *args, **kwargs) :
        super().__init__(*args, **kwargs)
        # تنظیمات اضافی برای فیلدها
        self.fields['name'].required = True
        self.fields['lastname'].required = True
        self.fields['mobile'].required = True
        self.fields['city'].required = True

    def clean_mobile(self) :
        mobile = self.cleaned_data.get('mobile')
        if mobile :
            mobile = mobile.strip()
            if not mobile.startswith('0') :
                raise ValidationError("شماره موبایل باید با صفر شروع شود.")
            if len(mobile) != 11 :
                raise ValidationError("شماره موبایل باید ۱۱ رقمی باشد.")
            if not mobile.isdigit() :
                raise ValidationError("شماره موبایل باید فقط شامل اعداد باشد.")
        return mobile

    def clean(self) :
        cleaned_data = super().clean()
        day = cleaned_data.get('day')
        month = cleaned_data.get('month')
        year = cleaned_data.get('year')

        # فقط اگر یکی از آن‌ها وجود داشت، بررسی کامل شود
        if any([day, month, year]) :
            if None in [day, month, year] :
                raise ValidationError(
                    "اگر قصد دارید تاریخ اعتبار را وارد کنید، هر سه قسمت (روز، ماه، سال) باید وارد شوند.")

            try :
                j_date = jdatetime.date(year, month, day)

                if month < 1 or month > 12 :
                    raise ValidationError("ماه باید بین ۱ تا ۱۲ باشد.")
                if day < 1 :
                    raise ValidationError("روز نمی‌تواند کمتر از ۱ باشد.")
                if month <= 6 and day > 31 :
                    raise ValidationError(f"ماه {month} حداکثر ۳۱ روز دارد.")
                if 7 <= month <= 11 and day > 30 :
                    raise ValidationError(f"ماه {month} حداکثر ۳۰ روز دارد.")
                if month == 12 :
                    max_day = 30 if j_date.isleap() else 29
                    if day > max_day :
                        raise ValidationError(
                            f"اسفند در سال {'کبیسه' if j_date.isleap() else 'غیرکبیسه'} حداکثر {max_day} روز دارد.")

                # اگر همه چیز درست بود، ذخیره شود
                cleaned_data['expire_date'] = j_date.togregorian()

            except ValueError as e :
                raise ValidationError(f"تاریخ وارد شده نامعتبر است: {str(e)}")

        return cleaned_data

    def save(self, commit=True) :
        instance = super().save(commit = False)

        # فقط اگر تاریخ تنظیم شده باشد، مقداردهی کن
        expire_date = self.cleaned_data.get('expire_date')
        if expire_date :
            instance.expire_date = expire_date
        else :
            instance.expire_date = None  # ← یا این خط را حذف کن، اگر قبلاً مقدار پیش‌فرض داری

        if commit :
            try :
                with transaction.atomic() :
                    instance.save()
                    if hasattr(self, 'save_m2m') :
                        self.save_m2m()
            except IntegrityError as e :
                logger.error(f"Error saving Karamooz: {str(e)}")
                raise ValidationError(
                    "خطا در ذخیره اطلاعات. ممکن است اطلاعات تکراری وارد کرده باشید یا مشکل دیگری وجود داشته باشد."
                )
            except Exception as e :
                logger.error(f"Unexpected error saving Karamooz: {str(e)}")
                raise ValidationError(
                    "خطای غیرمنتظره در ذخیره اطلاعات. لطفا با مدیر سیستم تماس بگیرید."
                )

        return instance
