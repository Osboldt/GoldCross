from fastapi import FastAPI, HTTPException
from src.agent.conversation_flow import ConversationFlow
from src.integrations.whatsapp import WhatsAppIntegration
from src.integrations.calendar import CalendarIntegration
from src.integrations.crm import CRMIntegration
from src.integrations.payment import PaymentIntegration
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize OpenAI API key
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# Initialize components
conversation_flow = ConversationFlow()
whatsapp = WhatsAppIntegration(
    account_sid=os.getenv("TWILIO_ACCOUNT_SID"),
    auth_token=os.getenv("TWILIO_AUTH_TOKEN"),
    from_number=os.getenv("TWILIO_FROM_NUMBER")
)
calendar = CalendarIntegration(os.getenv("GOOGLE_CREDENTIALS_PATH"))
crm = CRMIntegration(os.getenv("HUBSPOT_API_KEY"))
payment = PaymentIntegration(os.getenv("STRIPE_API_KEY"))

@app.post("/webhook/whatsapp")
async def whatsapp_webhook(data: dict):
    try:
        # Extract message data from Twilio webhook
        message = data["Body"]
        user_id = data["From"]
        
        # Process message through conversation flow
        response = await conversation_flow.handle_message(message, user_id)
        
        # Send response back to user
        await whatsapp.send_message(user_id, response)
        
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class Message(BaseModel):
    user_id: str
    message: str

@app.post("/chat")
async def chat_endpoint(message: Message):
    try:
        response = await conversation.handle_message(
            message.message,
            message.user_id
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    load_dotenv()
    uvicorn.run(app, host="127.0.0.1", port=8000)