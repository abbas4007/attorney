
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.db.models import Q
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from home.models import Article, ArticleImage, ArticleFile, Category
from .forms import  ArticleForm,CategoryForm

from django.http import JsonResponse





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


