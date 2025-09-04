import os

from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.conf import settings
import requests
from home.models import Article, ArticleImage, ArticleFile, Category
from .forms import KarAmoozCreateForm,ImageForm, ComisionForm, RaeesForm, ContactForm, ArticleForm,CategoryForm, VakilCreateForm
from .models import ContactMessage
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
from django.http import JsonResponse

# --- تماس با ما ---
@csrf_exempt
def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            message = form.save()
            try:
                response = requests.post(
                    "https://api.ghasedak.me/v2/sms/send/simple",
                    data={
                        "message": f"پیام شما با شماره پیگیری {message.id} دریافت شد",
                        "receptor": message.phone,
                        "linenumber": settings.SMS_LINE_NUMBER
                    },
                    headers={
                        "apikey": settings.GHASEDAK_API_KEY,
                        "Content-Type": "application/x-www-form-urlencoded"
                    },
                    timeout=10
                )
            except requests.exceptions.RequestException as e:
                print("SMS Error:", str(e))
            return redirect('account:success_page')
    else:
        form = ContactForm()
    return render(request, 'account/contact.html', {'form': form})

def refresh_captcha(request):
    new_key = CaptchaStore.generate_key()
    to_json_response = {
        'key': new_key,
        'image_url': captcha_image_url(new_key),
    }
    return JsonResponse(to_json_response)

def success_page(request):
    return render(request, 'account/success.html')


# --- مدیریت پیام‌ها ---
class MessageListView(LoginRequiredMixin, ListView):
    model = ContactMessage
    template_name = 'account/message_list.html'
    context_object_name = 'messages'
    ordering = ['-created_at']
    paginate_by = 10

class MessageDetailView(LoginRequiredMixin, DetailView):
    model = ContactMessage
    template_name = 'account/message_detail.html'
    context_object_name = 'message'

class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = ContactMessage
    fields = ['status', 'response']
    template_name = 'account/message_form.html'
    success_url = reverse_lazy('account:home')

    def form_valid(self, form):
        response = super().form_valid(form)
        if form.cleaned_data.get('response'):
            try:
                payload = {
                    "message": f"پاسخ به پیام شما:\n{form.cleaned_data['response']}",
                    "receptor": self.object.phone,
                    "linenumber": settings.SMS_LINE_NUMBER
                }
                headers = {
                    "apikey": settings.GHASEDAK_API_KEY,
                    "Content-Type": "application/x-www-form-urlencoded"
                }
                requests.post("https://api.ghasedak.me/v2/sms/send/simple", data=payload, headers=headers)
            except Exception as e:
                print("SMS Response Error:", str(e))
        return response


# --- ورود ---
class CustomLoginView(LoginView):
    template_name = 'account/login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('account:home')


# --- مقاله ---
class ArticleList(LoginRequiredMixin, ListView):
    model = Article
    paginate_by = 6
    template_name = "account/home.html"
    context_object_name = "object_list"

    def get_queryset(self) :
        query = self.request.GET.get("q")
        queryset = Article.objects.filter(status = 'p').order_by('-publish', '-created')
        if query :
            queryset = queryset.filter(Q(title__icontains = query)).order_by('-publish', '-created')
        return queryset


@login_required
def article_create_view(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save()
            messages.success(request, "مقاله با موفقیت ذخیره شد.")
            return redirect('home:article_list')
        else:
            messages.error(request, "لطفاً خطاهای فرم را بررسی کنید.")
    else:
        form = ArticleForm(initial={'author': request.user})

    return render(request, 'account/article-create-update.html', {
        'form': form,
    })
@login_required
@require_POST
def delete_article_image(request, image_id):
    try:
        image = ArticleImage.objects.get(id=image_id)
        # اطمینان از دسترسی کاربر
        if request.user.is_superuser or image.article.author == request.user:
            image.delete()
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)
    except ArticleImage.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Image not found'}, status=404)

class ArticleUpdate(LoginRequiredMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = "account/article-create-update.html"
    success_url = reverse_lazy('account:home')

    def form_valid(self, form):
        response = super().form_valid(form)
        files = self.request.FILES.getlist('file')
        for f in files:
            ArticleFile.objects.create(article=self.object, file=f)
        return response

class ArticleDelete(LoginRequiredMixin, DeleteView):
    model = Article
    template_name = "account/article_confirm_delete.html"
    success_url = reverse_lazy('account:home')






@login_required
def add_comision(request):
    if request.method == 'POST':
        form = ComisionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home:home')
    else:
        form = ComisionForm()
    return render(request, 'account/comision-create-update.html', {'form': form})




class CategoryListView(ListView):
    model = Category
    template_name = 'account/category_list.html'
    context_object_name = 'categories'


class CategoryCreateView(CreateView) :
    model = Category
    form_class = CategoryForm
    template_name = 'account/category_form.html'
    success_url = reverse_lazy('account:category_list')


class CategoryUpdateView(UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'account/category_form.html'
    success_url = reverse_lazy('account:category_list')

class CategoryDeleteView(DeleteView):
    model = Category
    template_name = 'account/category_confirm_delete.html'
    success_url = reverse_lazy('account:category_list')

