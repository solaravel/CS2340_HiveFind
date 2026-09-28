from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from jobs.models import Job
def index(request):
    cart = request.session.get('cart', {})
    job_ids = cart.keys()
    jobs_in_cart = Job.objects.filter(id__in=job_ids)
    template_data = {}
    template_data['title'] = 'Cart'
    template_data['jobs_in_cart'] = jobs_in_cart
    return render(request, 'cart/index.html',
        {'template_data': template_data})
def add(request, id):
    get_object_or_404(Job, id=id)
    cart = request.session.get('cart', {})
    cart[id] = 1
    request.session['cart'] = cart
    return redirect('cart.index')