from django.shortcuts import render,HttpResponse,get_object_or_404,get_list_or_404,redirect
from django.db.models import Count
from django.contrib import messages
from django.urls import reverse
from django.db.models import Q
from datetime import datetime
from django.utils import timezone
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from .models import ComplainCategory,ComplainSubCategory, AnonymousUser,Complain, Communication, Response,ComplainBroadCategory, FAQ
from account.models import CustomUser
from .forms import AnonymousForm,ComplainBroadCategoryForm,ComplainCategoryForm,ComplainSubCategoryForm, FAQForm
from nepalmap.models import Province,District,Municipality
from django.core.mail import send_mail
from django.template.loader import render_to_string
from account.decorators import authentication_not_required,is_admin,is_superadmin,is_user, is_employee
from django.contrib.auth.decorators import login_required
from .tasks import send_notification_mail

# Create your views here.
def index(request):
    total_complains=Complain.objects.count()
    food_and_beverage_count=Complain.objects.filter(broad_category__english_name='Food and Beverages').count()
    hotel_and_restaurant_count=Complain.objects.filter(broad_category__english_name='Hotel and Restaurants').count()
    feed_count=Complain.objects.filter(broad_category__english_name='Feed').count()
    service_count=Complain.objects.filter(broad_category__english_name='Service Delivery').count()
    others_count=Complain.objects.filter(broad_category__english_name='Others').count()
    context={
        'total_complains':total_complains,
        'food_and_beverage_count': food_and_beverage_count,
        'hotel_and_restaurant_count':hotel_and_restaurant_count,
        'feed_count':feed_count,
        'service_count':service_count,
        'others_count':others_count,

    }
    return render(request,'management/index.html',context)

def user_dashboard(request):
    user=request.user
    if user.role == 3:
        total_complains=Complain.objects.filter(created_by=user).count()
        food_and_beverage_count=Complain.objects.filter(Q(broad_category__english_name='Food and Beverages') &
                                                        Q(created_by=user)).count()
        hotel_and_restaurant_count=Complain.objects.filter(Q(broad_category__english_name='Hotel and Restaurants') &
                                                           Q(created_by=user)).count()
        feed_count=Complain.objects.filter(Q(broad_category__english_name='Feed') &
                                           Q(created_by=user)).count()
        service_count=Complain.objects.filter(Q(broad_category__english_name='Service Delivery') &
                                              Q(created_by=user)).count()
        others_count=Complain.objects.filter(Q(broad_category__english_name='Others') &
                                             Q(created_by=user)).count()
        pending_complains_count=Complain.objects.filter(Q(complain_status=1) &
                                                        Q(created_by=user)).count()
        processing_complains_count=Complain.objects.filter(Q(complain_status=2) & 
                                                           Q(created_by=user)).count()
        responded_complains_count=Complain.objects.filter(Q(complain_status=3) &
                                                          Q(created_by=user)).count()
        rejected_complains_count=Complain.objects.filter(Q(complain_status=4) &
                                                         Q(created_by=user)).count()
    else:
        total_complains=Complain.objects.count()
        food_and_beverage_count=Complain.objects.filter(broad_category__english_name='Food and Beverages').count()
        hotel_and_restaurant_count=Complain.objects.filter(broad_category__english_name='Hotel and Restaurants').count()
        feed_count=Complain.objects.filter(broad_category__english_name='Feed').count()
        service_count=Complain.objects.filter(broad_category__english_name='Service Delivery').count()
        others_count=Complain.objects.filter(broad_category__english_name='Others').count()
        pending_complains_count=Complain.objects.filter(complain_status=1).count()
        processing_complains_count=Complain.objects.filter(complain_status=2).count()
        responded_complains_count=Complain.objects.filter(complain_status=3).count()
        rejected_complains_count=Complain.objects.filter(complain_status=4).count()
    context={
        'total_complains':total_complains,
        'food_and_beverage_count': food_and_beverage_count,
        'hotel_and_restaurant_count':hotel_and_restaurant_count,
        'feed_count':feed_count,
        'service_count':service_count,
        'others_count':others_count,
        'pending_complains_count':pending_complains_count,
        'processing_complains_count':processing_complains_count,
        'responded_complains_count':responded_complains_count,
        'rejected_complains_count':rejected_complains_count,
    }
    return render(request,'dashboard.html',context)


#Category and Broad category related Views.
@is_superadmin
def create_broad_category(request,id=None):
    context=None
    if id:
        broad_category=ComplainBroadCategory.objects.get(id=id)
        context={
            'broad_category':broad_category
        }
    if request.method== 'POST':
        form=ComplainBroadCategoryForm(request.POST)
        if id:
            broad_category=ComplainBroadCategory.objects.get(id=id)
            name=form.data['english_name']
            nepali_name=form.data['nepali_name']
            broad_category.english_name=name
            broad_category.nepali_name=nepali_name
            broad_category.save()
            messages.info(request,"Category Updated Syccessfully.")
            return redirect(reverse('management:category_list'))
        else:
            if form.is_valid():
                form.save()
                return redirect('management:category_list')
            else:
                messages.error(request,"Category Not created! Please fill all required fields.")
                return redirect(reverse('management:create_broad_category'))
    else:
        return render(request,'management/add_broadcategory.html',context)
    

    
