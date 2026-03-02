from django.db import models
from django.contrib.auth import get_user_model
from .base_model import BaseModel
from .article_category import ArticleCategory

User = get_user_model()

class Article(BaseModel):
    thumbnail = models.ImageField(upload_to='articles/thumbnails/')
    title = models.CharField(max_length=255, unique=True)
    date = models.DateField(auto_now_add=True)
    description = models.TextField()

    category = models.ManyToManyField(ArticleCategory, related_name='articles', blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles')

    def __str__(self):
        return self.title