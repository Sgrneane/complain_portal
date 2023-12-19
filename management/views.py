from django.shortcuts import render,HttpResponse,get_object_or_404,get_list_or_404,redirect
from django.db.models import Count
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.http import JsonResponse
from .models import ComplainCategory,ComplainSubCategory, AnonymousUser,Complain, Communication, Response,ComplainBroadCategory
from account.models import CustomUser
from .forms import AnonymousForm,ComplainBroadCategoryForm,ComplainCategoryForm,ComplainSubCategoryForm
from nepalmap.models import Province,District,Municipality

# Create your views here.
def index(request):
    categories_with_counts = ComplainBroadCategory.objects.annotate(complaint_count=Count('broad_category'))
    return render(request,'management/index.html')

def user_dashboard(request):
    if request.user.role==1:
        categories_with_counts = ComplainBroadCategory.objects.annotate(complaint_count=Count('broad_category'))
        for category in categories_with_counts:
            print(category.english_name,category.complaint_count)
    if request.user.role==3:
        categories_with_counts = ComplainBroadCategory.objects.filter(broad_category__created_by=request.user).annotate(complaint_count=Count('broad_category'))
        for category in categories_with_counts:
            print(category.english_name,category.complaint_count)
    context={
        'a':5
    }
    return render(request,'dashboard.html',context)

#Category and Broad category related Views.
def create_broad_category(request):
    if request.method== 'POST':
        form=ComplainBroadCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('management:category_list')
        else:
            messages.error(request,"Category Not created! Please fill all required fields.")
            return redirect(reverse('management:create_borad_category'))
    else:
        return render(request,'management/add_broadcategory.html')
    
def category_list(request):
    broad_categories=ComplainBroadCategory.objects.all()
    sub_categories=ComplainSubCategory.objects.all()
    categories = ComplainCategory.objects.prefetch_related('complainsubcategories').all()
    context={
        'categories':categories,
        'broad_categories':broad_categories,
        'sub_categories': sub_categories
    }
    return render(request,'management/category_list.html',context)
def create_category(request):
    if request.method =='POST':
        form=ComplainCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('management:category_list')
        else:
            messages.error(request,"please fill the form correctly.")
            return redirect(reverse('management:add_category'))
    else:
        return render(request,'management/add_category.html')

def create_sub_category(request):
    categories=ComplainCategory.objects.all()
    context={
        'categories':categories
    }
    if request.method=='POST':
        form=ComplainSubCategoryForm(request.POST)
        if form.is_valid():
            sub_category_name=form.cleaned_data['name']
            category=form.cleaned_data['category']
            ComplainSubCategory.objects.create(
                name=sub_category_name,
                category=category,
            )
            return redirect('management:category_list')
        else:
            messages.error(request,'Please fill all fields to create subcategory.')
            return redirect(reverse('management:add_subcategory'))
    else:
        return render(request,'management/add_subcategory.html',context)

def delete_category(request,id):
    category=ComplainCategory.objects.get(id=id)
    category.delete()
    return redirect(reverse('management:category_list'))

def delete_broad_category(request,id):
    broad_category=ComplainBroadCategory.objects.get(id=id)
    broad_category.delete()
    return redirect(reverse('management:category_list'))

def delete_sub_category(request,id):
    sub_category=ComplainSubCategory.objects.get(id=id)
    sub_category.delete()
    return redirect(reverse('management:category_list'))
def get_subcategories(request, category_id):
    subcategories = ComplainSubCategory.objects.filter(category_id=category_id)
    data = [{'id': sub.id, 'name': sub.name} for sub in subcategories]
    return JsonResponse(data, safe=False)

#Anonymous Complain related views
def anonymous_complain(request):
    complain_broad_category=ComplainBroadCategory.objects.all()
    provinces=Province.objects.all()
    context={
            'complain_category': complain_broad_category,
            'provinces': provinces
            }
            
    if request.method == 'POST':
        form=AnonymousForm(request.POST,request.FILES)
        if form.is_valid():
            person_first_name=form.cleaned_data['first_name']
            person_last_name=form.cleaned_data['last_name']
            person_phone_number=form.cleaned_data['phone_number']
            person_address=form.cleaned_data['person_address']
            complain_broad_category=int(request.POST.get('complain_broad_category',None))
            complain_title=form.cleaned_data['complain_title']
            complain_priority=int(request.POST.get('priority',None))
            complain_province=request.POST.get('province',None)
            complain_district=request.POST.get('district',None)
            complain_municipality=request.POST.get('municipality',None)
            complain_ward=request.POST.get('ward',None)
            complain_tole=request.POST.get('tole',None)
            complain_description=form.cleaned_data['complain_description']
            complain_secrecy=request.POST.get('secrecy',None)
            if(complain_secrecy=='1'):
                secrecy=False
            else:
                secrecy=True
            complain_image=form.cleaned_data['complain_image']
            complain_broad_category_instance=ComplainBroadCategory.objects.get(id=complain_broad_category)
            anonymous_object={
            "first_name":person_first_name,
            "last_name": person_last_name,
            "phone_number":person_phone_number,
            "address":person_address
            }
            complain={
                "broad_category":complain_broad_category_instance,
                "complain_title": complain_title,
                "complain_description":complain_description,
                "province":complain_province,
                "district":complain_district,
                "municipality": complain_municipality,
                "ward_no": complain_ward,
                "tole":complain_tole,
                "complain_image": complain_image,
                "complain_priority":complain_priority,
                "complain_secrecy":secrecy,
            }
            user_info=AnonymousUser.objects.create(**anonymous_object)
            complain_obj=Complain.objects.create(is_anonymous=user_info,**complain)
            return render(request,'management/success.html')
        else:
            additional_context={
                'form':form,
            }
            context.update(additional_context)
            print(form.errors)
            return render(request,"management/anonymous_complain.html",context)
    else:
        return render(request,'management/anonymous_complain.html',context)


