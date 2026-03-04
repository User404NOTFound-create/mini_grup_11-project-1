from rest_framework import serializers
from .models import Article, ArticleCategory


class ArticleCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleCategory
        fields = ['id', 'name', 'created', 'modified']


class ArticleSerializer(serializers.ModelSerializer):
    category_names = serializers.SerializerMethodField()
    author_username = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Article
        fields = [
            'id', 'thumbnail', 'title', 'date', 'description',
            'category', 'category_names', 'author', 'author_username',
            'created', 'modified'
        ]
        read_only_fields = ['author', 'date']

    def get_category_names(self, obj):
        return [category.name for category in obj.category.all()]

    def create(self, validated_data):
        categories = validated_data.pop('category', [])
        article = Article.objects.create(**validated_data)
        article.category.set(categories)
        return article

    def update(self, instance, validated_data):
        categories = validated_data.pop('category', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if categories is not None:
            instance.category.set(categories)

        instance.save()
        return instance