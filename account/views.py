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
from home.models import Article, Vakil, Riyasat, ArticleImage, ArticleFile, Comision, Category,Karamooz
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


class AddVakil(LoginRequiredMixin, CreateView):
    model = Vakil
    form_class = VakilCreateForm
    template_name = "account/vakil-create-update.html"
    success_url = reverse_lazy('account:home')

class AddKarAmooz(LoginRequiredMixin, CreateView):
    model = Karamooz
    form_class = KarAmoozCreateForm
    template_name = "account/karamooz-create-update.html"
    success_url = reverse_lazy('account:karamooz_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'کارآموز با موفقیت اضافه شد.')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'افزودن کارآموز جدید'
        return context

class VakilUpdateView(LoginRequiredMixin, UpdateView):
    model = Vakil
    form_class = VakilCreateForm
    template_name = 'account/vakil-create-update.html'
    success_url = reverse_lazy('account:vakil_list')

class KarAmoozUpdateView(LoginRequiredMixin, UpdateView):
    model = Karamooz
    form_class = KarAmoozCreateForm
    template_name = 'account/karamooz-create-update.html'
    success_url = reverse_lazy('account:karamooz_list')

class VakilDeleteView(LoginRequiredMixin, DeleteView):
    model = Vakil
    template_name = 'account/vakil_confirm_delete.html'
    success_url = reverse_lazy('account:vakil_list')

class KarAmoozDeleteView(LoginRequiredMixin, DeleteView):
    model = Karamooz
    template_name = 'account/karamooz_confirm_delete.html'
    success_url = reverse_lazy('account:karamooz_list')


class vakileList(LoginRequiredMixin, ListView):
    model = Vakil
    template_name = "account/vakil_list.html"
    context_object_name = "vakils"
    paginate_by = 10

    def get_queryset(self):
        search_query = self.request.GET.get('search', '')
        if search_query:
            return Vakil.objects.filter(
                Q(name__icontains=search_query) |
                Q(lastname__icontains=search_query) |
                Q(city__icontains=search_query) |
                Q(address__icontains=search_query)
            )
        return Vakil.objects.all()


class KarAmoozList(LoginRequiredMixin, ListView) :
    model = Karamooz
    template_name = "account/karamooz_List.html"
    context_object_name = "karamoozs"
    paginate_by = 10

    def get_queryset(self) :
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search')

        if search_query :
            queryset = queryset.filter(
                Q(name__icontains = search_query) |
                Q(lastname__icontains = search_query) )


        return queryset.order_by('-id')



class vakil_image_view(LoginRequiredMixin, View):
    form_class = ImageForm
    template_name = 'account/vakil_image_update.html'

    def get_object(self):
        return get_object_or_404(Vakil, pk=self.kwargs['id'])

    def get(self, request, *args, **kwargs):
        form = self.form_class(instance=self.get_object())
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        vakil = self.get_object()
        form = self.form_class(request.POST, request.FILES, instance=vakil)
        if form.is_valid():
            form.save()
            return redirect('account:vakil_list')
        return render(request, self.template_name, {'form': form})

class karamooz_image_view(LoginRequiredMixin, View):
    form_class = ImageForm
    template_name = 'account/karamooz_image_update.html'

    def get_object(self):
        return get_object_or_404(Karamooz, pk=self.kwargs['id'])

    def get(self, request, *args, **kwargs):
        form = self.form_class(instance=self.get_object())
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        karamooz = self.get_object()
        form = self.form_class(request.POST, request.FILES, instance=karamooz)
        if form.is_valid():
            form.save()
            return redirect('account:karamooz_list')
        return render(request, self.template_name, {'form': form})


# --- کمیسیون ---
class ComisionList(LoginRequiredMixin, View):
    def get(self, request):
        comisions = Comision.objects.all().order_by('-chairman')
        return render(request, 'inc/navbar.html', {'comisions': comisions})


class ComisionDetail(View):
    def get(self, request, id):
        comision = get_object_or_404(Comision.objects.prefetch_related('vakils'), id=id)
        return render(request, 'account/comisiondetail.html', {'comisions': comision})


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


@require_GET
def search_vakils(request) :
    q = request.GET.get('q', '')

    vakils = Vakil.objects.filter(
        Q(name__icontains = q) | Q(lastname__icontains = q)
    ).values('id', 'name', 'lastname')

    return JsonResponse({
        'items' : [
            {
                'id' : v['id'],
                'text' : f"{v['name']} {v['lastname']}"
            } for v in vakils
        ]
    })

class AddComision(LoginRequiredMixin, CreateView):
    model = Comision
    form_class = ComisionForm
    template_name = "account/comision-create-update.html"
    success_url = reverse_lazy('account:home')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['vakils'].widget.attrs.update({'class': 'vakil-raw-id'})
        form.fields['raees'].widget.attrs.update({'class': 'raees-raw-id'})
        return form


class ComisionView(LoginRequiredMixin, View):
    def get(self, request):
        comi = Comision.objects.all()
        return render(request, 'account/comision.html', {'comi': comi})


@login_required
def comision_edit(request, pk):
    commission = get_object_or_404(Comision, id=pk)
    if request.method == "POST":
        form = ComisionForm(request.POST, instance=commission)
        if form.is_valid():
            form.save()
            return redirect('account:comision')
    else:
        form = ComisionForm(instance=commission)
    return render(request, 'account/comision-create-update.html', {'form': form})


@login_required
def comision_delete(request, pk):
    commission = get_object_or_404(Comision, id=pk)
    if request.method == "POST":
        commission.delete()
        return redirect('account:comision')
    return render(request, 'account/comision_confirm_delete.html', {'commission': commission})


# --- ریاست ---
class Riyasatlist(LoginRequiredMixin, ListView):
    template_name = "account/riyasat_list.html"
    model = Riyasat


@login_required
def add_riyasat(request):
    if request.method == 'POST':
        form = RaeesForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'عضو هیئت مدیره با موفقیت اضافه شد!')
            return redirect('account:home')
    else:
        form = RaeesForm()
    vakils = Vakil.objects.all()
    return render(request, 'account/add_riyasat.html', {'form': form, 'vakils': vakils})

