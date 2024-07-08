from django.shortcuts import render,redirect
from .models import Items,OrderDetail
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView,DetailView,TemplateView
from django.views.generic.edit import CreateView,UpdateView,DeleteView
from django.urls import reverse_lazy,reverse
from django.core.paginator import Paginator
#from django.db.models import Q
from users.models import Profile
#3from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.http.response import HttpResponseNotFound,JsonResponse
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import stripe
import json

# Create your views here.
def index(request):
    return HttpResponse("Welcome to Django!!!")

def items(request):
    page_obj = items=Items.objects.all()  # Ensure consistent ordering
    product_name = request.GET.get('product_name')
    if product_name != '' and product_name is not None:
        page_obj =items.filter(Name__icontains=product_name)  # Ensure the field name matches your model
    paginator = Paginator(page_obj, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'newapp/index.html', context)

class ProductListView(ListView):
    model = Items
    template_name = 'newapp/index.html'
    context_object_name = 'items'
    paginate_by = 3

    def get_queryset(self):
        queryset = super().get_queryset().order_by('id')  # Ensure consistent ordering
        product_name = self.request.GET.get('product_name')
        if product_name and product_name != '':
            queryset = queryset.filter(Name__icontains=product_name)
        return queryset

def item_detail(request, id):
    item = get_object_or_404(Items, id=id)
    context = {
        'item': item
    }
    return render(request, 'newapp/detail.html', context)

class ProductDetailView(DetailView):
    model = Items
    template_name = 'newapp/detail.html'
    context_object_name = 'item'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        context['stripe_publishable_key'] = settings.STRIPE_PUBLISHABLE_KEY
        return context

@login_required
def add_product(request):
    if request.method == 'POST':
        Name = request.POST.get('Name')
        price = request.POST.get('price')
        desc = request.POST.get('desc')
        image = request.FILES['upload']
        seller_name = request.user
        item = Items(Name=Name, price=price, desc=desc, image=image, seller_name=seller_name)
        item.save()
        return redirect('newapp:items')
    return render(request, 'newapp/addproduct.html')

class ProductCreateView(CreateView):
    model = Items
    fields = ['Name', 'price', 'desc', 'image', 'seller_name']
    template_name = 'newapp/product_form.html'

def update_product(request, id):
    item = get_object_or_404(Items, id=id)
    if request.method == 'POST':
        item.Name = request.POST.get('Name')
        item.price = request.POST.get('price')
        item.desc = request.POST.get('desc')
        if 'upload' in request.FILES:
            item.image = request.FILES['upload']
        item.save()
        return redirect('newapp:items')
    context = {
        'item': item,
    }
    return render(request, 'newapp/updateproduct.html', context)

class ProductUpdateView(UpdateView):
    model = Items
    fields = ['Name', 'price', 'desc', 'image', 'seller_name']
    template_name = 'newapp/product_update_form.html'

def delete_product(request, id):
    item = get_object_or_404(Items, id=id)
    if request.method == 'POST':
        item.delete()
        return redirect('newapp:items')
    context = {
        'item': item,
    }
    return render(request, 'newapp/delete.html', context)

class ProductDeleteView(DeleteView):
    model = Items
    success_url = reverse_lazy('newapp:items')

def my_listings(request):
    items = Items.objects.filter(seller_name=request.user).order_by('id')  # Ensure consistent ordering
    context = {
        'items': items,
    }
    return render(request, 'newapp/my_listings.html', context)

@csrf_exempt
def create_checkout_session(request, id):
    item = get_object_or_404(Items, pk=id)
    stripe.api_key = settings.STRIPE_SECRET_KEY
    checkout_session = stripe.checkout.Session.create(

        customer_email=request.user.email,
        payment_method_types=['card'],
        line_items=[
            {
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': item.Name,
                },
                'unit_amount': int(item.price * 100),  # Convert to cents
            },
            'quantity': 1,
        }
    ],
    mode='payment',
    success_url=request.build_absolute_uri(reverse('newapp:success')) + "?session_id={CHECKOUT_SESSION_ID}",
    cancel_url=request.build_absolute_uri(reverse('newapp:failed')),
    )
    #checkout_session_id = checkout_session['id']
    #session_details = stripe.checkout.Session.retrieve(checkout_session_id)
    order=OrderDetail()
    order.customer_username = request.user.username
    order.item = item
    order.stripe_payment_intent=checkout_session['id']
    order.amount = int(item.price * 100)  
    order.save()
    return JsonResponse({'sessionId': checkout_session.id})

class PaymentSuccessView(TemplateView):
    template_name='newapp/payment_success.html'

    def get(self, request, *args, **kwargs):
        session_id=request.GET.get('session_id')
        if session_id is None:
            return HttpResponseNotFound()        
        session=stripe.checkout.Session.retrieve(session_id)
        stripe.api_key=settings.STRIPE_SECRET_KEY
        order = get_object_or_404(OrderDetail,stripe_payment_intent=session.id)
        order.has_paid=True
        order.amount = int(order.amount/ 100)
        order.save()
        context = self.get_context_data(**kwargs)
        context['order'] = order
        return self.render_to_response(context)
        #return render(request,self.template_name)
class PaymentFailedView(TemplateView):
    template_name = 'newapp/payment_failed.html'



    
        
