from django.db import models
from django.urls import reverse


class Author(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=40)

    def __str__(self) -> str:
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self) -> str:
        return self.name


class Article(models.Model):
    title = models.CharField(max_length=200)
    content =models.TextField(blank=True, null=True)
    # pub_date = models.DateTimeField(auto_now_add=True)
    pub_date = models.DateTimeField(blank=True, null=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='articles')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='categories')
    tags = models.ManyToManyField(Tag, blank=True, related_name='tags')

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self):
        return reverse("blogapp:article", kwargs={"pk": self.pk})
