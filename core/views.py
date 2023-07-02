from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import *
import json
import datetime
from django.views.decorators.csrf import csrf_exempt
from .utils import cookieCart, cartData, guestOrder
from .forms import LoginForm, RegisterForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


def loginPage(request):

    if request.user.is_authenticated:
        return redirect('store')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('store')

    form = LoginForm()
    context = {'form': form}
    return render(request, 'core/login.html', context)


def registerPage(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            authenticated_user = authenticate(
                request, 
                username=request.POST.get('username'),
                password=request.POST.get('password1')
            )
            customer = Customer.objects.create(
                user=authenticated_user,
                name=request.POST.get('username'),
                email=request.POST.get('email')
            )
            customer.save()
            
            login(request, authenticated_user)
            return redirect('store')
    else:
        form = RegisterForm()
    context = {'form': form}
    return render(request, 'core/register.html', context)


@login_required(login_url='login')
def logoutPage(request):
    logout(request)
    return redirect('store')


def store(request):

    data = cartData(request)

    cartItems = data['cartItems']
    
    products = Product.objects.all()
    context = {'products': products, 'cartItems': cartItems}
    return render(request, 'core/store.html', context)


def cart(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'core/cart.html', context)



def checkout(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    
    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'core/checkout.html', context)


def updateItem(request):

    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action:', action)
    print('ProductId:', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)


# Solution 1: To Fix CSRF_TOKEN
@csrf_exempt
def processOrder(request):
    print('Data:', request.body)
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)

    else:
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode']
        )

    return JsonResponse('Payment submitted...', safe=False)