def category_list(request):
    broad_categories=ComplainBroadCategory.objects.all()
    sub_categories=ComplainSubCategory.objects.all()
    categories = ComplainCategory.objects.all()
    context={
        'categories':categories,
        'broad_categories':broad_categories,
        'sub_categories': sub_categories
    }
    return render(request,'management/category_list.html',context)


@is_superadmin
def create_category(request,id=None):
    sub_categories=ComplainSubCategory.objects.all()

    if id:
        category=ComplainCategory.objects.get(id=id)
    else:
        category=None
    if request.method =='POST':
        form=ComplainCategoryForm(request.POST)
        category_sub_categories = request.POST.getlist('sub_categories')
        selected_sub_categories = ComplainSubCategory.objects.filter(id__in=category_sub_categories)
        if id:
            #for editing Purpose
            category=ComplainCategory.objects.get(id=id)
            category_name=form.data['category_name']
            nepali_name= form.data['nepali_name']
            category.category_name=category_name
            category.nepali_name=nepali_name
            category.save()
            category.sub_category.clear()
            category.sub_category.add(*selected_sub_categories)
            messages.info(request,"Category Updated Successfully")
            return redirect(reverse('management:category_list'))
        else:
            if form.is_valid():
                category_name=form.cleaned_data['category_name']
                nepali_name= form.cleaned_data['nepali_name']
                complain_category,created=ComplainCategory.objects.get_or_create(
                    category_name=category_name,
                    nepali_name=nepali_name,
                )
                complain_category.sub_category.add(*selected_sub_categories)
            
                return redirect('management:category_list')
            else:
                messages.error(request,"please fill the form correctly.")
                return redirect(reverse('management:create_category'))
    else:
        context={
            'sub_categories':sub_categories,
            'category':category,
        }
        return render(request,'management/add_category.html',context)
    

@is_superadmin
def create_sub_category(request,id=None):
    categories=ComplainCategory.objects.all()
    if id:
        sub_category=ComplainSubCategory.objects.get(id=id)
    else:
        sub_category=None
    context={
        'categories':categories,
        'sub_category':sub_category
    }
    if request.method=='POST':
        form=ComplainSubCategoryForm(request.POST)
        if id:
            sub_category=ComplainSubCategory.objects.get(id=id)
            sub_category_name=form.data['name']
            nepali_name=form.data['nepali_name']
            sub_category.name=sub_category_name
            sub_category.nepali_name=nepali_name
            sub_category.save()
            messages.info(request,"Sub Category has been Updated Successfully.")
            return redirect(reverse('management:category_list'))
        else:
            if form.is_valid():
                sub_category_name=form.cleaned_data['name']
                nepali_name=form.cleaned_data['nepali_name']
                ComplainSubCategory.objects.create(
                    name=sub_category_name,
                    nepali_name=nepali_name,
                )
                messages.info(request,"Sub Category has been created Successfully.")
                return redirect('management:category_list')
            else:
                messages.error(request,'Please fill all fields to create subcategory.')
                return redirect(reverse('management:add_subcategory'))
    else:
        return render(request,'management/add_subcategory.html',context)
@is_superadmin
def delete_category(request,id):
    category=ComplainCategory.objects.get(id=id)
    category.delete()
    messages.info(request,"Category has been deleted Successfully.")
    return redirect(reverse('management:category_list'))
@is_superadmin
def delete_broad_category(request,id):
    broad_category=ComplainBroadCategory.objects.get(id=id)
    broad_category.delete()
    messages.info(request,"Broad Category has been deleted Successfully.")
    return redirect(reverse('management:category_list'))
@is_superadmin
def delete_sub_category(request,id):
    sub_category=ComplainSubCategory.objects.get(id=id)
    sub_category.delete()
    messages.info(request,"Sub Category has been deleted Successfully.")
    return redirect(reverse('management:category_list'))
def get_subcategories(request, category_id):
    # complain_category=ComplainCategory.objects.get(id=category_id)
    # sub=ComplainSubCategory.objects.all()
    subcategories = ComplainCategory.objects.get(id=category_id).sub_category.all()
    print(subcategories)
    data = [{'id': sub.id, 'name': sub.nepali_name} for sub in subcategories]
    return JsonResponse(data, safe=False)

