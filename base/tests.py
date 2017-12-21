from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from .models import (Bet, Bettor, Transaction, Turn)


@override_settings(STARTING_CREDITS=1000)
class BaseTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="a")
        t = Turn.objects.create(name="1", active=True)
        self.b1 = Bet.objects.create(
            description="fail", odds=2, did_happen=False, turn=t
        )
        self.b2 = Bet.objects.create(
            description="win", odds=4, did_happen=True, turn=t
        )

    def test_credits_baseline(self):
        self.assertEqual(self.user.bettor.credits, 1000)

    def test_credits_win_one(self):
        Transaction(bet=self.b2, bettor=self.user.bettor, wager=1000).save()
        self.assertEqual(self.user.bettor.credits, 1000*4)

    def test_credits_win_two(self):
        Transaction(bet=self.b2, bettor=self.user.bettor, wager=500).save()
        self.assertEqual(self.user.bettor.credits, 500+500*4)

    def test_credits_win_three(self):
        Transaction(bet=self.b2, bettor=self.user.bettor, wager=200).save()
        Transaction(bet=self.b2, bettor=self.user.bettor, wager=200).save()
        self.assertEqual(self.user.bettor.credits, 1000-400+400*4)

    def test_credits_loss_one(self):
        Transaction(bet=self.b1, bettor=self.user.bettor, wager=500).save()
        self.assertEqual(self.user.bettor.credits, 500)

    def test_credits_loss_two(self):
        Transaction(bet=self.b1, bettor=self.user.bettor, wager=1000).save()
        self.assertEqual(self.user.bettor.credits, 0)

    def test_credits_invalid_wager(self):
        with self.assertRaises(ValidationError):
            Transaction(
                bet=self.b2,
                bettor=self.user.bettor,
                wager=1001).clean()

    def test_credits_invalid_wager_two(self):
        with self.assertRaises(ValidationError):
            Transaction(bet=self.b1, bettor=self.user.bettor, wager=500).save()
            Transaction(bet=self.b1, bettor=self.user.bettor, wager=500).save()
            Transaction(bet=self.b2, bettor=self.user.bettor, wager=1).clean()

    def test_credits_invalid_wager_invalid_turn(self):
        t = Turn.objects.create(name="2", active=False)
        b3 = Bet.objects.create(
            description="win", odds=2.2, did_happen=True, turn=t)
        with self.assertRaises(ValidationError):
            Transaction(bet=b3, bettor=self.user.bettor, wager=1).clean()

    def test_credits_queryset_ordering(self):
        u2 = User.objects.create(username="b")
        Transaction(bet=self.b1, bettor=self.user.bettor, wager=1000).save()
        Transaction(bet=self.b2, bettor=u2.bettor, wager=1000).save()
        qs = Bettor.objects.all()
        self.assertEqual(qs[0].id, u2.bettor.id)
        self.assertEqual(qs[1].id, self.user.bettor.id)
