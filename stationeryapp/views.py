from django.shortcuts import render, redirect,get_object_or_404,HttpResponse
from .models import Product, Cart,Order
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout 
import random
import razorpay




def about(req):
    return render(req,'about.html')

def contact(req):
    return render(req,'contact.html')

# Create your views here.
def index(req):
    username = req.user.username
    allproducts = Product.objects.all()
    context = {"allproducts": allproducts, "username": username}
    return render(req, "index.html", context)


def register(req):
    if req.method == "POST":
        uname = req.POST["uname"]
        upass = req.POST["upass"]
        ucpass = req.POST["ucpass"]
        context = {}
        if uname == "" or upass == "" or ucpass == "":
            context["errmsg"] = "Field can't be empty"
            return render(req, "register.html", context)
        elif ucpass != upass:
            context["errmsg"] = "Password and confirm password doesn't match"
            return render(req, "register.html", context)
        else:
            try:
                u = User.objects.create(username=uname, password=upass)
                u.set_password(upass)
                u.save()
                return redirect("/userlogin")
            except Exception:
                context["errmsg"] = "User already exists"
                return render(req, "register.html", context)
    else:
        return render(req, "register.html")


def userlogin(req):
    if req.method == "POST":
        uname = req.POST["uname"]
        upass = req.POST["upass"]
        context = {}
        if uname == "" and upass == "":
            context["errmsg"] = "Field can't be empty"
            return render(req, "login.html", context)
        else:
            u = authenticate(username=uname, password=upass)
            if u is not None:
                login(req, u)
                return redirect("/")
            else:
                context["errmsg"] = "Invalid username and password"
                return render(req, "login.html", context)
    else:
        return render(req, "login.html")


def userlogout(req):
    logout(req)
    return redirect("/")


def add_to_cart(request, product_id):
    if request.user.is_authenticated:
        user = request.user
    else:
        user = None
    allproducts = get_object_or_404(Product, product_id=product_id)
    cart_item, created = Cart.objects.get_or_create(product_id=allproducts, userid=user)
    if not created:
        cart_item.qty += 1
    else:
        cart_item.qty = 1
    cart_item.save()

    return redirect("/cart")


def cart(req):
    if req.user.is_authenticated:
        username = req.user.username
        allcarts = Cart.objects.filter(userid=req.user.id)
        total_price = 0
        for x in allcarts:
            total_price += x.product_id.price * x.qty
        length = len(allcarts)
        context = {
            "cart_items": allcarts,
            "total": total_price,
            "items": length,
            "username": username,
        }
        return render(req, "cart.html", context)
    else:
        allcarts = Cart.objects.filter(userid=req.user.id)
        total_price = 0
        for x in allcarts:
            total_price += x.product_id.price * x.qty
        length = len(allcarts)
        context = {
            "cart_items": allcarts,
            "total": total_price,
            "items": length,
        }
        return render(req, "cart.html", context)

def placeorder(request):
    if request.user.is_authenticated:
        user=request.user
    else:
        user=None
    
    allcarts = Cart.objects.filter(userid=user)
    
    total_price = 0
    length = len(allcarts)
    for x in allcarts:
        total_price += x.product_id.price * x.qty
    context={}
    context['cart_items']=allcarts
    context['total']=total_price
    context['items']=length
    context['username']=user
    return render(request,'placeorder.html',context)

def showorders(req):
    if req.user.is_authenticated:
        user=req.user
        allorders = Order.objects.filter(userid=user)
        context = {"allorders": allorders, "username": user}
        return render(req, "orders.html", context)
    else:
        user=None
        return redirect('/userlogin')


