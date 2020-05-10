from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth import authenticate, login, logout

from django.contrib import messages

from django.contrib.auth.decorators import login_required
import json
import datetime

from .models import *
from .forms import CreateUserForm


def loginPage(request):
    if request.user.is_authenticated:
        return redirect("store")
    else:
        if request.method == "POST":
            username = request.POST.get("username")
            password = request.POST.get("password")

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect("store")
            else:
                messages.info(request, "Username OR password is incorrect")

        context = {}
        return render(request, "store/login.html", context)


def logoutUser(request):
    logout(request)
    return redirect("login")


def registerPage(request):
    if request.user.is_authenticated:
        return redirect("store")
    else:
        form = CreateUserForm()
        if request.method == "POST":
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get("username")
                messages.success(request, "Account was created for " + user)

                return redirect("login")

        context = {"form": form}
        return render(request, "store/register.html", context)


@login_required(login_url="login")
def store(request):
    if request.user.is_authenticated:
        # customer = request.user
        order, created = Order.objects.get_or_create(
            customer=request.user, complete=False
        )
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {"get_cart_items": 0, "get_cart_total": 0, "shipping": False}
        cartItems = order["get_cart_items"]
    products = Product.objects.all()
    context = {"products": products, "cartItems": cartItems}
    return render(request, "store/Store.html", context)


@login_required(login_url="login")
def cart(request):
    if request.user.is_authenticated:
        # customer = request.user
        order, created = Order.objects.get_or_create(
            customer=request.user, complete=False
        )
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {"get_cart_items": 0, "get_cart_total": 0, "shipping": False}
        cartItems = order["get_cart_items"]

    context = {"items": items, "order": order, "cartItems": cartItems}
    return render(request, "store/Cart.html", context)


@login_required(login_url="login")
def Checkout(request):
    if request.user.is_authenticated:
        # customer = request.user
        order, created = Order.objects.get_or_create(
            customer=request.user, complete=False
        )
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {"get_cart_items": 0, "get_cart_total": 0, "shipping": False}
        cartItems = order["get_cart_items"]
    context = {"items": items, "order": order, "cartItems": cartItems}
    return render(request, "store/Checkout.html", context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data["productId"]
    action = data["action"]
    print(productId, action)

    # customer = request.user
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=request.user, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == "add":
        orderItem.quantity = orderItem.quantity + 1
    elif action == "remove":
        orderItem.quantity = orderItem.quantity - 1

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse("Item was added ", safe=False)


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    if request.user.is_authenticated:

        order, created = Order.objects.get_or_create(
            customer=request.user, complete=False
        )
        total = float(data["form"]["total"])
        order.transaction_id = transaction_id

        if total == order.get_cart_total:
            order.complete = True
        order.save()
        if order.shipping == True:
            ShippingAddress.objects.create(
                customer=request.user,
                order=order,
                address=data["shipping"]["address"],
                city=data["shipping"]["city"],
                state=data["shipping"]["state"],
                zipcode=data["shipping"]["zipcode"],
                country=data["shipping"]["country"],
                phone_number=data["shipping"]["phone_number"],
                total=float(data["form"]["total"]),
            )
            OrderDeliveryStatus.objects.create(
                order=order, customer=request.user, address=data["shipping"]["address"]
            )
            PaymentInfo.objects.create(
                order=order, customer=request.user, address=data["shipping"]["address"]
            )
    else:
        print("user is not logged in")
    return JsonResponse("Payment complete", safe=False)


def each_product(request, pk):
    if pk:
        order, created = Order.objects.get_or_create(
            customer=request.user, complete=False
        )
        product = Product.objects.get(id=pk)

        product = {
            "name": product.name,
            "price": product.price,
            "image": product.imageUrl,
            "image_first": product.image1.url,
            "image_second": product.image2.url,
            "image_third": product.image3.url,
            "seller": product.seller,
            "size": product.size,
            "color": product.color,
            "description": product.description,
            "stock": product.stock,
            "distance": product.distance,
            "id": pk,
        }
        cartItems = order.get_cart_items

    context = {"product": product, "cartItems": cartItems}
    return render(request, "store/view_product.html", context)