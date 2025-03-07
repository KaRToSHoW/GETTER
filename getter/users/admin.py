from django.contrib import admin
from main.models import Review
from .models import User

class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    readonly_fields = ('product', 'rating', 'comment', 'created_at')

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('username', 'email', 'first_name', 'last_name')
    readonly_fields = ('last_login',)
    list_display_links = ('username',)
    inlines = [ReviewInline]