def makepayment(request):
    if request.user.is_authenticated:
        user=request.user
        order_id=random.randrange(1000,9999)
        allcarts = Cart.objects.filter(userid=user)
        for x in allcarts:
            o=Order.objects.create(order_id=order_id,product_id=x.product_id,userid=x.userid,qty=x.qty)
            o.save()
            x.delete()
        orders=Order.objects.filter(userid=user)
        total_price = 0
        for x in orders:
            total_price += x.product_id.price * x.qty
            oid=x.order_id
        client = razorpay.Client(auth=("rzp_test_e6hibIz7ehSLPJ", "SOrhioVsn96PkNAVAEQVQfSi"))
        data = { "amount": total_price*100, "currency": "INR", "receipt": str(oid) }
        payment = client.order.create(data=data)
        # print(payment)
        context={}
        context['data']=payment
        context['amount']=payment
        return render(request,'payment.html',context)
    else:
        user=None
        return redirect('/userlogin')
    

def remove_from_cart(request, product_id):
    if request.user.is_authenticated:
        user = request.user
    else:
        user = None
    cart_item = Cart.objects.filter(product_id=product_id, userid=user)
    cart_item.delete()
    return redirect("/cart")

def remove_from_order(request, product_id):
    if request.user.is_authenticated:
        user = request.user
    else:
        user = None
    orders=Order.objects.filter(userid=user,product_id=product_id)
    orders.delete()
    return redirect("/cart")

def range_view(request):
    if request.method == "GET":
        return render(request, "index.html")
    else:
        r1 = request.POST.get("min")
        r2 = request.POST.get("max")
        if r1 is not None and r2 is not None and r1.isdigit() and r2.isdigit():
            allproducts = Product.prod.get_price_range(r1, r2)
            context = {"allproducts": allproducts}
            return render(request, "index.html", context)
        else:
            allproducts = Product.objects.all()
            context = {"allproducts": allproducts}
            return render(request, "index.html", context)


def penlistview(request):
    if request.method == "GET":
        allproducts = Product.prod.pen_list()
        context = {"allproducts": allproducts}
        return render(request, "index.html", context)
    else:
        allproducts = Product.objects.all()
        context = {"allproducts": allproducts}
        return render(request, "index.html", context)


def notebooklistview(request):
    if request.method == "GET":
        allproducts = Product.prod.notebook_list()
        context = {"allproducts": allproducts}
        return render(request, "index.html", context)
    else:
        allproducts = Product.objects.all()
        context = {"allproducts": allproducts}
        return render(request, "index.html", context)


def calculatorlistview(request):
    if request.method == "GET":
        allproducts = Product.prod.calculator_list()
        context = {"allproducts": allproducts}
        return render(request, "index.html", context)
    else:
        allproducts = Product.object.all()
        context = {"allproducts": allproducts}
        return render(request, "index.html", context)
    
def otherProductlistview(request):
    if request.method == "GET":
        allproducts = Product.prod.otherproduct_list()
        context = {"allproducts": allproducts}
        return render(request, "index.html", context)
    else:
        allproducts = Product.object.all()
        context = {"allproducts": allproducts}
        return render(request, "index.html", context)    



def searchproduct(request):
    query = request.GET.get("q")
    if query:
        allproducts = Product.objects.filter(
            Q(product_name__icontains=query)
            | Q(category__icontains=query)
            | Q(price__icontains=query)
        )
    else:
        allproducts = Product.objects.all()
    context = {"allproducts": allproducts, "query": query}
    return render(request, "index.html", context)


def updateqty(request, qv, product_id):
    allcarts = Cart.objects.filter(product_id=product_id)
    if qv == "1":
        totol = allcarts[0].qty + 1
        allcarts.update(qty=totol)
    else:
        if allcarts[0].qty > 1:
            totol = allcarts[0].qty - 1
            allcarts.update(qty=totol)
        else:
            allcarts = Cart.objects.filter(product_id=product_id)
            allcarts.delete()

    return redirect("/cart")


def viewregisterproduct(request):
    if request.user.is_authenticated:
        user = request.user
        allproducts=Product.objects.filter()
        context={'allproducts':allproducts,'username':user}
        return render(request,"viewregisterproduct.html",context)
    else:
        user = None
        return redirect('/userlogin')

def deleteproducts(request, product_id):
    m = Product.objects.filter(bookID =  product_id);
    m.delete()
    return redirect('/viewregisterproduct')

