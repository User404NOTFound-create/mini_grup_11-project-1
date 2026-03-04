from django.urls import path
from . import views

urlpatterns = [

    path('articles/',
         views.ArticleListCreateView.as_view(),
         name='article-list-create'),

    path('articles/<uuid:id>/',
         views.ArticleRetrieveUpdateDestroyView.as_view(),
         name='article-detail'),


    path('categories/',
         views.CategoryListCreateView.as_view(),
         name='category-list-create'),

    path('categories/<uuid:id>/',
         views.CategoryRetrieveUpdateDestroyView.as_view(),
         name='category-detail'),
]