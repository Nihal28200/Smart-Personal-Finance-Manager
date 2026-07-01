from django import forms
from django.contrib.auth.models import User
# ✅ UPDATED IMPORTS: Saare models yahan hone chahiye
from .models import Expense, UserProfile, Goal, PlannedExpense, Investment, BankConnection

# ---------------------------------------------------------
# 1. SIGNUP FORM
# ---------------------------------------------------------
class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control', 
        'placeholder': '******'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control', 
        'placeholder': '******'
    }))

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose a username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'you@example.com'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match!")

# ---------------------------------------------------------
# 2. EXPENSE FORM
# ---------------------------------------------------------
class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['category', 'amount', 'expense_date', 'receipt_image']
        widgets = {
            'category': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Food, Travel'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
            'expense_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'receipt_image': forms.FileInput(attrs={'class': 'form-control'}),
        }

# ---------------------------------------------------------
# 3. BUDGET FORM
# ---------------------------------------------------------
class BudgetForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['monthly_budget']
        widgets = {
            'monthly_budget': forms.NumberInput(attrs={'class': 'form-control'}),
        }

# ---------------------------------------------------------
# 4. PROFILE UPDATE FORM
# ---------------------------------------------------------
class ProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'wa-input form-control', 
        'placeholder': 'Enter First Name'
    }))
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'wa-input form-control', 
        'placeholder': 'Enter Last Name'
    }))
    
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'wa-input form-control', 
        'readonly': 'readonly' 
    }))

    class Meta:
        model = UserProfile
        fields = ['profile_pic'] 
        widgets = {
            'profile_pic': forms.FileInput(attrs={'class': 'd-none', 'id': 'id_profile_pic'}),
        }

# ---------------------------------------------------------
# 5. CURRENCY FORM
# ---------------------------------------------------------
class CurrencySelectionForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['currency']
        widgets = {
            'currency': forms.Select(attrs={'class': 'form-select form-select-lg mb-3 shadow-sm border-2'}),
        }

# ---------------------------------------------------------
# 6. GOAL FORM
# ---------------------------------------------------------
class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ['name', 'target_amount', 'current_amount', 'deadline']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Goal Name (e.g. New Laptop)'}),
            'target_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Target Amount'}),
            'current_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Saved So Far'}),
            'deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

# ---------------------------------------------------------
# 7. PLANNED PAYMENT FORM (✅ Added)
# ---------------------------------------------------------
class PlannedExpenseForm(forms.ModelForm):
    class Meta:
        model = PlannedExpense
        fields = ['title', 'amount', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Electric Bill'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

# ---------------------------------------------------------
# 8. INVESTMENT FORM (✅ Added)
# ---------------------------------------------------------
class InvestmentForm(forms.ModelForm):
    class Meta:
        model = Investment
        fields = ['name', 'amount', 'category', 'invest_date', 'return_rate']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Investment Name'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Invested Amount'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'invest_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'return_rate': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Expected Return %'}),
        }

# ---------------------------------------------------------
# 9. BANK SYNC FORM (✅ Added - Ye missing tha!)
# ---------------------------------------------------------
class BankSyncForm(forms.ModelForm):
    class Meta:
        model = BankConnection
        fields = ['country', 'bank_name']
        widgets = {
            'country': forms.Select(choices=[
                ('India', '🇮🇳 India'),
                ('USA', '🇺🇸 USA'),
                ('UK', '🇬🇧 UK'),
                ('Canada', '🇨🇦 Canada'),
                ('UAE', '🇦🇪 UAE'),
            ], attrs={'class': 'form-select form-select-lg'}),
            
            'bank_name': forms.TextInput(attrs={
                'class': 'form-control form-control-lg', 
                'placeholder': 'Search your bank (e.g. HDFC, SBI)'
            }),
        }