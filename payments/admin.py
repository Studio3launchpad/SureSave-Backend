from django.contrib import admin

from .models import Card
@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('card_holder_name', 'card_number', 'is_default', 'created_at')
    search_fields = ('card_holder_name', 'card_number')
    list_filter = ('is_default', 'created_at')