class RiyasatDeleteView(LoginRequiredMixin, DeleteView):
    model = Riyasat
    success_url = reverse_lazy('account:riyasat_list')
    template_name = 'account/riyasat_confirm_delete.html'


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

@login_required()
def assign_thumbnails(request) :
    # دریافت تمام وکلا
    vakils = Vakil.objects.all()

    # مسیر پوشه عکس‌ها
    images_dir = os.path.join(settings.MEDIA_ROOT, 'images')

    # لیست تمام فایل‌های موجود در پوشه عکس‌ها
    image_files = os.listdir(images_dir) if os.path.exists(images_dir) else []

    updated_count = 0

    for vakil in vakils :
        if vakil.code :  # اگر شماره پروانه وجود دارد
            # جستجوی عکس با شماره پروانه (با پسوندهای مختلف)
            for ext in ['.jpg','.JPG','.jpeg', '.png','.PNG'] :
                image_name = f"{vakil.code}{ext}"
                if image_name in image_files :
                    # ساخت مسیر نسبی برای فایل
                    relative_path = f"images/{image_name}"

                    # بررسی اینکه آیا عکس فعلی با عکس جدید متفاوت است
                    if not vakil.thumbnail or vakil.thumbnail.name != relative_path :
                        vakil.thumbnail = relative_path
                        vakil.save()
                        updated_count += 1
                    break

    return render(request, 'account/assign_thumbnails.html', {
        'updated_count' : updated_count,
        'total_vakils' : vakils.count()
    })
@login_required()
def assign_karamooz_thumbnails(request) :
    # دریافت تمام وکلا
    karamoozs = Karamooz.objects.all()

    # مسیر پوشه عکس‌ها
    images_dir = os.path.join(settings.MEDIA_ROOT, 'images/karamozan')

    # لیست تمام فایل‌های موجود در پوشه عکس‌ها
    image_files = os.listdir(images_dir) if os.path.exists(images_dir) else []

    updated_count = 0

    for karamooz in karamoozs :
        if karamooz.code :  # اگر شماره پروانه وجود دارد
            # جستجوی عکس با شماره پروانه (با پسوندهای مختلف)
            for ext in ['.jpg', '.jpeg', '.png'] :
                image_name = f"{karamooz.code}{ext}"
                if image_name in image_files :
                    # ساخت مسیر نسبی برای فایل
                    relative_path = f"images/karamozan/{image_name}"

                    # بررسی اینکه آیا عکس فعلی با عکس جدید متفاوت است
                    if not karamooz.thumbnail or karamooz.thumbnail.name != relative_path :
                        karamooz.thumbnail = relative_path
                        karamooz.save()
                        updated_count += 1
                    break

    return render(request, 'account/assign_thumbnails_karamoozan.html', {
        'updated_count' : updated_count,
        'total_karamoozs' : karamoozs.count()
    })
