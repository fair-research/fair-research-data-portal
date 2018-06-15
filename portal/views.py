import logging
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages

log = logging.getLogger(__name__)


def landing_page(request):
    context = {}
    return render(request, 'landing_page.html', context)
