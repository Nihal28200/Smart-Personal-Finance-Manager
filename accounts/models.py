from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from datetime import datetime

# --- 1. LOGIN HISTORY MODEL (Tracker) ---
class LoginHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_time = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, null=True, blank=True) # Browser Info

    def __str__(self):
        return f"{self.user.username} - {self.date_time}"

    class Meta:
        verbose_name_plural = "Login History"

# --- 2. SIGNAL (Jasoos + Terminal Alert) ---
@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    # IP Address nikalna
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    
    # Browser Info nikalna
    user_agent = request.META.get('HTTP_USER_AGENT', '')[:255]
    
    # Database mein save karna
    LoginHistory.objects.create(user=user, ip_address=ip, user_agent=user_agent)

    # 🔥 TERMINAL MEIN PRINT KARNA (Sirf aapko dikhega)
    print(f"\n{'='*40}")
    print(f"🕵️‍♂️  JASOOS ALERT: NEW LOGIN DETECTED!")
    print(f"👤 User: {user.username}")
    print(f"🌍 IP Address: {ip}")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*40}\n")