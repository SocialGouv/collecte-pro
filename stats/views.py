from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class Stats(LoginRequiredMixin, TemplateView):
    template_name = "stats/stats.html"
