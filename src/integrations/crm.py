from hubspot import HubSpot
from typing import Dict, Optional

class CRMIntegration:
    def __init__(self, api_key: str):
        self.client = HubSpot(api_key=api_key)
        
    async def create_or_update_lead(self, user_data: Dict) -> Dict:
        properties = {
            "email": user_data.get("email"),
            "firstname": user_data.get("name"),
            "fitness_goal": user_data.get("goal"),
            "preferred_time": user_data.get("preferred_time"),
            "lifecycle_stage": "lead"
        }
        
        try:
            contact = self.client.crm.contacts.basic_api.create(
                properties=properties
            )
            return {"contact_id": contact.id, "status": "success"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
            
    async def update_lead_status(self, contact_id: str, status: str) -> Dict:
        properties = {
            "lifecycle_stage": status
        }
        
        try:
            self.client.crm.contacts.basic_api.update(
                contact_id=contact_id,
                properties=properties
            )
            return {"status": "success"}
        except Exception as e:
            return {"status": "error", "message": str(e)}