from django.contrib import admin

from .models import CustomUser, UserProfile

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'phone_number', 'is_verified', 'is_active', 'is_staff', 'role', 'date_joined')
    search_fields = ('email', 'full_name', 'phone_number')
    list_filter = ('is_verified', 'is_active', 'is_staff', 'role')
    ordering = ('date_joined',)
    fieldsets = (
        (None, {'fields': ('email', 'phone_number', 'full_name', 'password')}),
        ('Permissions', {'fields': ('is_verified', 'is_active', 'is_staff', 'is_superuser', 'role', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'city', 'country', 'date_of_birth')
    search_fields = ('user__email', 'user__full_name', 'city', 'country')
    list_filter = ('country',)
    ordering = ('user__date_joined',)
    fieldsets = (
        (None, {'fields': ('user', 'bio', 'profile_picture')}),
        ('Location Info', {'fields': ('address', 'city', 'state', 'zip_code', 'country')}),
        ('Personal Info', {'fields': ('date_of_birth',)}),
    )
