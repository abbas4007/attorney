from django.contrib.auth import views
from django.urls import path
from django.conf.urls import include


from .views import (
    ArticleList,
    article_create_view,
    ArticleUpdate,
CustomLoginView,
CategoryCreateView,CategoryDeleteView,CategoryListView,CategoryUpdateView,
    ArticleDelete,
    delete_article_image
)

app_name = 'account'

urlpatterns = [
	path('', ArticleList.as_view(), name="home"),
    path('article/update/<int:pk>', ArticleUpdate.as_view(), name="article_update"),
    path('article/create/', article_create_view, name="article_create"),
	path('article/delete/<int:pk>', ArticleDelete.as_view(), name="article_delete"),
    path('login/', CustomLoginView.as_view(), name = 'login'),
    path('delete-article-image/<int:image_id>/', delete_article_image, name='delete-article-image'),
    path('categories/', CategoryListView.as_view(), name = 'category_list'),
    path('categories/add/', CategoryCreateView.as_view(), name = 'category_add'),
    path('categories/edit/<int:pk>/', CategoryUpdateView.as_view(), name = 'category_edit'),
    path('categories/delete/<int:pk>/', CategoryDeleteView.as_view(), name = 'category_delete'),

]