"""roulette URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from base import views

urlpatterns = [
    path('', views.Landing.as_view(), name="landing"),
    path('leaderboard/', views.Leaderboard.as_view(), name="leaderboard"),
    path('turn/<int:pk>', views.TurnBets.as_view(), name="turn"),
    path('place-bet/<int:pk>', views.PlaceBet.as_view(), name="place-bet"),
    path('manual/', views.Manual.as_view(), name="manual"),
    path('no-round/', views.NoRound.as_view(), name="no-round"),
    path('bettor/<int:pk>/placed-wagers/', views.PlacedWagers.as_view(), name="transactions"),

    path('accounts/login/', auth_views.LoginView.as_view(), name="login"),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name="logout"),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
