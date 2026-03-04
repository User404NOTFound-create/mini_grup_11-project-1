from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404
from .models import Article, ArticleCategory
from .serializers import ArticleSerializer, ArticleCategorySerializer


# ============ ARTICLE VIEWS ============

class ArticleListCreateView(generics.ListCreateAPIView):
    """
    GET: Barcha articlarni ro'yxatini olish
    POST: Yangi article yaratish
    """
    queryset = Article.objects.all().order_by('-created')
    serializer_class = ArticleSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by category
        category_id = self.request.query_params.get('category', None)
        if category_id:
            queryset = queryset.filter(category__id=category_id)

        # Search by title
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(title__icontains=search)

        return queryset


class ArticleRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Bitta articleni o'qish
    PUT/PATCH: Articleni yangilash
    DELETE: Articleni o'chirish
    """
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    lookup_field = 'id'

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            # Update va delete uchun faqat o'z articlari yoki admin
            if self.request.user.is_staff:
                return Article.objects.all()
            return Article.objects.filter(author=self.request.user)
        return Article.objects.all()

    def perform_update(self, serializer):
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"message": "Article muvaffaqiyatli o'chirildi"},
            status=status.HTTP_200_OK
        )


# ============ CATEGORY VIEWS ============

class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = ArticleCategory.objects.all()
    serializer_class = ArticleCategorySerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]  # Faqat admin kategoriya qo'sha oladi


class CategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ArticleCategory.objects.all()
    serializer_class = ArticleCategorySerializer
    lookup_field = 'id'

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]  # Faqat admin o'zgartira oladi