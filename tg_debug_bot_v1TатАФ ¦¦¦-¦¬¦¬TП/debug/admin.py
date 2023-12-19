from django.contrib import admin

from debug.models import User, Platform, Debug, Asnwering


class UserAdmin(admin.ModelAdmin):
    model = User
    list_display = (
        'id', 'iduser', 'username', 'name', 'is_admin')


class PlatformAdmin(admin.ModelAdmin):
    model = Platform
    list_display = (
        'id', 'user', 'name', 'url')


class DebugAdmin(admin.ModelAdmin):
    model = Debug
    list_display = (
        'id', 'platform', 'from_user', 'request_text', 'file', 'is_answered', 'answer')


class AsnweringAdmin(admin.ModelAdmin):
    model = Asnwering
    list_display = (
        'id', 'from_user', 'ans_user', 'problem')


admin.site.register(User, UserAdmin)
admin.site.register(Asnwering, AsnweringAdmin)
admin.site.register(Platform, PlatformAdmin)
admin.site.register(Debug, DebugAdmin)
