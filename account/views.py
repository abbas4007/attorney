from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View

from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView
)
from home.models import Article


# Create your views here.
class ArticleList(ListView):
    model = Article
    paginate_by = 6
    template_name = "account/home.html"



class ArticleCreate(CreateView):
    model = Article
    fields =  '__all__'
    template_name = "account/article-create-update.html"
    success_url = reverse_lazy('account:home')



class ArticleUpdate(UpdateView):
    model = Article
    template_name = "account/article-create-update.html"
    fields =  '__all__'

class ArticleDelete(DeleteView):
    model = Article
    success_url = reverse_lazy('account:home')
    template_name = "account/article_confirm_delete.html"
