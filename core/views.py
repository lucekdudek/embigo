# -*- coding: utf-8 -*-

from django.shortcuts import  render, get_object_or_404
from core.models import Space

def index(request):
    return render(request, 'index.html')

def space(request, space_id):
    spaces_list = Space.objects.all()
    space = get_object_or_404(Space, pk=space_id)
    context = {'spaces_list': spaces_list, 'space': space}
    return render(request, 'space.html', context)
