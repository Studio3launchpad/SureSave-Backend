from django.contrib import admin

from .models import CustomUser, UserProfile, BVN

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'phone_number', 'is_verified', 'is_active', 'is_staff', 'role', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')
    list_filter = ('is_verified', 'is_active', 'is_staff', 'role')
    ordering = ('date_joined',)
    fieldsets = (
        (None, {'fields': ('email', 'first_name', 'last_name', 'phone_number', 'password')}),
        ('Permissions', {'fields': ('is_verified', 'is_active', 'is_staff', 'is_superuser', 'role', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'city', 'country', 'date_of_birth')
    search_fields = ('user__email', 'user__frist_name', 'user__last_name' 'city', 'country')
    list_filter = ('country',)
    ordering = ('user__date_joined',)
    fieldsets = (
        (None, {'fields': ('user', 'bio', 'profile_picture')}),
        ('Location Info', {'fields': ('address', 'city', 'state', 'zip_code', 'country', 'ip_address')}),
        ('Personal Info', {'fields': ('date_of_birth',)}),
    )

@admin.register(BVN)
class BvnModelAdmin(admin.ModelAdmin):
    list_display = ('user', 'bvn_number', 'is_verified', 'verified_at')
    search_fields = ('user__email', 'bvn')
    list_filter = ('is_verified',)
    ordering = ('user__date_joined',)
    fieldsets = (
        (None, {'fields': ('user', 'bvn')}),
        ('Verification Info', {'fields': ('is_verified', 'verified_at')}),
    )