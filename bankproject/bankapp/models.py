from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Customer(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    phone = models.CharField(max_length=11, unique=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=5000.00)

    def __str__(self):
        return self.user.username