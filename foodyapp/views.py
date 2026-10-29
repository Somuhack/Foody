import logging
from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from .forms import RegistrationForm
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .models import Product,Category
from django.db.models import Q
from django.core.paginator import Paginator
from .ai_service import expand_search_query


from decimal import Decimal, InvalidOperation

from django.shortcuts import render
from django.db.models import Q

from .models import Product



logger=logging.getLogger(__name__)

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
    search=request.GET.get("search","").strip()
    ai_search_used=False
    search_error_occurred=False
    if search:
        try:
            search_terms=expand_search_query(search)
            ai_search_used=True
        except Exception:
            logger.exception("Ai Searched failed")
            search_terms=[search]
            search_error_occurred = True
        search_query=Q()    
        for term in search_terms:
                search_query |=(Q(name__icontains=term) |
                           Q(description__icontains=term))
        products=products.filter(search_query).distinct()
    #    products=products.filter(
    #        Q(name__icontains=search) |
    #        Q(description__icontains=search)
    #    )
    # Filter
    category = request.GET.get("category","")
    if category.isdigit():
        products = products.filter(category_id=int(category))
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
    # Total=103  10/page
    context={
            "page_obj":page_obj,
            "categories":categories,
            "search":search,
            "selected_category":category,
            "selected_sort":sort,
            "ai_search_used":ai_search_used,
            "search_error_occurred":search_error_occurred
    }
    return render(request,"Product.html",context)
def product_detail(request,pk):
    product = get_object_or_404(Product,id=pk)
    return render(request,"ProductDetails.html",{"product":product})   


def ai_recommendations(request):
    submitted = request.GET.get("budget") is not None

    budget = request.GET.get("budget", "")
    diet = request.GET.get("diet", "any")
    spice = request.GET.get("spice", "any")

    products = Product.objects.none()

    if submitted:
        try:
            max_budget = Decimal(budget)

            if not max_budget.is_finite() or max_budget <= 0:
                raise InvalidOperation

        except (InvalidOperation, ValueError):
            context = {
                "products": products,
                "budget": budget,
                "diet": diet,
                "spice": spice,
                "submitted": False,
                "error": "Please enter a valid positive budget.",
            }
            return render(
                request, "ai_recommendations.html", context
            )

        # Apply budget filter
        products = Product.objects.filter(price__lte=max_budget)

        # Basic keyword matching
        if diet == "vegetarian":
            products = products.filter(
                Q(name__icontains="paneer")
                | Q(name__icontains="vegetable")
                | Q(name__icontains="veg")
                | Q(description__icontains="vegetarian")
            )

        elif diet == "vegan":
            products = products.filter(
                Q(name__icontains="vegan")
                | Q(description__icontains="vegan")
            )

        if spice == "spicy":
            products = products.filter(
                Q(name__icontains="spicy")
                | Q(description__icontains="spicy")
                | Q(name__icontains="chilli")
                | Q(description__icontains="chilli")
            )

        elif spice == "mild":
            products = products.filter(
                Q(name__icontains="mild")
                | Q(description__icontains="mild")
            )

        products = products.order_by("price", "name")[:12]

    context = {
        "products": products,
        "budget": budget,
        "diet": diet,
        "spice": spice,
        "submitted": submitted,
    }

    return render(request, "ai_recommendations.html", context)

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from .models import Product

@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Initialize cart in session if it doesn't exist
    cart = request.session.get('cart', {})
    
    product_id_str = str(product_id)
    
    # Increment quantity if exists, else add new
    if product_id_str in cart:
        cart[product_id_str]['quantity'] += 1
    else:
        cart[product_id_str] = {
            'name': product.name,
            'price': str(product.price),
            'quantity': 1,
        }
        
    request.session['cart'] = cart
    request.session.modified = True

    total_items = sum(item['quantity'] for item in cart.values())
    
    return JsonResponse({
        'status': 'success',
        'message': f'"{product.name}" added to cart!',
        'total_cart_items': total_items,
    })