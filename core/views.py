from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
import csv
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth import views as auth_views # ✅ Custom classes ke liye zaroori hai
from django.db.models import Sum
from django.contrib import messages
import json
import random
from datetime import datetime, date
import requests

from .models import (
    Expense, UserProfile, PlannedExpense, Goal,
    Investment, BankConnection, Notification
)
from .forms import (
    SignUpForm, ExpenseForm, BudgetForm, ProfileUpdateForm,
    CurrencySelectionForm, GoalForm, PlannedExpenseForm,
    InvestmentForm, BankSyncForm
)
from .utils import extract_data_from_receipt

# --- ✅ CUSTOM PASSWORD RESET VIEWS (To kill the black Admin page) ---
# Ye classes wahi templates uthayengi jo humne banaye hain.
class MyPasswordResetView(auth_views.PasswordResetView):
    template_name = 'registration/password_reset_form.html'

class MyPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'registration/password_reset_done.html'

class MyPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'

class MyPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'registration/password_reset_complete.html'


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('select_currency')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def select_currency(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = CurrencySelectionForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Currency set successfully!')
            return redirect('dashboard')
    else:
        form = CurrencySelectionForm(instance=profile)
    return render(request, 'select_currency.html', {'form': form})


@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    total_receipts = Expense.objects.filter(user=request.user).count()
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            user = request.user
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        initial_data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email
        }
        form = ProfileUpdateForm(instance=profile, initial=initial_data)
    context = {
        'form': form,
        'user': request.user,
        'total_receipts': total_receipts,
        'currency_symbol': profile.currency
    }
    return render(request, 'profile.html', context)


@login_required
def update_budget(request):
    if request.method == 'POST':
        new_budget = request.POST.get('monthly_budget')
        if new_budget:
            profile = request.user.userprofile
            profile.monthly_budget = new_budget
            profile.save()
            messages.success(request, 'Monthly Budget Updated!')
            if 'budgets-goals' in request.META.get('HTTP_REFERER', ''):
                return redirect('budgets_goals')
            return redirect('dashboard')
    return redirect('dashboard')


