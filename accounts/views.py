from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group

# Create your views here.
from .models import Customer, Product, Order, Tag
from .forms import OrderForm, CreateUserForm, CustomerForm
from .filters import OrderFilter
from .decorators import unauthenticated_user, allowed_users, admin_only


@unauthenticated_user
def registerPage(request):

    # if request.user.is_authenticated:
    #     return redirect('home')

    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')

            # group  = Group.objects.get(name='customer')
            # user.groups.add(group)
            # Customer.objects.create(user=user,
            #                         name = user.username,
            #                         email = user.email)
            messages.success(request, 'Account was created for ' + username)
            return redirect('/login')
    else:
        form = CreateUserForm()

    data = {
        'form': form
    }
    return render(request, 'accounts/register.html', data)


@unauthenticated_user
def loginPage(request):

    # if request.user.is_authenticated:
    #     return redirect('home')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'username or password incorrect')

    data = {

    }
    return render(request, 'accounts/login.html', data)


def logoutPage(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
@admin_only
def home(request):
    customers = Customer.objects.all()
    orders = Order.objects.all()
    total_customer = customers.count()
    total_order = orders.count()
    delivered = orders.filter(status='Delivered').count()
    pending = orders.filter(status='Pending').count()

    data = {
        'customers': customers,
        'orders': orders,
        'total_customer': total_customer,
        'total_order': total_order,
        'delivered': delivered,
        'pending': pending
    }
    return render(request, 'accounts/dashboard.html', data)

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def userPage(request):
    myorders = request.user.customer.order_set.all()
    total_order = myorders.count()
    delivered = myorders.filter(status='Delivered').count()
    pending = myorders.filter(status='Pending').count()
    data = {
        'myorders':myorders,
        'total_order': total_order,
        'delivered': delivered,
        'pending': pending
    }
    return render(request, 'accounts/user.html', data)


@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def accountSettings(request):
    customer = request.user.customer
    form = CustomerForm(instance=customer)

    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()
    data = {
        'form':form
    }
    return render(request, 'accounts/account_settings.html', data)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def products(request):
    products = Product.objects.all()
    data = {
        'products': products
    }
    return render(request, 'accounts/products.html', data)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def customer(request, pk):
    customer = Customer.objects.get(id=pk)
    orders = customer.order_set.all()
    total_order = orders.count()
    myfilter = OrderFilter(request.GET, queryset=orders)
    orders = myfilter.qs
    data = {
        'customer': customer,
        'orders': orders,
        'total_order': total_order,
        'myfilter': myfilter
    }
    return render(request, 'accounts/customer.html', data)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def createOrder(request, pk):
    OrderFormSet = inlineformset_factory(
        Customer, Order, fields=('product', 'status'), extra=5)
    customer = Customer.objects.get(id=pk)
    formset = OrderFormSet(queryset=Order.objects.none(), instance=customer)
    # form  = OrderForm(initial={'customer':customer})
    if request.method == 'POST':
        # form = OrderForm(request.POST)
        formset = OrderFormSet(request.POST, instance=customer)
        if formset.is_valid():
            formset.save()
            return redirect('/customer/'+pk+'/')

    data = {
        # 'form':form,
        'formset': formset
    }
    return render(request, 'accounts/order_form.html', data)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def updateOrder(request, pk):
    curr_order = Order.objects.get(id=pk)
    form = OrderForm(instance=curr_order)

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=curr_order)
        if form.is_valid():
            form.save()
            return redirect('/')
    data = {
        'form': form
    }
    return render(request, 'accounts/order_form.html', data)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def deleteOrder(request, pk):
    order = Order.objects.get(id=pk)
    if request.method == 'POST':
        order.delete()
        return redirect('/')

    data = {
        'item': order
    }
    return render(request, 'accounts/order_delete.html', data)
