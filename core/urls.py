from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # --- AUTHENTICATION & PROFILE ---
    path('signup/', views.signup, name='signup'),
    path('select-currency/', views.select_currency, name='select_currency'),
    path('profile/', views.profile_view, name='profile'),
    path('logout/', views.logout_view, name='user_logout'),

    # --- ✅ FIXED PASSWORD RESET FLOW (Using Custom View Classes) ---
    # Ab ye auth_views ki jagah seedhe aapke views.py ki classes ko call karega
    # 1. User email dalta hai
    path('forgot-password/', 
         views.MyPasswordResetView.as_view(), 
         name='password_reset'),
    
    # 2. Email bhejne ke baad ka confirmation
    path('forgot-password/sent/', 
         views.MyPasswordResetDoneView.as_view(), 
         name='password_reset_done'),
    
    # 3. Email link par click karne ke baad naya password set karne ka page
    path('reset/<uidb64>/<token>/', 
         views.MyPasswordResetConfirmView.as_view(), 
         name='password_reset_confirm'),
    
    # 4. Password change hone ke baad ka success page
    path('reset/done/', 
         views.MyPasswordResetCompleteView.as_view(), 
         name='password_reset_complete'),

    # --- DASHBOARD & EXPENSE ACTIONS ---
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add-expense/', views.add_expense, name='add_expense'),
    path('edit-expense/<int:pk>/', views.edit_expense, name='edit_expense'),
    path('delete-expense/<int:pk>/', views.delete_expense, name='delete_expense'),
    
    # --- CORE FINANCIAL FEATURES ---
    path('records/', views.records_view, name='records'),
    path('planned-payments/', views.planned_payments, name='planned_payments'),
    path('investments/', views.investments_view, name='investments'),
    path('budgets-goals/', views.budgets_goals, name='budgets_goals'),
    path('delete-goal/<int:pk>/', views.delete_goal, name='delete_goal'),
    path('premium/', views.premium_view, name='premium'),
    path('bank-sync/', views.bank_sync_view, name='bank_sync'),
    path('delete-bank/<int:pk>/', views.delete_bank, name='delete_bank'),
    path('export-csv/', views.export_expenses_csv, name='export_expenses_csv'),
    path('expense-report/', views.expense_report, name='expense_report'),
    path('update-budget/', views.update_budget, name='update_budget'),

    # --- NOTIFICATION CENTER ---
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/delete/<int:pk>/', views.delete_notification, name='delete_notification'),

    # --- TOOLS & AI (FINBOT) ---
    path('tools/emi-calculator/', views.emi_calculator, name='emi_calculator'),
    path('tools/finbot/', views.finbot_view, name='finbot'),
    path('currency-rates/', views.currency_rates_view, name='currency_rates'),

    # --- EXTRA FEATURES (PLACEHOLDERS) ---
    path('wallet-business/', views.placeholder_view, {'feature': 'Wallet for Business'}, name='wallet_business'),
    path('loyalty-cards/', views.placeholder_view, {'feature': 'Loyalty Cards'}, name='loyalty_cards'),
    path('group-sharing/', views.placeholder_view, {'feature': 'Group Sharing'}, name='group_sharing'),
]