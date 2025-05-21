from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import stripe
import json
from datetime import datetime
from .models import SubscriptionPlan, UserSubscription, PaymentHistory
from .services import PaymentService

stripe.api_key = settings.STRIPE_SECRET_KEY

class SubscriptionViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """List all available subscription plans"""
        plans = SubscriptionPlan.objects.filter(is_active=True)
        return Response([{
            'id': plan.id,
            'name': plan.name,
            'price': float(plan.price),
            'interval': plan.interval,
            'features': plan.features
        } for plan in plans])

    @action(detail=True, methods=['post'])
    def subscribe(self, request, pk=None):
        """Subscribe to a plan"""
        try:
            result = PaymentService.create_subscription(request.user, pk)
            return Response({
                'subscription_id': result['subscription_id'],
                'client_secret': result['client_secret']
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def cancel(self, request):
        """Cancel current subscription"""
        try:
            PaymentService.cancel_subscription(request.user)
            return Response({'status': 'success'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def status(self, request):
        """Get current subscription status"""
        try:
            status = PaymentService.get_subscription_status(request.user)
            return Response(status if status else {'status': 'no_subscription'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get payment history"""
        try:
            history = PaymentService.get_payment_history(request.user)
            return Response([{
                'amount': float(payment.amount),
                'status': payment.status,
                'created_at': payment.created_at
            } for payment in history])
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Handle Stripe webhooks"""
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    try:
        PaymentService.handle_webhook_event(event)
        return HttpResponse(status=200)
    except Exception as e:
        return HttpResponse(status=400)
