from twilio.rest import Client
from typing import Dict

class WhatsAppIntegration:
    def __init__(self, account_sid: str, auth_token: str, from_number: str):
        self.client = Client(account_sid, auth_token)
        self.from_number = from_number
        
    async def send_message(self, to_number: str, message: str) -> Dict:
        response = self.client.messages.create(
            from_=f'whatsapp:{self.from_number}',
            body=message,
            to=f'whatsapp:{to_number}'
        )
        return {"message_id": response.sid, "status": response.status}
    
    async def send_reminder(self, to_number: str, appointment_time: str) -> Dict:
        message = (
            f"Não se esqueça do seu treino experimental amanhã às {appointment_time}! "
            "Estamos ansiosos para te receber! 💪"
        )
        return await self.send_message(to_number, message)
    
    async def send_follow_up(self, to_number: str) -> Dict:
        message = (
            "E aí, como foi seu treino? Esperamos que tenha gostado! "
            "Que tal aproveitar nossa promoção especial para novos alunos? 🏋️‍♂️"
        )
        return await self.send_message(to_number, message)