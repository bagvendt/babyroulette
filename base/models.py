import math
from django.conf import settings
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

    def __str__(self):
        return '{} til odds {} i runde {}'.format(self.description, self.odds, self.turn)

    class Meta:
        ordering = ('turn', 'order',)


class Turn(models.Model):
    name = models.CharField(max_length=100)
    active = models.BooleanField(default=False)

    def __str__(self):
        return '{} (id: {})'.format(self.name, self.id)


class Transaction(models.Model):
    created = models.DateTimeField(auto_now_add=True, blank=True)
    bettor = models.ForeignKey('Bettor', on_delete=models.CASCADE)
    bet = models.ForeignKey('Bet', on_delete=models.CASCADE, null=True, blank=True)
    wager = models.PositiveIntegerField()

    @property
    def result(self):
        bet = getattr(self, "bet")
        if bet and not bet.turn.active:
            if bet.did_happen:
                return bet.odds * self.wager
            return self.wager * -1
        return None

    def clean(self):
        if self.bet:
            if not self.bet.turn.active:
                raise ValidationError({'bet': "Runden er ikke aktiv"})
            if self.wager > self.bettor.credits:
                raise ValidationError({'wager': "Du har ikke nok jetoner til at placere denne satsning"})
            if self.wager <= 0:
                raise ValidationError({'wager': "Nej"})

    def __str__(self):
        if not self.bet:
            return "{} Startjetoner : {}".format(
                self.bettor.user.username,
                self.wager,
            )
        return "{} satsede {} jetoner på {}. Runde: '{}'".format(
            self.bettor.user.username,
            self.wager,
            self.bet.description,
            self.bet.turn,
        )

    class Meta:
        ordering = ('-created',)


class BettorQuerySet(models.QuerySet):
    def with_credits(self):
        return self.annotate(
            annotated_credits=Sum(
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
        return BettorQuerySet(self.model, using=self._db).with_credits().order_by('-annotated_credits')


class Bettor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    objects = BettorManager()

    @property
    def credits(self):
        return math.floor(Bettor.objects.filter(pk=self.pk).with_credits().first().annotated_credits)

    def __str__(self):
        return self.user.username


def create_bettor(sender, instance, created, **kwargs):
    if created:
        with transaction.atomic():
            bettor = Bettor(user=instance)
            bettor.save()
            Transaction(
                bettor=bettor,
                wager=settings.STARTING_CREDITS,
            ).save()


post_save.connect(create_bettor, sender=User)