#Anonymous Complain related views
def anonymous_complain(request):
    complain_broad_category=ComplainBroadCategory.objects.all()
    provinces=Province.objects.all()
    context={
            'complain_category': complain_broad_category,
            'provinces': provinces
            }
    complaints_today = request.session.get('complaints_today', [])  
    if len(complaints_today) >= 2:
        return redirect(reverse('management:limit_reached'))  
            
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
            complain_province=int(request.POST.get('province',None))
            complain_district=int(request.POST.get('district',None))
            complain_municipality=int(request.POST.get('municipality',None))
            complain_province=Province.objects.get(id=complain_province)
            complain_district=District.objects.get(id=complain_district)
            complain_municipality=Municipality.objects.get(id=complain_municipality)
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
            current_date_str = datetime.now().date().isoformat()
            complaints_today.append(current_date_str)
            request.session['complaints_today'] = complaints_today
            request.session.save()
            mail_context={
                'complain_obj':complain_obj,
            }
            admin_users=CustomUser.objects.filter(role =1)
            email_lists=[admin_user.email for admin_user in admin_users]
            html_content = render_to_string('management/mail_template.html',mail_context)
            try:
                for email in email_lists:
                    send_notification_mail.delay(email,html_content)    
            finally:
                messages.info(request,f"<strong>Success!</strong> Your Complain has been registered successfully.<br> Save and search the complain token <Strong>{complain_obj.ticket_no}</strong> for further information.")
                return redirect(reverse('management:index'))
        else:
            additional_context={
                'form':form,
            }
            context.update(additional_context)
            print(form.errors)
            return render(request,"management/anonymous_complain.html",context)
    else:
        return render(request,'management/anonymous_complain.html',context)

@is_user
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
        complain_province=int(request.POST.get('province',None))
        complain_district=int(request.POST.get('district',None))
        complain_municipality=int(request.POST.get('municipality',None))
        complain_province=Province.objects.get(id=complain_province)
        complain_district=District.objects.get(id=complain_district)
        complain_municipality=Municipality.objects.get(id=complain_municipality)
        complain_ward=request.POST.get('ward',None)
        complain_tole=request.POST.get('tole',None)
        complain_description=request.POST.get('complain_description',None)
        complain_secrecy=request.POST.get('secrecy',None)
        if(complain_secrecy=='1'):
            secrecy=False
        else:
            secrecy=True
        complain_image=request.FILES.get('complain_image',None)
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
        mail_context={
                'complain_obj':complain_obj,
            }
        admin_users=CustomUser.objects.filter(role =1)
        email_lists=[admin_user.email for admin_user in admin_users]
        html_content = render_to_string('management/mail_template.html',mail_context)
        try:
            for email in email_lists:
                send_notification_mail.delay(email,html_content)
        finally:
            return redirect(reverse('management:all_complains'))
    return render(request,'management/create_complain.html',context)

@login_required
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

@login_required
def view_complain(request,id):
    complain=get_object_or_404(Complain,id=id)
    complain_broad_categories=ComplainBroadCategory.objects.all()
    complain_categories=ComplainCategory.objects.all()
    complain_reviewers=get_list_or_404(CustomUser, role=2)
    context={
        'complain_categories':complain_categories,
        'complain':complain,
        'complain_reviewers':complain_reviewers,
        'complain_broad_categories':complain_broad_categories,
    }
    if request.method=='POST':
        if 'forward_button' in request.POST:
            admin_message=request.POST.get('admin_message',None)
            assigned_to=int(request.POST.get('assigned_to',None))
            image=request.FILES.get('communication_image',None)
            if not complain.complain_category:
                complain_broad_category=int(request.POST.get('complain_broad_category'))
                complain_category=int(request.POST.get('complain_category',None))
                complain_sub_category=int(request.POST.get('complain_sub_category',None))
                complain_broad_category_instance=ComplainBroadCategory.objects.get(id=complain_broad_category)
                complain_category_instance=ComplainCategory.objects.get(id=complain_category)
                complain_sub_category_instance=ComplainSubCategory.objects.get(id=complain_sub_category)
                complain.broad_category=complain_broad_category_instance
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


@is_employee
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
        mail_context={
            'complain_obj':complain,
        }
        admin_users=CustomUser.objects.filter(role =1)
        html_content = render_to_string('management/mail_template.html',mail_context)
        try:
            send_notification_mail.delay(communication_to.email,html_content)
        finally:
            return redirect("management:view_complain",id=complain.id)
@is_superadmin  
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

def search_complain(request):
    if request.method=='POST':
        search=request.POST['search']
        try:
            complain=Complain.objects.get(ticket_no=search)
        except ObjectDoesNotExist:
            complain = None
        if complain:
            context={
                'complain':complain
            }
            return render(request,'management/search.html',context)
        else:
            messages.info(request,f"<strong>Sorry!</strong> Complain with this ticket number({search}) doesn't exist.")
            return redirect(reverse('management:index'))
        
def index_categories(request):
    broad_categories=ComplainBroadCategory.objects.all()
    context={
        'broad_categories':broad_categories,
    }
    return render(request,'management/index_categories.html',context)  


def all_faqs(request):
    faqs=FAQ.objects.all()
    context={
        'faqs':faqs
    }
    return render(request,'management/faqs_list.html',context)
def index_faq(request):
    faqs=FAQ.objects.all()
    context={
        'faqs':faqs
    }
    return render(request,'management/index_faq.html',context)
def create_faq(request):
    if request.method=='POST':
        form=FAQForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('management:all_faqs'))
        else:
            messages.info(request,'Please fill form correctly')
            return redirect(reverse('management:create_faq'))
    
    return render(request,'management/create_faq.html')

def limit_reached(request):
    return render(request,'management/limit_reached.html')




