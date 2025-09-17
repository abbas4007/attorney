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
    success_page,MessageUpdateView,MessageListView,delete_article_image,refresh_captcha,MessageDetailView
)

app_name = 'account'

urlpatterns = [
	path('', ArticleList.as_view(), name="home"),

    path('article/update/<int:pk>', ArticleUpdate.as_view(), name="article_update"),
	path('article/delete/<int:pk>', ArticleDelete.as_view(), name="article_delete"),
    path('login/', CustomLoginView.as_view(), name = 'login'),
    path('refresh-captcha/', refresh_captcha, name='refresh_captcha'),
    path('contact/success/', success_page, name = 'success_page'),
    path('messages/', MessageListView.as_view(), name = 'message_list'),
    path('messages/<int:pk>/', MessageDetailView.as_view(), name = 'message_detail'),
    path('admin/messages/<int:pk>/', MessageUpdateView.as_view(), name = 'message_update'),
    path('delete-article-image/<int:image_id>/', delete_article_image, name='delete-article-image'),
    path('categories/', CategoryListView.as_view(), name = 'category_list'),
    path('categories/add/', CategoryCreateView.as_view(), name = 'category_add'),
    path('categories/edit/<int:pk>/', CategoryUpdateView.as_view(), name = 'category_edit'),
    path('categories/delete/<int:pk>/', CategoryDeleteView.as_view(), name = 'category_delete'),

]