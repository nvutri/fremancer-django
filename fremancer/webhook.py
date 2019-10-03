"""View handlers for main page."""
import json

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from fremancer_invoices.models import FremancerInvoice


@csrf_exempt
@require_POST
def stripe(request):
    """Handle Stripe webhook."""
    data = json.loads(request.body).get('object')
    if data.get('object') == 'charge':
        invoice = FremancerInvoice.objects.get(stripe_charge_id=data.get('id'))
        invoice.paid = data.get('paid')
        invoice.stripe_charge_status = data.get('status')
        invoice.save()
    return JsonResponse({'success': True})
