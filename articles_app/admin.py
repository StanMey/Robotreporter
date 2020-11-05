from django.contrib import admin
from .models import Stocks, Articles, Observations, Comment

admin.site.register(Stocks)
admin.site.register(Observations)
admin.site.register(Articles)


# add the comment section and build function to approve comments
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'body', 'article', 'created_on', 'active')
    list_filter = ('active', 'created_on')
    search_fields = ('author', 'body')
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(active=True)
