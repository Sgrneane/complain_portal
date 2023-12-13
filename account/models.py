from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

class CustomUser(AbstractUser):
    username = models.CharField(max_length=255,unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(
        max_length=10, null=False, 
        validators=[
            RegexValidator(r'^\d{10}$', 'Phone number must be 10 digits')
        ]
    )
    created_date=models.DateTimeField(auto_now_add=True)
    USER=1
    ADMIN=2
    SUPERADMIN=3
    COMPLAIN_REVIEWER=4
    ROLE_CHOICES=(
        (USER,'USER'),
        (ADMIN,'ADMIN'),
        (SUPERADMIN,'SUPERADMIN'),
        (COMPLAIN_REVIEWER,'COMPLAIN REVIEWER')
    )
    role = models.PositiveSmallIntegerField(
        choices=ROLE_CHOICES, blank=True, default=1
    )
    USERNAME_FIELD='email'
    REQUIRED_FIELDS=['username',]
    
    def __str__(self) -> str:
        return self.email
    
    def role_name(self):
        if self.role==1:
            return 'user'
        elif self.role==2:
            return 'admin'
        elif self.role==3:
            return 'superadmin'
        elif self.role==4:
            return 'Complain Reviewer'