@login_required
def dashboard(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if not profile.currency:
        return redirect('select_currency')
    expenses = Expense.objects.filter(user=request.user).order_by('-expense_date', '-id')
    
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    search_category = request.GET.get('category')
    
    if start_date:
        expenses = expenses.filter(expense_date__gte=start_date)
    if end_date:
        expenses = expenses.filter(expense_date__lte=end_date)
    if search_category:
        expenses = expenses.filter(category__icontains=search_category)
    
    total_spent = expenses.aggregate(Sum('amount'))['amount__sum'] or 0.00
    total_receipts = expenses.count()
    
    current_month = datetime.now().month
    current_year = datetime.now().year
    month_spent = Expense.objects.filter(
        user=request.user,
        expense_date__month=current_month,
        expense_date__year=current_year
    ).aggregate(Sum('amount'))['amount__sum'] or 0.00
    
    budget_limit = profile.monthly_budget
    budget_percent = (float(month_spent) / float(budget_limit)) * 100 if float(budget_limit) > 0 else 0
    
    if budget_percent < 50:
        bar_color = 'bg-success'
    elif budget_percent < 85:
        bar_color = 'bg-warning'
    else:
        bar_color = 'bg-danger'
    
    category_data = expenses.values('category').annotate(total=Sum('amount'))
    categories = [item['category'] for item in category_data if item['category']]
    amounts = [float(item['total']) for item in category_data if item['category']]
    
    daily_data = expenses.values('expense_date').annotate(total=Sum('amount')).order_by('expense_date')
    dates = [item['expense_date'].strftime('%Y-%m-%d') for item in daily_data if item['expense_date']]
    daily_amounts = [float(item['total']) for item in daily_data if item['expense_date']]
    
    tips = [
        'A budget is telling your money where to go instead of wondering where it went.',
        'Beware of little expenses. A small leak will sink a great ship.',
        'Track every penny, because every penny counts!',
        'Save first, spend later.',
        'Do not save what is left after spending, but spend what is left after saving.'
    ]
    daily_tip = random.choice(tips)
    
    try:
        planned_expenses = PlannedExpense.objects.filter(
            user=request.user, due_date__gte=date.today()
        ).order_by('due_date')[:3]
    except Exception:
        planned_expenses = []
        
    currency_symbols = {'INR': '₹', 'USD': '$', 'EUR': '€', 'GBP': '£'}
    currency_symbol = currency_symbols.get(profile.currency, profile.currency)
    
    context = {
        'expenses': expenses,
        'planned_expenses': planned_expenses,
        'total_spent': round(total_spent, 2),
        'total_receipts': total_receipts,
        'month_spent': round(month_spent, 2),
        'budget_limit': budget_limit,
        'budget_percent': round(budget_percent),
        'bar_color': bar_color,
        'categories': json.dumps(categories),
        'amounts': json.dumps(amounts),
        'dates': json.dumps(dates),
        'daily_amounts': json.dumps(daily_amounts),
        'daily_tip': daily_tip,
        'currency_symbol': currency_symbol,
        'start_date': start_date,
        'end_date': end_date,
        'search_category': search_category,
    }
    return render(request, 'dashboard.html', context)


@login_required
def add_expense(request):
    form = ExpenseForm()
    if request.method == 'POST':
        if 'receipt_image' in request.FILES and not request.POST.get('amount'):
            image_file = request.FILES['receipt_image']
            scanned_data = extract_data_from_receipt(image_file)
            form = ExpenseForm(initial={
                'amount': scanned_data.get('amount'),
                'category': scanned_data.get('category'),
                'expense_date': scanned_data.get('date')
            })
            messages.info(request, f"Invoice Scanned! Amount Found: {scanned_data.get('amount')}. Verify & Save.")
            return render(request, 'add_expense.html', {'form': form, 'scanned_data': scanned_data})
        else:
            form = ExpenseForm(request.POST, request.FILES)
            if form.is_valid():
                expense = form.save(commit=False)
                expense.user = request.user
                expense.save()
                
                profile = request.user.userprofile
                current_month = datetime.now().month
                current_year = datetime.now().year
                month_spent = Expense.objects.filter(
                    user=request.user,
                    expense_date__month=current_month,
                    expense_date__year=current_year
                ).aggregate(Sum('amount'))['amount__sum'] or 0
                
                if float(profile.monthly_budget) > 0 and float(month_spent) > float(profile.monthly_budget):
                    excess = float(month_spent) - float(profile.monthly_budget)
                    msg = f"Alert: You have exceeded your monthly budget by {excess} {profile.currency}!"
                    Notification.objects.create(user=request.user, message=msg)
                    messages.warning(request, msg)
                else:
                    messages.success(request, f'Expense of {expense.amount} added successfully.')
                return redirect('dashboard')
    return render(request, 'add_expense.html', {'form': form})


@login_required
def edit_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense Updated Successfully!')
            return redirect('dashboard')
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'add_expense.html', {'form': form, 'edit_mode': True})


@login_required
def delete_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        expense.delete()
        messages.warning(request, 'Expense Deleted.')
        return redirect('dashboard')
    return render(request, 'delete_expense.html', {'expense': expense})


@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'notifications.html', {'notifications': notifications})


