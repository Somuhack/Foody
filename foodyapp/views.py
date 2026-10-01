from django.shortcuts import render,redirect
from django.http import HttpResponse
from .forms import RegistrationForm
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .models import Product,Category
from django.db.models import Q
from django.core.paginator import Paginator

# Create your views here.
def Home(request):
    # return HttpResponse("<h1>Hello Python 72</h1>")
   context={
        "batch":"Python 72",
        "name":"Somnath",
        "age":23,
        "hobbies":["Cooding","Gamming","research","reading"]
    }
   return render(request,"Home.html",context)
def Contact(request):
    address={
        "address":[
            {"name":"Somnath","city":"howrah","pin":289566,"conatct":980359836,"isIndian":True},
            {"name":"Gourav","city":"hoogly","pin":238866,"conatct":980359836,"isIndian":False},
            {"name":"Trisha","city":"kolkata","pin":278566,"conatct":980359836,"isIndian":False},
            {"name":"Shilpi","city":"Jalpaiguri","pin":265566,"conatct":980359836,"isIndian":True},
        ]
    }
    return render(request,"Contact.html",address)
def About(request):
    return render(request,"About.html")

def register(request):
    form=RegistrationForm(request.POST)
    if request.method=="POST":
        if form.is_valid():
            user=form.save()
            login(request,user)
            return redirect("home-page")
        else:
            return render(request,"register.html",{"form":form})
    return render(request,"register.html",{"form":form})
            
def login_view(request):
    form=AuthenticationForm()
    if(request.method=="POST"):
        form=AuthenticationForm(request,data=request.POST)
        if form.is_valid():
           user = form.get_user()
           login(request, user)
           return redirect('home-page')
        else:
            form=AuthenticationForm()
            
    return render(request,"login.html",{"form":form})
@login_required
def logout_page(request):
    if request.method=="POST":
        logout(request)
        return redirect('login-page')
    return redirect('home-page')
def Products_views(request):
    products=Product.objects.select_related("category").all() #Select * from Products;
    
    # Search
    search=request.get("search","")
    if search:
       products=products.filter(
           Q(name__icontains=search) |
           Q(description__icontains=search)
       )
    # Filter
    category = request.GET.get("category","")
    if category:
        products=Product.filter(category_id=category)
     # Sort
    sort=request.GET.get("sort","newest")
    allowed_sorts={
          "name": "name", 
          "-name": "-name",
          "price": "price", 
          "-price": "-price", 
          "newest": "-created_at", 
          "oldest": "created_at", 
     }

    products = products.order_by( 
        allowed_sorts.get(sort, "-created_at") 
    )
    # Pagination
    paginator=Paginator(products,10)
    page_number = request.GET.get("page") 
    page_obj = paginator.get_page(page_number) 
    categories=Category.objects.all()
    context={
            "page_obj":page_obj,
            "categories":categories,
            "search":search,
            "selected_category":category,
            "selected_sort":sort
    }
    
    return render(request,"Product.html",context)