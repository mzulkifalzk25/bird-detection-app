import stripe
from django.conf import settings
from django.utils import timezone
from datetime import datetime
from .models import SubscriptionPlan, UserSubscription, PaymentHistory

stripe.api_key = settings.STRIPE_SECRET_KEY

class PaymentService:
    @staticmethod
    def create_customer(user):
        """Create a Stripe customer for a user"""
        try:
            customer = stripe.Customer.create(
                email=user.email,
                metadata={'user_id': user.id}
            )
            return customer
        except stripe.error.StripeError as e:
            raise Exception(f"Error creating customer: {str(e)}")

    @staticmethod
    def create_subscription(user, plan_id):
        """Create a subscription for a user"""
        try:
            plan = SubscriptionPlan.objects.get(id=plan_id, is_active=True)

            # Get or create customer
            if not hasattr(user, 'usersubscription'):
                customer = PaymentService.create_customer(user)
            else:
                customer = stripe.Customer.retrieve(
                    user.usersubscription.stripe_customer_id
                )

            # Create subscription
            subscription = stripe.Subscription.create(
                customer=customer.id,
                items=[{'price': plan.stripe_price_id}],
                payment_behavior='default_incomplete',
                expand=['latest_invoice.payment_intent']
            )

            # Create or update UserSubscription
            user_subscription = UserSubscription.objects.update_or_create(
                user=user,
                defaults={
                    'plan': plan,
                    'stripe_customer_id': customer.id,
                    'stripe_subscription_id': subscription.id,
                    'status': subscription.status,
                    'current_period_start': datetime.fromtimestamp(
                        subscription.current_period_start
                    ),
                    'current_period_end': datetime.fromtimestamp(
                        subscription.current_period_end
                    ),
                }
            )[0]

            return {
                'subscription_id': subscription.id,
                'client_secret': subscription.latest_invoice.payment_intent.client_secret,
                'user_subscription': user_subscription
            }

        except stripe.error.StripeError as e:
            raise Exception(f"Error creating subscription: {str(e)}")

    @staticmethod
    def cancel_subscription(user):
        """Cancel a user's subscription"""
        try:
            subscription = user.usersubscription
            stripe_sub = stripe.Subscription.modify(
                subscription.stripe_subscription_id,
                cancel_at_period_end=True
            )

            subscription.cancel_at_period_end = True
            subscription.save()

            return True
        except stripe.error.StripeError as e:
            raise Exception(f"Error canceling subscription: {str(e)}")

    @staticmethod
    def handle_webhook_event(event):
        """Handle Stripe webhook events"""
        try:
            if event['type'] == 'customer.subscription.updated':
                subscription = event['data']['object']
                user_subscription = UserSubscription.objects.get(
                    stripe_subscription_id=subscription.id
                )
                user_subscription.status = subscription.status
                user_subscription.current_period_start = datetime.fromtimestamp(
                    subscription.current_period_start
                )
                user_subscription.current_period_end = datetime.fromtimestamp(
                    subscription.current_period_end
                )
                user_subscription.save()

            elif event['type'] == 'invoice.payment_succeeded':
                invoice = event['data']['object']
                user_subscription = UserSubscription.objects.get(
                    stripe_customer_id=invoice.customer
                )
                PaymentHistory.objects.create(
                    subscription=user_subscription,
                    stripe_payment_intent_id=invoice.payment_intent,
                    amount=invoice.amount_paid / 100,
                    status='succeeded'
                )

            elif event['type'] == 'invoice.payment_failed':
                invoice = event['data']['object']
                user_subscription = UserSubscription.objects.get(
                    stripe_customer_id=invoice.customer
                )
                PaymentHistory.objects.create(
                    subscription=user_subscription,
                    stripe_payment_intent_id=invoice.payment_intent,
                    amount=invoice.amount_due / 100,
                    status='failed'
                )

            return True
        except Exception as e:
            raise Exception(f"Error handling webhook event: {str(e)}")

    @staticmethod
    def get_subscription_status(user):
        """Get the current subscription status for a user"""
        try:
            if not hasattr(user, 'usersubscription'):
                return None

            subscription = user.usersubscription
            stripe_sub = stripe.Subscription.retrieve(
                subscription.stripe_subscription_id
            )

            return {
                'status': stripe_sub.status,
                'current_period_end': datetime.fromtimestamp(
                    stripe_sub.current_period_end
                ),
                'cancel_at_period_end': stripe_sub.cancel_at_period_end,
                'plan': {
                    'name': subscription.plan.name,
                    'price': float(subscription.plan.price),
                    'interval': subscription.plan.interval
                }
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Error getting subscription status: {str(e)}")

    @staticmethod
    def get_payment_history(user):
        """Get payment history for a user"""
        try:
            if not hasattr(user, 'usersubscription'):
                return []

            return PaymentHistory.objects.filter(
                subscription=user.usersubscription
            ).order_by('-created_at')
        except Exception as e:
            raise Exception(f"Error getting payment history: {str(e)}")