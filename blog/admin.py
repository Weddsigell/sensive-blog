from django.contrib import admin
from blog.models import Post, Tag, Comment


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_absolute_url', 'text', 'image', 'published_at', 'author')
    raw_id_fields = ("likes", 'tags')


class CommentAdmin(admin.ModelAdmin):
    list_display = ('text', 'published_at')
    raw_id_fields = ("author", 'post')


admin.site.register(Post, PostAdmin)
admin.site.register(Tag)
admin.site.register(Comment, CommentAdmin)
