from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from typing import List, Dict
import pytz

class CalendarIntegration:
    def __init__(self, credentials_path: str):
        self.credentials = Credentials.from_authorized_user_file(credentials_path)
        self.service = build('calendar', 'v3', credentials=self.credentials)
        self.calendar_id = 'primary'
        self.timezone = pytz.timezone('America/Sao_Paulo')

    async def get_available_slots(self, class_type: str, days_ahead: int = 7) -> List[Dict]:
        # Get class schedule from gym info
        class_times = self._get_class_schedule(class_type)
        
        available_slots = []
        now = datetime.now(self.timezone)
        
        for day in range(days_ahead):
            date = now + timedelta(days=day)
            
            for time_slot in class_times:
                slot_datetime = self._combine_date_time(date, time_slot)
                
                if await self._is_slot_available(slot_datetime):
                    available_slots.append({
                        'datetime': slot_datetime,
                        'formatted': slot_datetime.strftime('%d/%m/%Y %H:%M')
                    })
        
        return available_slots

    async def schedule_class(self, user_data: Dict, slot_datetime: datetime) -> Dict:
        event = {
            'summary': f"{user_data['class_type']} - Aula Experimental",
            'description': f"""
                Nome: {user_data['name']}
                WhatsApp: {user_data['phone']}
                Email: {user_data['email']}
                Objetivo: {user_data['goal']}
                Experiência: {user_data['experience_level']}
            """,
            'start': {
                'dateTime': slot_datetime.isoformat(),
                'timeZone': 'America/Sao_Paulo',
            },
            'end': {
                'dateTime': (slot_datetime + timedelta(hours=1)).isoformat(),
                'timeZone': 'America/Sao_Paulo',
            },
            'attendees': [
                {'email': user_data['email']},
            ],
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 60},
                ],
            },
        }
        
        response = await self.service.events().insert(
            calendarId=self.calendar_id,
            body=event,
            sendUpdates='all'
        ).execute()
        
        return {
            'event_id': response['id'],
            'status': 'confirmed',
            'datetime': slot_datetime.strftime('%d/%m/%Y %H:%M')
        }

    async def _is_slot_available(self, slot_datetime: datetime) -> bool:
        start = slot_datetime.isoformat()
        end = (slot_datetime + timedelta(hours=1)).isoformat()
        
        events = self.service.events().list(
            calendarId=self.calendar_id,
            timeMin=start,
            timeMax=end,
            singleEvents=True
        ).execute()
        
        return len(events.get('items', [])) == 0

    def _get_class_schedule(self, class_type: str) -> List[str]:
        # This should be integrated with your gym_info.json
        schedules = {
            'CrossFit': ['07:00', '09:00', '18:00', '20:00'],
            'Musculação': ['06:00', '08:00', '10:00', '14:00', '16:00', '18:00', '20:00']
        }
        return schedules.get(class_type, [])

    def _combine_date_time(self, date: datetime, time_str: str) -> datetime:
        hour, minute = map(int, time_str.split(':'))
        return self.timezone.localize(
            datetime.combine(date.date(), datetime.min.time().replace(hour=hour, minute=minute))
        )