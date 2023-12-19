from django.db import models

# Create your models here.

class Province(models.Model):
    province_id = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=255, unique=True)
    nepali_name = models.CharField(max_length=255)
    longitude = models.CharField(max_length=255)
    latitude = models.CharField(max_length=255)
    area = models.IntegerField()
    population = models.IntegerField()
    
    def __str__(self):
        return self.name


class District(models.Model):
    district_id = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=255)
    nepali_name = models.CharField(max_length=255)
    longitude = models.CharField(max_length=255)
    latitude = models.CharField(max_length=255)
    headquarter = models.CharField(max_length=255)
    nepali_headquarter = models.CharField(max_length=255)
    province= models.ForeignKey(Province, on_delete=models.CASCADE, related_name='districts')
    
    def __str__(self):
        return self.name


class Municipality(models.Model):
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255, blank=True, null=True)
    district = models.ForeignKey('District', on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name


class City(models.Model):
    city_id = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=255)
    nepali_name = models.CharField(max_length=255, blank=True, null=True)
    district = models.ForeignKey('District', on_delete=models.CASCADE)
    province = models.ForeignKey('Province', on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name


