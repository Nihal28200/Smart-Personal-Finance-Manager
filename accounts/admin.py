from django.contrib import admin
from .models import LoginHistory

@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_time', 'ip_address', 'user_agent_short') # Columns
    list_filter = ('date_time', 'user') # Sidebar Filters
    search_fields = ('user__username', 'ip_address') # Search Bar
    readonly_fields = ('user', 'date_time', 'ip_address', 'user_agent') # Edit block

    def user_agent_short(self, obj):
        return obj.user_agent[:50] + '...' if obj.user_agent else '-'
    user_agent_short.short_description = 'Browser Info'