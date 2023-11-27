from django.shortcuts import render
from django.views.generic import ListView

from apps.core.models import Job, JobApplication, Category


class HomeView(ListView):
    template_name = "core/home.html"
    queryset = Job.objects.all()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = "Home"
        return context
