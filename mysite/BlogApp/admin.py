from django.contrib import admin

from BlogApp.models import Article, Tag, Category, Author

# admin.site.register(Article)
admin.site.register(Tag)
admin.site.register(Category)
admin.site.register(Author)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = "id", "title", "content", "pub_date", "author", "category"
