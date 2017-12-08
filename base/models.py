import math
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models, transaction

from django.db.models import (
    Case,
    FloatField,
    F,
    Q,
    Sum,
    When
)
from django.db.models.signals import post_save



class Bet(models.Model):
    description = models.CharField(max_length=100)
    odds = models.FloatField()
    turn = models.ForeignKey('Turn', on_delete=models.CASCADE)
    did_happen = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0, blank=False, null=False)

    class Meta:
        ordering = ('order',)


class Turn(models.Model):
    name = models.CharField(max_length=100)
    active = models.BooleanField(default=False)

    def __str__(self):
        return '%s (id: %s)' % (self.name, self.id)


class Transaction(models.Model):
    created = models.DateTimeField(auto_now_add=True, blank=True)
    bettor = models.ForeignKey('Bettor', on_delete=models.CASCADE)
    bet = models.ForeignKey('Bet', on_delete=models.CASCADE, null=True, blank=True)
    wager = models.PositiveIntegerField()


    def clean(self):
        FAILTEXT = 'Det kan ikke lade sig gøre'
        if self.bet:
            if not self.bet.turn.active:
                raise ValidationError({'bet': FAILTEXT})
            if self.wager > self.bettor.credits:
                raise ValidationError({'wager': FAILTEXT})

    def __str__(self):
        return "%s satsede %s jetoner på %s" % (self.bettor.user.username, self.wager, getattr(self.bet, 'description', None))

    class Meta:
        ordering = ('-created',)


class BettorQuerySet(models.QuerySet):
    def with_credits(self):
        return self.annotate(
            _credits=Sum(
                Case(
                    When(
                        Q(transaction__bet__isnull=False) &
                        Q(transaction__bet__did_happen=True),
                        then=F('transaction__wager') * F('transaction__bet__odds') - F('transaction__wager'),
                    ),
                    When(
                        Q(transaction__bet__isnull=False) &
                        Q(transaction__bet__did_happen=False),
                        then=-1 * F('transaction__wager'),
                    ),
                    When(
                        Q(transaction__bet__isnull=True),
                        then=F('transaction__wager'),
                    ),
                    output_field=FloatField()
                )
            )
        )


class BettorManager(models.Manager):
    def get_queryset(self):
        return BettorQuerySet(self.model, using=self._db).with_credits().order_by('-_credits')


class Bettor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    objects = BettorManager()

    @property
    def credits(self):
        return math.floor(Bettor.objects.filter(pk=self.pk).with_credits().first()._credits)


def create_bettor(sender, instance, created, **kwargs):
    if created:
    with transaction.atomic():
        bettor = Bettor(user=instance)
        bettor.save()
        Transaction(
            bettor=bettor,
            wager=1000,
        ).save()


post_save.connect(create_bettor, sender=User)
