from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel
from .memory import AgentMemory
import httpx
import json

class ConversationState(Enum):
    INITIAL = "initial"
    QUALIFICATION = "qualification"
    PLAN_SUGGESTION = "plan_suggestion"
    SCHEDULING = "scheduling"
    FOLLOW_UP = "follow_up"
    RETENTION = "retention"
    SHOWING_AVAILABLE_SLOTS = "showing_available_slots"
    CONFIRMING_SCHEDULE = "confirming_schedule"

class ConversationFlow:
    async def _handle_scheduling(self, message: str, user_id: str) -> str:
        if not self.user_profile:
            return "Por favor, complete seu cadastro primeiro."
            
        if self.state == ConversationState.SCHEDULING:
            # Get available slots for the next 7 days
            available_slots = await self.calendar.get_available_slots(
                self.user_profile.class_type
            )
            
            if not available_slots:
                return "Desculpe, não encontramos horários disponíveis nos próximos 7 dias."
            
            # Format available slots message
            slots_message = "Horários disponíveis:\n\n"
            for i, slot in enumerate(available_slots, 1):
                slots_message += f"[{i}] {slot['formatted']}\n"
            slots_message += "\nDigite o número do horário desejado:"
            
            self.available_slots = available_slots
            self.state = ConversationState.SHOWING_AVAILABLE_SLOTS
            return slots_message
            
        elif self.state == ConversationState.SHOWING_AVAILABLE_SLOTS:
            try:
                slot_index = int(message) - 1
                selected_slot = self.available_slots[slot_index]
                
                # Schedule the class
                scheduling_result = await self.calendar.schedule_class(
                    {
                        'name': self.user_profile.name,
                        'email': self.user_profile.email,
                        'phone': self.user_profile.phone,
                        'class_type': self.user_profile.class_type,
                        'goal': self.user_profile.goal,
                        'experience_level': self.user_profile.experience_level
                    },
                    selected_slot['datetime']
                )
                
                self.state = ConversationState.FOLLOW_UP
                return f"""
                Ótimo! Sua aula experimental foi agendada para {scheduling_result['datetime']}.
                
                Você receberá um email de confirmação em instantes.
                Te esperamos! 💪
                """
                
            except (ValueError, IndexError):
                return "Por favor, escolha um número válido da lista de horários."

class UserProfile(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    class_type: Optional[str] = None
    goal: Optional[str] = None
    preferred_time: Optional[str] = None
    experience_level: Optional[str] = None
    restrictions: Optional[str] = None
    
class ConversationFlow:
    def __init__(self):
        self.state = ConversationState.INITIAL
        self.user_profile = UserProfile()
        self.memory = AgentMemory()
        self.api_url = "http://localhost:11434/api/generate"
        
    async def _call_ollama(self, prompt: str) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.api_url,
                json={
                    "model": "mistral",
                    "prompt": prompt,
                    "stream": False
                }
            )
            result = response.json()
            return result["response"]

    async def handle_message(self, message: str, user_id: str) -> str:
        # Format WhatsApp message if it contains media
        if isinstance(message, dict):
            if 'type' in message and message['type'] == 'image':
                message = "[Image received]"
            elif 'type' in message and message['type'] == 'document':
                message = "[Document received]"
            else:
                message = message.get('text', '')

        if self.state == ConversationState.INITIAL:
            response = await self._handle_initial_greeting(message)
        elif self.state == ConversationState.QUALIFICATION:
            response = await self._handle_qualification(message)
        else:
            relevant_info = await self.memory.search_knowledge_base(message)
            context = "\n".join(relevant_info) if relevant_info else ""
            
            prompt = f"""
            Context: {context}
            Current state: {self.state.value}
            User profile: {self.user_profile}
            WhatsApp user ID: {user_id}
            
            User message: {message}
            """
            response = await self._call_ollama(prompt)
        
        # Format response for WhatsApp
        response = response.strip()
        
        # Store interaction
        self.memory.save_context(
            user_id,
            {"input": message},
            {"output": response}
        )
        
        return response
    
    async def _handle_initial_greeting(self, message: str) -> str:
        greeting = """
        Olá! Bem-vindo à Academia Fitness! 
        Você tem interesse em musculação ou CrossFit?
        
        [1] Musculação
        [2] CrossFit
        [3] Ambos
        """
        self.state = ConversationState.QUALIFICATION
        return greeting