def create_complain(request):
    user=request.user
    complain_broad_category=ComplainBroadCategory.objects.all()
    provinces=Province.objects.all()
    context={
            'complain_category': complain_broad_category,
            'provinces': provinces
            }
    if request.method == 'POST':
        complain_broad_category=int(request.POST.get('complain_broad_category',None))
        complain_title=request.POST.get('complain_title',None)
        complain_priority=int(request.POST.get('priority',None))
        complain_province=request.POST.get('province',None)
        complain_district=request.POST.get('district',None)
        complain_municipality=request.POST.get('municipality',None)
        complain_ward=request.POST.get('ward',None)
        complain_tole=request.POST.get('tole',None)
        complain_description=request.POST.get('complain_description',None)
        complain_secrecy=request.POST.get('secrecy',None)
        if(complain_secrecy=='1'):
            secrecy=False
        else:
            secrecy=True
        complain_image=request.FILES['complain_image']
        complain_broad_category_instance = ComplainBroadCategory.objects.get(id=complain_broad_category)
        complain={
            "broad_category":complain_broad_category_instance,
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
        return redirect(reverse('management:all_complains'))
    return render(request,'management/create_complain.html',context)

def all_complains(request):
    user=request.user
    if user.role == 1:
        complains=Complain.objects.all()
        pending_complains=Complain.objects.filter(complain_status = 1)
        processing_complains=Complain.objects.filter(complain_status=2)
        responded_complains=Complain.objects.filter(complain_status=3)
    if user.role == 2:
        complains=Complain.objects.filter(assigned_to = user)
        pending_complains=Complain.objects.filter(assigned_to = user,complain_status=1 )
        processing_complains=Complain.objects.filter(assigned_to = user, complain_status=2)
        responded_complains=Complain.objects.filter(assigned_to = user,complain_status=3)
    if user.role == 3:
        complains=Complain.objects.filter(created_by=user)
        pending_complains=Complain.objects.filter(created_by=user,complain_status=1)
        processing_complains=Complain.objects.filter(created_by = user, complain_status=2)
        responded_complains=Complain.objects.filter(created_by = user,complain_status=3)
    context={
        'complains':complains,
        'pending_complains':pending_complains,
        'processing_complains': processing_complains,
        'responded_complains': responded_complains
    }
    return render(request,'management/complain_list.html',context)

def view_complain(request,id):
    complain=get_object_or_404(Complain,id=id)
    complain_categories=ComplainCategory.objects.all()
    complain_reviewers=get_list_or_404(CustomUser, role=2)
    context={
        'complain_categories':complain_categories,
        'complain':complain,
        'complain_reviewers':complain_reviewers,
    }
    if request.method=='POST':
        if 'forward_button' in request.POST:
            admin_message=request.POST.get('admin_message',None)
            assigned_to=int(request.POST.get('assigned_to',None))
            image=request.FILES.get('communication_image',None)
            if not complain.complain_category:
                complain_category=int(request.POST.get('complain_category',None))
                complain_sub_category=int(request.POST.get('complain_sub_category',None))
                complain_category_instance=ComplainCategory.objects.get(id=complain_category)
                complain_sub_category_instance=ComplainSubCategory.objects.get(id=complain_sub_category)
                complain.complain_category=complain_category_instance
                complain.complain_sub_category=complain_sub_category_instance
            customuser_instance=CustomUser.objects.get(id=assigned_to)
            complain.assigned_to=customuser_instance
            complain.assigned_by=request.user
            complain.complain_status=2
            
            complain.assigned_date=timezone.now()
            if admin_message:
                Communication.objects.create(
                    complain=complain,
                    communication_from=request.user,
                    communication_to=customuser_instance,
                    message=admin_message,
                    image=image
                )
            complain.save()
            return redirect('management:view_complain',id=complain.id)
    return render(request,'management/view_complain.html',context)



def create_communication(request,id):
    complain=get_object_or_404(Complain,id=id)
    if request.method =='POST':
        message=request.POST.get('communication_message')
        image=request.FILES.get('communication_image',None)
        if request.user.role == 2:
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
        return redirect("management:view_complain",id=complain.id)
    
def response(request,id):
    user=request.user
    complain=Complain.objects.get(id=id)
    if request.method=='POST':
        message=request.POST.get('response_message',None)
        image=request.FILES.get('response_image',None)
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
        return redirect(reverse('management:all_complains'))
    return redirect(reverse('management:all_complains'))
        
        