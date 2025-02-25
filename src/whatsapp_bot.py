from fastapi import FastAPI, Request
from twilio.rest import Client
from .agent.conversation_flow import ConversationFlow
import os
import asyncio

app = FastAPI()
conversation_flow = ConversationFlow()

# Initialize Twilio client
client = Client(
    os.getenv('TWILIO_ACCOUNT_SID'),
    os.getenv('TWILIO_AUTH_TOKEN')
)

@app.post("/webhook")
async def webhook(request: Request):
    form_data = await request.form()
    
    # Get message details
    message = form_data.get('Body', '')
    user_id = form_data.get('From', '').split(':')[-1]  # Extract number from WhatsApp ID
    
    # Handle media if present
    num_media = int(form_data.get('NumMedia', 0))
    if num_media > 0:
        media_type = form_data.get('MediaContentType0', '')
        media_url = form_data.get('MediaUrl0', '')
        message = {
            'type': 'image' if 'image' in media_type else 'document',
            'url': media_url,
            'text': message
        }
    
    # Get response from agent
    response = await conversation_flow.handle_message(message, user_id)
    
    # Send response via WhatsApp
    client.messages.create(
        body=response,
        from_=f'whatsapp:{os.getenv("TWILIO_PHONE_NUMBER")}',
        to=f'whatsapp:{user_id}'
    )
    
    return {"status": "success"}