from typing import Dict
from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI

class LeadQualifier:
    def __init__(self):
        self.llm = ChatOpenAI(temperature=0.7)
        self.conversation = ConversationChain(llm=self.llm)
        
    async def qualify_lead(self, user_profile: Dict) -> Dict:
        qualification_score = 0
        recommended_plan = None
        
        # Score based on profile completeness
        if user_profile.get("goal"):
            qualification_score += 2
        if user_profile.get("preferred_time"):
            qualification_score += 1
            
        # Use LLM for plan recommendation
        if qualification_score >= 3:
            prompt = self._create_recommendation_prompt(user_profile)
            response = await self.conversation.arun(prompt)
            recommended_plan = self._parse_recommendation(response)
            
        return {
            "score": qualification_score,
            "recommended_plan": recommended_plan,
            "status": "qualified" if qualification_score >= 3 else "pending"
        }