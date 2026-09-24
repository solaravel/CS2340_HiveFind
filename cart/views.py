from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from jobs.models import Job
def add(request, id):
    get_object_or_404(Job, id=id)
    cart = request.session.get('cart', {})
    cart[id] = request.POST['quantity']
    request.session['cart'] = cart
    return redirect('home.index')