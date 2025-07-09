from django.conf import settings
from django.db import models

# Create your models here.

class Order(models.Model):
    STATUS_PENDING = 'PENDING'
    STATUS_DELIVERED = 'DELIVERED'
    STATUS_COMPLETE = 'COMPLETE'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_DELIVERED, 'Delivered'),
        (STATUS_COMPLETE, 'Complete'),
    ]

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='orders',
        on_delete=models.CASCADE,
    )
    delivery_man = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='assigned_orders',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    description = models.TextField()
    address = models.CharField(max_length=255)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id}" 