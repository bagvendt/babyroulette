
from django.views.generic import (
    CreateView,
    DetailView,
    RedirectView,
    TemplateView
)
from django.core.exceptions import (
    MultipleObjectsReturned,
    ObjectDoesNotExist,
    SuspiciousOperation
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from base import models


class Landing(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self):
        try:
            pk = models.Turn.objects.get(active=True).pk
            return reverse('turn', kwargs={'pk': pk})
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            return "no-round"


class TurnBets(LoginRequiredMixin, DetailView):
    template_name = "turn.html"
    model = models.Turn


class PlaceBet(LoginRequiredMixin, CreateView):
    success_url = "/"
    model = models.Transaction
    fields = ('bettor', 'bet', 'wager')
    template_name = "place-bet.html"

    def dispatch(self, request, *args, **kwargs):
        self.bet = models.Bet.objects.get(pk=kwargs['pk'])
        if not self.bet.turn.active:
            raise SuspiciousOperation("Fuuuuck af")
        return super().dispatch(request, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['bet'] = self.bet
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.method == 'POST':
            data = {
                'wager': self.request.POST['wager'],
                'bettor': self.request.user.bettor.pk,
                'bet': self.bet.pk
            }
            kwargs['data'] = data
        return kwargs


class Leaderboard(LoginRequiredMixin, TemplateView):
    template_name = "leaderboard.html"

    def get_context_data(self):
        context = super().get_context_data()
        context['bettors'] = models.Bettor.objects.filter(user__is_active=True).select_related('user')
        return context


class PlacedWagers(LoginRequiredMixin, DetailView):
    template_name = "placed-wagers.html"
    model = models.Bettor

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset\
            .prefetch_related(
                "transaction_set",
                "transaction_set__bet",
                "transaction_set__bet__turn",
            )\
            .select_related('user')
        return queryset


class Manual(LoginRequiredMixin, TemplateView):
    template_name = "manual.html"


class NoRound(LoginRequiredMixin, TemplateView):
    template_name = "no_round.html"
