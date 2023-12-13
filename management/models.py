from django.db import models
from account.models import CustomUser

# Create your models here.
class ComplainCategory(models.Model):
    name=models.CharField(max_length=60,unique=True)

    def __str__(self):
        return self.name

class ComplainSubCategory(models.Model):
    name=models.CharField(max_length=60,unique=True)
    category=models.ForeignKey(ComplainCategory,on_delete=models.CASCADE,related_name='complainsubcategories')

    def __str__(self):
        return self.name

class AnonymousUser(models.Model):
    """Personal Information"""
    first_name=models.CharField(max_length=50,default='abc')
    last_name=models.CharField(max_length=50,null=True)
    phone_number=models.CharField(max_length=13)
    address=models.CharField(max_length=50,null=True)

    def __str__(self):
        return self.first_name
class Complain(models.Model):
    status=(
        (1,'Pending'),
        (2,'Processing'),
        (3,'Responsed')
    )
    priority=(
        (1,'Normal'),
        (2,'Urgent'),
        (3,'Very Urgent'),
    )
    ticket_no=models.CharField(max_length=20)
    complain_category = models.ForeignKey(ComplainCategory,on_delete=models.CASCADE,related_name='complain')
    complain_sub_category=models.ForeignKey(ComplainSubCategory,on_delete=models.CASCADE,null=True,related_name='complain_sub_category')
    complain_title=models.CharField(max_length=300)
    complain_description=models.TextField()
    complain_image=models.ImageField()
    province=models.CharField(max_length=20)
    district=models.CharField(max_length=2)
    municipality=models.CharField(max_length=20)
    ward_no=models.CharField(max_length=5)
    tole=models.CharField(max_length=30,null=True)
    complain_status=models.PositiveBigIntegerField(choices=status,default=1)
    complain_priority=models.PositiveBigIntegerField(choices=priority,default=1)
    created_by=models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True,related_name='user_complains')
    assigned_by=models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True,related_name='assigned_complain')
    assigned_to=models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True,related_name='is_available')
    is_anonymous=models.OneToOneField(AnonymousUser, null=True, on_delete=models.CASCADE)
    complain_secrecy=models.BooleanField(default=False)
    admin_message=models.CharField(max_length=200,null=True)

    def __str__(self):
        return self.complain_title
    def save(self, *args, **kwargs):
        if not self.ticket_no:
            category_id = self.complain_category.id if self.complain_category else 'NA'
            self.ticket_no = f'DFTQC-C{category_id}-{self.id}'

        super(Complain, self).save(*args, **kwargs)
    def get_status(self):
        if self.complain_status == 1:
            return 'Pending'
        elif self.complain_status == 3:
            return 'Responded'
        else:
            return 'Processing'
        
    def get_priority(self):
        if self.complain_priority == 1:
            return 'Normal'
        elif self.complain_priority == 2:
            return 'Urgent'
        else:
            return 'Very Urgent'
class Communication(models.Model):
    complain = models.ForeignKey(Complain,on_delete=models.CASCADE,related_name='complain_communication')
    communication_from =models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True,related_name='user_from')
    communication_to =models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True,related_name='user_to')
    message=models.TextField(null=True)
    image=models.ImageField(null=True)

class Response(models.Model):
    created_by=models.ForeignKey(CustomUser,on_delete=models.SET_NULL,null=True)
    response_description=models.TextField()
    complain=models.ForeignKey(Complain,on_delete=models.CASCADE,related_name='response')
    response_image=models.ImageField(null=True)