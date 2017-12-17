from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django import forms
from .models import (Bet, Bettor, Turn, Transaction)


class BetInline(admin.TabularInline):
    model = Bet


class BettorInline(admin.StackedInline):
    model = Bettor


class BettorAdmin(UserAdmin):
    inlines = [BettorInline, ]


class TurnForm(forms.ModelForm):

    class Meta:
        model = Turn
        fields = ['name', 'active']


class TurnAdmin(admin.ModelAdmin):
    inlines = (BetInline,)
    form = TurnForm


admin.site.unregister(User)
admin.site.register(User, BettorAdmin)
admin.site.register(Turn, TurnAdmin)
admin.site.register(Transaction)
