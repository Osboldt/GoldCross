import stripe
from typing import Dict

class PaymentIntegration:
    def __init__(self, api_key: str):
        stripe.api_key = api_key
        
    async def create_checkout_session(self, plan_id: str, customer_email: str) -> Dict:
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': plan_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url='https://yourgym.com/success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url='https://yourgym.com/canceled',
                customer_email=customer_email
            )
            return {"session_id": session.id, "url": session.url}
        except Exception as e:
            return {"status": "error", "message": str(e)}
            
    async def handle_subscription_webhook(self, event_data: Dict) -> Dict:
        event = stripe.Event.construct_from(event_data, stripe.api_key)
        
        if event.type == 'customer.subscription.created':
            subscription = event.data.object
            return {
                "status": "success",
                "customer_id": subscription.customer,
                "subscription_id": subscription.id
            }
        
        return {"status": "unhandled_event"}