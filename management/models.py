from django.db import models
from account.models import CustomUser
from nepalmap.models import District,Municipality,Province
import hashlib
from django.core.validators import FileExtensionValidator,MaxLengthValidator,MaxValueValidator
from .choices import status,priority

# Create your models here.
class ComplainBroadCategory(models.Model):
    english_name=models.CharField(max_length=50,unique=True)
    nepali_name=models.CharField(max_length=100,unique=True)
    def __str__(self):
        return self.english_name
class ComplainCategory(models.Model):
    category_name=models.CharField(max_length=60,unique=True)
    nepali_name=models.CharField(max_length=200,null=True)

    def __str__(self):
        return self.category_name

class ComplainSubCategory(models.Model):
    name=models.CharField(max_length=60,unique=True)
    nepali_name=models.CharField(max_length=100, null=True)
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
    ticket_no=models.CharField(max_length=20)
    broad_category= models.ForeignKey(ComplainBroadCategory,on_delete=models.CASCADE,related_name='broad_category',null=True)
    complain_category = models.ForeignKey(ComplainCategory,on_delete=models.CASCADE,related_name='complain',null=True)
    complain_sub_category=models.ForeignKey(ComplainSubCategory,on_delete=models.CASCADE,null=True,related_name='complain_sub_category')
    complain_title=models.CharField(max_length=300)
    complain_description=models.TextField()
    complain_image=models.ImageField()
    province=models.ForeignKey(Province,on_delete=models.SET_NULL,related_name='complain_province',null=True)
    district=models.ForeignKey(District,on_delete=models.SET_NULL,related_name='complain_district',null=True)
    municipality=models.ForeignKey(Municipality,on_delete=models.SET_NULL,related_name='complain_municipality',null=True)
    ward_no=models.CharField(max_length=5)
    tole=models.CharField(max_length=30,null=True)
    complain_status=models.PositiveBigIntegerField(choices=status,default=1)
    complain_priority=models.PositiveBigIntegerField(choices=priority,default=1)
    created_by=models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True,related_name='user_complains')
    assigned_by=models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True,related_name='assigned_complain')
    assigned_to=models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True,related_name='is_available')
    assigned_date=models.DateTimeField(blank=True,null=True)
    is_anonymous=models.OneToOneField(AnonymousUser, null=True, on_delete=models.CASCADE)
    complain_secrecy=models.BooleanField(default=False)
    complain_video=models.FileField(upload_to='complain-video/', null=True, blank=True,
                                    validators=[
                                        FileExtensionValidator(allowed_extensions=['mp4', 'avi', 'mov']),
                                        MaxValueValidator(100 * 1024 * 1024, message='File size must be no more than 100 MB.'),
        ])
    def __str__(self):
        return self.complain_title
    def save(self, *args, **kwargs):
        if not self.ticket_no:
            broad_category_id = self.broad_category.id if self.broad_category else 'NA'
            complain_id = Complain.objects.count() + 1
            encrypted_id = hashlib.md5(str(complain_id).encode()).hexdigest()[:4]
            self.ticket_no = f'DFTQC-C{broad_category_id}-{encrypted_id}'

        super(Complain, self).save(*args, **kwargs)
    def get_status(self):
        if self.complain_status == 1:
            return 'Pending'
        elif self.complain_status == 3:
            return 'Responded'
        elif self.complain_status == 4:
            return "Rejected"
        else:
            return 'Processing'
        
    def get_priority(self):
        if self.complain_priority == 1:
            return 'Normal'
        elif self.complain_priority == 2:
            return 'Urgent'
        else:
            return 'Very Urgent'
    
    class Meta:
        ordering=['-id']
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