from django.shortcuts import render,HttpResponse,get_object_or_404,get_list_or_404,redirect
from django.http import JsonResponse
from .models import ComplainCategory,ComplainSubCategory, AnonymousUser,Complain, Communication, Response
from account.models import CustomUser

# Create your views here.
def index(request):
    return render(request,'management/index.html')

def user_dashboard(request):
    return render(request,'management/user_dashboard.html')

def category_list(request):
    categories = ComplainCategory.objects.prefetch_related('complainsubcategories').all()
    context={
        'categories':categories
    }
    return render(request,'management/category_list.html',context)
def create_category(request):
    if request.method =='POST':
        print('hello')
        category_name=request.POST.get('category_name', None)
        print(category_name)
        ComplainCategory.objects.create(
            name=category_name
        )
        return redirect('management:category_list')
    else:
        return render(request,'management/create_category.html')

def create_sub_category(request):
    categories=ComplainCategory.objects.all()
    context={
        'categories':categories
    }
    if request.method=='POST':
        sub_category_name=request.POST.get('sub_category_name',None)
        category=int(request.POST.get('category_id',None))
        print(category)
        category=ComplainCategory.objects.get(id=category)
        ComplainSubCategory.objects.create(
            name=sub_category_name,
            category=category,
        )
        return redirect('management:category_list')
    else:
        return render(request,'management/create_sub_category.html',context)


def get_subcategories(request, category_id):
    subcategories = ComplainSubCategory.objects.filter(category_id=category_id)
    data = [{'id': sub.id, 'name': sub.name} for sub in subcategories]
    return JsonResponse(data, safe=False)
def anonymous_complain(request):
    complain_category=ComplainCategory.objects.all()
    context={
        'complain_category': complain_category,
    }
    if request.method == 'POST':
        person_first_name=request.POST.get('first_name',None)
        person_last_name=request.POST.get('last_name',None)
        person_phone_number=request.POST.get('phone_number',None)
        person_address=request.POST.get('person_address',None)
        complain_category1=int(request.POST.get('complain_category',None))
        complain_sub_category=int(request.POST.get('complain_sub_category',None))
        complain_title=request.POST.get('complain_title',None)
        complain_priority=int(request.POST.get('priority',None))
        complain_province=request.POST.get('province',None)
        complain_district=request.POST.get('district',None)
        complain_municipality=request.POST.get('municipality',None)
        complain_ward=request.POST.get('ward',None)
        complain_tole=request.POST.get('tole',None)
        complain_description=request.POST.get('description',None)
        complain_secrecy=request.POST.get('secrecy',None)
        complain_image=request.FILES['complain_image']
        complain_category_instance = ComplainCategory.objects.get(id=complain_category1)
        complain_sub_category_instance=ComplainSubCategory.objects.get(id=complain_sub_category)
        anonymous_object={
            "first_name":person_first_name,
            "last_name": person_last_name,
            "phone_number":person_phone_number,
            "address":person_address
        }
        complain={
            "complain_category":complain_category_instance,
            "complain_sub_category": complain_sub_category_instance,
            "complain_title": complain_title,
            "complain_description":complain_description,
            "province":complain_province,
            "district":complain_district,
            "municipality": complain_municipality,
            "ward_no": complain_ward,
            "tole":complain_tole,
            "complain_image": complain_image,
            "complain_priority":complain_priority,
        }
        user_info=AnonymousUser.objects.create(**anonymous_object)
        complain_obj=Complain.objects.create(is_anonymous=user_info,**complain)
        return render(request,'management/success.html')

    return render(request,'management/anonymous-complain.html',context)


def create_complain(request):
    user=request.user
    complain_category=ComplainCategory.objects.all()
    context={
        'complain_category': complain_category,
    }
    if request.method == 'POST':
        complain_category1=int(request.POST.get('complain_category',None))
        complain_sub_category=int(request.POST.get('complain_sub_category',None))
        complain_title=request.POST.get('complain_title',None)
        complain_priority=int(request.POST.get('priority',None))
        complain_province=request.POST.get('province',None)
        complain_district=request.POST.get('district',None)
        complain_municipality=request.POST.get('municipality',None)
        complain_ward=request.POST.get('ward',None)
        complain_tole=request.POST.get('tole',None)
        complain_description=request.POST.get('description',None)
        complain_secrecy=request.POST.get('secrecy',None)
        if(complain_secrecy=='1'):
            secrecy=False
        else:
            secrecy=True
        complain_image=request.FILES['complain_image']
        complain_category_instance = ComplainCategory.objects.get(id=complain_category1)
        complain_sub_category_instance=ComplainSubCategory.objects.get(id=complain_sub_category)
        complain={
            "complain_category":complain_category_instance,
            "complain_sub_category": complain_sub_category_instance,
            "complain_title": complain_title,
            "complain_description":complain_description,
            "province":complain_province,
            "district":complain_district,
            "municipality": complain_municipality,
            "ward_no": complain_ward,
            "tole":complain_tole,
            "complain_image": complain_image,
            "complain_priority":complain_priority,
            "complain_secrecy":secrecy
        }
        complain_obj=Complain.objects.create(created_by=user,**complain)
        return render(request,'management/success.html')
    return render(request,'management/create_complain.html',context)

def all_complains(request):
    user=request.user
    if user.role == 3 or user.role == 2:
        complains=Complain.objects.all()
    if user.role == 4:
        complains=Complain.objects.filter(assigned_to = user)
    context={
        'complains':complains
    }
    return render(request,'management/complain_list.html',context)

def my_complains(request):
    complains=Complain.objects.filter(created_by=request.user)
    context={
        'complains':complains
    }
    return render(request,'management/my_complains.html',context)

def view_complain(request,id):
    complain=get_object_or_404(Complain,id=id)
    complain_reviewers=get_list_or_404(CustomUser, role=4)
    context={
        'complain':complain,
        'complain_reviewers':complain_reviewers,
    }
    if request.method=='POST':
        if 'forward_button' in request.POST:
            admin_message=request.POST.get('admin_message',None)
            assigned_to=int(request.POST.get('assigned_to',None))
            complain_category=request.POST.get('complain_category',None)
            complain_sub_category=request.POST.get('complain_sub_category',None)
            customuser_instance=CustomUser.objects.get(id=assigned_to)
            complain.admin_message=admin_message
            complain.assigned_to=customuser_instance
            complain.assigned_by=request.user
            complain.complain_status=2
            complain.save()
            return redirect('management:view_complain')
    return render(request,'management/view_complain.html',context)



def create_communication(request,id):
    complain=get_object_or_404(Complain,id=id)
    if request.method =='POST':
        message=request.POST.get('complain_message')
        image=request.POST.get('communication_image')
        if request.user.role == 4:
            communication_from=request.user
            communication_to=complain.assigned_by
        else:
            communication_from=complain.assigned_by
            communication_to=complain.assigned_to
        data={
            'complain':complain,
            'communication_from': communication_from,
            'communication_to':communication_to,
            'message':message,
            'image':image
        }
        Communication.objects.create(**data)
        return redirect("management:view_complain")
    
def response(request,id):
    user=request.user
    complain=Complain.objects.get(id=id)
    if request.method=='POST':
        message=request.POST.get('response_message',None)
        image=request.POST.get('response_image',None)
        if 'reject' in request.POST:
            complain.complain_status = 4
            complain.save()
        if 'response' in request.POST:
            complain.complain_status = 3
            complain.save()
        Response.objects.create(
                created_by=user,
                response_description=message,
                complain=complain,
                response_image=image,
            )
        return HttpResponse("responded")
        
        