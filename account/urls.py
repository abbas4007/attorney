from django.contrib.auth import views
from django.urls import path
from django.conf.urls import include


from .views import (
    ArticleList,
    KarAmoozList,
    article_create_view,
    ArticleUpdate,
    ArticleDelete,
    AddVakil,
    vakileList,
    Riyasatlist,
    vakil_image_view,
    add_comision,
    KarAmoozUpdateView,
    search_vakils,
    assign_karamooz_thumbnails,
    karamooz_image_view,
    assign_thumbnails,
    AddKarAmooz, CustomLoginView, ComisionView, VakilUpdateView, VakilDeleteView, RiyasatDeleteView,CategoryListView,CategoryCreateView,CategoryUpdateView,CategoryDeleteView,
    add_riyasat, comision_edit, comision_delete, KarAmoozDeleteView,success_page,MessageUpdateView,MessageListView,delete_article_image,refresh_captcha,MessageDetailView
)
from home.views import VakilExcelUploadView,KaramoozExcelUploadView
app_name = 'account'

urlpatterns = [
	path('', ArticleList.as_view(), name="home"),
	path('vakillist/', vakileList.as_view(), name="vakil_list"),
	path('karamoozlist/', KarAmoozList.as_view(), name="karamooz_list"),
    path('vakil/edit/<int:pk>/', VakilUpdateView.as_view(), name = 'vakil_edit'),
    path('karamooz/edit/<int:pk>/', KarAmoozUpdateView.as_view(), name = 'karamooz_edit'),
    path('vakil/delete/<int:pk>/', VakilDeleteView.as_view(), name = 'vakil_delete'),
    path('karamooz/delete/<int:pk>/', KarAmoozDeleteView.as_view(), name = 'karamooz_delete'),
	path('riyasatlist/', Riyasatlist.as_view(), name="riyasat_list"),
	path('addvakil/', AddVakil.as_view(), name="vakil_add"),
	path('addkaramooz/', AddKarAmooz.as_view(), name="karamooz_add"),
    path('add-riyasat/', add_riyasat, name = 'add_riyasat'),
    path('addcomision/', add_comision, name="comision_add"),
    path('article/create/', article_create_view, name="create_article"),
    path('comision/', ComisionView.as_view(), name = "comision"),
    path('article/update/<int:pk>', ArticleUpdate.as_view(), name="article_update"),
	path('article/delete/<int:pk>', ArticleDelete.as_view(), name="article_delete"),
    path('image_upload/<int:id>/', vakil_image_view.as_view(), name = 'image_upload'),
    path('karamooz_image_upload/<int:id>/', karamooz_image_view.as_view(), name = 'karamooz_image_upload'),
    path('login/', CustomLoginView.as_view(), name = 'login'),
    path('assign-thumbnails/', assign_thumbnails, name = 'assign_thumbnails'),
    path('assign-thumbnails-karamooz/', assign_karamooz_thumbnails, name = 'assign_thumbnails_karamooz'),
    path('comision/edit/<int:pk>/', comision_edit, name='comision_edit'),
    path('comision/delete/<int:pk>/', comision_delete, name='comision_delete'),
    path('riyasat/delete/<int:pk>/', RiyasatDeleteView.as_view(), name = 'riyasat_delete'),
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
    path('upload-excel/', VakilExcelUploadView.as_view(), name = 'upload_excel'),
	path('upload-excel_karamooz/', KaramoozExcelUploadView.as_view(), name = 'upload_excel_karamooz'),
    path('search-vakils/', search_vakils, name='search-vakils'),

]