from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Bettor


class Leaderboard(LoginRequiredMixin, TemplateView):
    template_name = "leaderboard.html"

    def get_context_data(self):
        context = super().get_context_data()
        context['bettors'] = Bettor.objects.all()
        return context
