"""fremancer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from rest_framework import routers

from fremancer import views
from fremancer import webhook
from fremancer_contracts import views as contracts_views
from fremancer_invoices import views as invoices_views
from fremancer_timesheets import views as timesheets_views
from fremancer_users import views as users_views
from fremancer_withdrawals import views as withdrawals_views

router = routers.SimpleRouter()
router.register(r'contracts', contracts_views.ContractsViewSet)
router.register(r'dailysheets', timesheets_views.DailySheetsViewSet)
router.register(r'invoices', invoices_views.InvoicesViewSet)
router.register(r'payments', invoices_views.PaymentsViewSet, base_name='payments')
router.register(r'profiles', users_views.UserProfileViewSet)
router.register(r'timesheets', timesheets_views.TimeSheetsViewSet)
router.register(r'users', users_views.UserViewSet)
router.register(r'withdrawals', withdrawals_views.WithdrawalsViewSet)

urlpatterns = [
    url(r'^api/', include(router.urls)),

    # Installed app.
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^password_reset/', include('password_reset.urls')),
    url(r'^webhook/', webhook.stripe),

    # Public pages.
    url(r'^$', views.index),

    # Admin Site.
    url(r'^admin/', include(admin.site.urls)),

    # Match all other pages.
    url(r'^(?:.*)/?$', views.index),

]
