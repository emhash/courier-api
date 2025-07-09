from django.contrib.auth.models import AbstractUser
from django.db import models

ROLES= (
    ('admin', 'Admin'),
    ('delivery_man', 'Delivery Man'),
    ('user', 'User'),
)

class User(AbstractUser):
    role = models.CharField(max_length=20, choices=ROLES, default="user")
    
    def __str__(self):
        return f"{self.email} ({self.role})"
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def is_delivery_man(self):
        return self.role == 'delivery_man'
    
    @property
    def is_regular_user(self):
        return self.role == 'user'