@login_required
def delete_notification(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.delete()
    messages.success(request, 'Notification deleted!')
    return redirect('notifications')


@login_required
def export_expenses_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="my_expenses.csv"'
    writer = csv.writer(response)
    writer.writerow(['Date', 'Category', 'Amount'])
    expenses = Expense.objects.filter(user=request.user).values_list('expense_date', 'category', 'amount')
    for expense in expenses:
        writer.writerow(expense)
    return response


@login_required
def expense_report(request):
    expenses = Expense.objects.filter(user=request.user).order_by('-expense_date')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date:
        expenses = expenses.filter(expense_date__gte=start_date)
    if end_date:
        expenses = expenses.filter(expense_date__lte=end_date)
    total_spent = expenses.aggregate(Sum('amount'))['amount__sum'] or 0.00
    total_transactions = expenses.count()
    category_data = expenses.values('category').annotate(total=Sum('amount')).order_by('-total')
    context = {
        'expenses': expenses,
        'total_spent': total_spent,
        'total_transactions': total_transactions,
        'category_data': category_data,
        'today': datetime.now(),
        'start_date': start_date,
        'end_date': end_date
    }
    return render(request, 'expense_report.html', context)


@login_required
def budgets_goals(request):
    goals = Goal.objects.filter(user=request.user)
    if request.method == 'POST':
        form = GoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            messages.success(request, 'New Goal Set!')
            return redirect('budgets_goals')
    else:
        form = GoalForm()
    currency_symbols = {'INR': '₹', 'USD': '$', 'EUR': '€', 'GBP': '£'}
    profile = request.user.userprofile
    currency = currency_symbols.get(profile.currency, profile.currency)
    context = {'goals': goals, 'form': form, 'currency': currency, 'user': request.user}
    return render(request, 'budgets_goals.html', context)


@login_required
def delete_goal(request, pk):
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    goal.delete()
    messages.warning(request, 'Goal Deleted.')
    return redirect('budgets_goals')


@login_required
def records_view(request):
    expenses = Expense.objects.filter(user=request.user).order_by('-expense_date')
    return render(request, 'records.html', {'expenses': expenses})


@login_required
def planned_payments(request):
    payments = PlannedExpense.objects.filter(user=request.user).order_by('due_date')
    if request.method == 'POST':
        form = PlannedExpenseForm(request.POST)
        if form.is_valid():
            plan = form.save(commit=False)
            plan.user = request.user
            plan.save()
            messages.success(request, 'Payment Scheduled!')
            return redirect('planned_payments')
    else:
        form = PlannedExpenseForm()
    return render(request, 'planned_payments.html', {'payments': payments, 'form': form})


@login_required
def investments_view(request):
    investments = Investment.objects.filter(user=request.user)
    total_invested = investments.aggregate(Sum('amount'))['amount__sum'] or 0
    if request.method == 'POST':
        form = InvestmentForm(request.POST)
        if form.is_valid():
            inv = form.save(commit=False)
            inv.user = request.user
            inv.save()
            messages.success(request, 'Investment Added!')
            return redirect('investments')
    else:
        form = InvestmentForm()
    return render(request, 'investments.html', {
        'investments': investments,
        'form': form,
        'total_invested': total_invested
    })


@login_required
def premium_view(request):
    return render(request, 'premium.html')


@login_required
def bank_sync_view(request):
    linked_banks = BankConnection.objects.filter(user=request.user)
    if request.method == 'POST':
        form = BankSyncForm(request.POST)
        if form.is_valid():
            bank = form.save(commit=False)
            bank.user = request.user
            bank.balance = random.randint(5000, 500000)
            bank.save()
            messages.success(request, f'Successfully connected to {bank.bank_name}!')
            return redirect('bank_sync')
    else:
        form = BankSyncForm()
    return render(request, 'bank_sync.html', {'form': form, 'linked_banks': linked_banks})


@login_required
def delete_bank(request, pk):
    bank = get_object_or_404(BankConnection, pk=pk, user=request.user)
    bank.delete()
    messages.warning(request, 'Bank account disconnected.')
    return redirect('bank_sync')


@login_required
def placeholder_view(request, feature):
    context = {
        'feature_name': feature,
        'message': f'The {feature} module is currently under development.'
    }
    return render(request, 'placeholder.html', context)


@login_required
def emi_calculator(request):
    return render(request, 'emi_calculator.html')


@login_required
def finbot_view(request):
    profile = request.user.userprofile
    expenses = Expense.objects.filter(user=request.user)
    total_spent = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    budget = profile.monthly_budget
    balance = float(budget) - float(total_spent)
    last_expense = expenses.order_by('-expense_date').first()
    last_expense_text = f'{last_expense.category} ({last_expense.amount})' if last_expense else 'None'
    user_name = getattr(profile, 'full_name', None) or request.user.username
    context = {
        'user_name': user_name,
        'total_spent': total_spent,
        'budget': budget,
        'balance': balance,
        'last_expense': last_expense_text,
        'currency': profile.currency
    }
    return render(request, 'finbot.html', context)


@login_required
def currency_rates_view(request):
    url = 'https://api.exchangerate-api.com/v4/latest/USD'
    data = {}
    last_updated = ''
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            result = response.json()
            rates = result.get('rates', {})
            data = {
                'INR (Indian Rupee)': rates.get('INR'),
                'EUR (Euro)': rates.get('EUR'),
                'GBP (British Pound)': rates.get('GBP'),
            }
        else:
            messages.error(request, 'Failed to fetch live rates.')
    except Exception:
        messages.error(request, 'Error: Internet required!')
    return render(request, 'currency_rates.html', {'rates': data})


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('login')