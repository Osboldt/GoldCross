from typing import Dict, List
import json

class AgentMemory:
    def __init__(self):
        self.api_url = "http://localhost:11434/api/generate"
        self.embeddings_url = "http://localhost:11434/api/embeddings"
        self.memories = {}
        self.initialize_knowledge_base()
    
    def initialize_knowledge_base(self):
        try:
            with open("data/gym_info.json", "r") as f:
                self.gym_data = json.load(f)
        except Exception as e:
            print(f"Warning: Could not initialize knowledge base: {e}")
            self.gym_data = {}
    
    def get_user_memory(self, user_id: str) -> Dict:
        if user_id not in self.memories:
            self.memories[user_id] = {
                "chat_history": []
            }
        return self.memories[user_id]
    
    def save_context(self, user_id: str, input_data: Dict, output_data: Dict):
        if user_id not in self.memories:
            self.memories[user_id] = {"chat_history": []}
        self.memories[user_id]["chat_history"].append({
            "input": input_data["input"],
            "output": output_data["output"]
        })
    
    async def search_knowledge_base(self, query: str) -> List[str]:
        return []  # Simplified for now, implement search logic later
    
    def get_conversation_history(self, user_id: str) -> List[Dict]:
        return self.memories.get(user_id, {}).get("history", [])
    
    def add_interaction(self, user_id: str, message: str, response: str):
        if user_id not in self.memories:
            self.memories[user_id] = {"history": []}
        
        self.memories[user_id]["history"].append({
            "message": message,
            "response": response
        })