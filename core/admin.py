from django.contrib import admin
from .models import Expense, UserProfile, PlannedExpense  # <-- PlannedExpense add kiya

admin.site.register(Expense)
admin.site.register(UserProfile)
admin.site.register(PlannedExpense)  