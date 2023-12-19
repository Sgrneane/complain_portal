from rest_framework import serializers
from .models import Complain
class ComplainSerializer(serializers.ModelSerializer):
    complain_status = serializers.SerializerMethodField()
    complain_priority = serializers.SerializerMethodField()
    complain_category=serializers.SerializerMethodField()
    complain_sub_category=serializers.SerializerMethodField()
    fullname=serializers.SerializerMethodField()
    phone_number=serializers.SerializerMethodField()
    address=serializers.SerializerMethodField()
    class Meta:
        model=Complain
        fields= '__all__'
    def get_complain_status(self, obj):
        return obj.get_status()

    def get_complain_priority(self, obj):
        return obj.get_priority()
    def get_complain_category(self,obj):
        return obj.complain_category.category_name
    def get_complain_sub_category(self,obj):
        return obj.complain_sub_category.name
    
    def is_registered(self,obj):
        if obj.created_by==None:
            return False
        else:
            return True
    if is_registered==True:
        def get_fullname(self,obj):
            return (obj.created_by.first_name+" "+obj.created_by.last_name)
        def get_phone_number(self,obj):
            return obj.created_by.phone_number
        def get_address(self,obj):
            return obj.created_by.address
    else:
        def get_fullname(self,obj):
            return (obj.is_anonymous.first_name+" "+obj.is_anonymous.last_name)
        def get_phone_number(self,obj):
            return (obj.is_anonymous.phone_number)
        def get_address(self,obj):
            return obj.is_anonymous.address
