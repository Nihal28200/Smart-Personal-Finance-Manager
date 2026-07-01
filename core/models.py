from django.db import models
from django.contrib.auth.models import User
from datetime import date

# ---------------------------------------------------------
# 1. WORLD CURRENCIES LIST
# ---------------------------------------------------------
CURRENCY_CHOICES = [
    ('INR', '🇮🇳 INR - Indian Rupee (₹)'),
    ('USD', '🇺🇸 USD - US Dollar ($)'),
    ('EUR', '🇪🇺 EUR - Euro (€)'),
    ('GBP', '🇬🇧 GBP - British Pound (£)'),
    ('JPY', '🇯🇵 JPY - Japanese Yen (¥)'),
    ('AUD', '🇦🇺 AUD - Australian Dollar (A$)'),
    ('CAD', '🇨🇦 CAD - Canadian Dollar (C$)'),
    ('CNY', '🇨🇳 CNY - Chinese Yuan (¥)'),
    ('AED', '🇦🇪 AED - UAE Dirham (د.إ)'),
    ('SAR', '🇸🇦 SAR - Saudi Riyal (﷼)'),
    ('RUB', '🇷🇺 RUB - Russian Ruble (₽)'),
    ('KRW', '🇰🇷 KRW - South Korean Won (₩)'),
    ('BRL', '🇧🇷 BRL - Brazilian Real (R$)'),
    ('PKR', '🇵🇰 PKR - Pakistani Rupee (₨)'),
    ('BDT', '🇧🇩 BDT - Bangladeshi Taka (৳)'),
]

# ---------------------------------------------------------
# 2. USER PROFILE MODEL
# ---------------------------------------------------------
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Personal Details
    profile_pic = models.ImageField(upload_to='profile_pics', blank=True, null=True)
    full_name = models.CharField(max_length=100, blank=True, default='')
    phone = models.CharField(max_length=50, blank=True, default='')
    
    bio = models.TextField(blank=True, default='')
    
    # Financial Settings
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='INR')
    monthly_budget = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    # Legacy field support
    target_currency = models.CharField(max_length=10, blank=True, null=True) 

    def __str__(self):
        return f"{self.user.username}'s Profile"

# ---------------------------------------------------------
# 3. EXPENSE MODEL
# ---------------------------------------------------------
class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    category = models.CharField(max_length=100, default='General')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    expense_date = models.DateField(default=date.today)
    receipt_image = models.ImageField(upload_to='receipts/', blank=True, null=True)
    currency = models.CharField(max_length=3, default='INR', blank=True)

    def __str__(self):
        return f"{self.category} - {self.amount}"

# ---------------------------------------------------------
# 4. PLANNED EXPENSE MODEL (Upcoming Payments)
# ---------------------------------------------------------
class PlannedExpense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, default='Planned Expense')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    due_date = models.DateField(default=date.today)
    
    def __str__(self):
        return f"{self.title} - {self.amount}"

# ---------------------------------------------------------
# 5. GOAL MODEL 
# ---------------------------------------------------------
class Goal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)  # e.g., "Buy iPhone"
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    deadline = models.DateField(null=True, blank=True)
    
    def progress_percent(self):
        if self.target_amount > 0:
            return int((self.current_amount / self.target_amount) * 100)
        return 0

    def __str__(self):
        return self.name
    
# ---------------------------------------------------------
# 6. INVESTMENT MODEL
# ---------------------------------------------------------
class Investment(models.Model):
    INVESTMENT_TYPES = [
        ('Stock', 'Stocks/Share Market'),
        ('MF', 'Mutual Funds'),
        ('Crypto', 'Crypto Currency'),
        ('Gold', 'Gold/Silver'),
        ('FD', 'Fixed Deposit'),
        ('RealEstate', 'Real Estate'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100) 
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.CharField(max_length=20, choices=INVESTMENT_TYPES, default='Stock')
    invest_date = models.DateField(default=date.today)
    return_rate = models.FloatField(default=0.0, help_text="Expected Return %")

    def __str__(self):
        return f"{self.name} ({self.category})"

# ---------------------------------------------------------
# 7. BANK CONNECTION MODEL 
# ---------------------------------------------------------
class BankConnection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bank_name = models.CharField(max_length=100)
    country = models.CharField(max_length=50)
    account_number = models.CharField(max_length=20, default="**** 1234") 
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    last_synced = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.bank_name} ({self.country})"

# ---------------------------------------------------------
# 8. NOTIFICATION MODEL (NEW FEATURE)
# ---------------------------------------------------------
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username} - {self.created_at.strftime('%d %b')}"