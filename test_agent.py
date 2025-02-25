import asyncio
from src.agent.conversation_flow import ConversationFlow

async def test_agent():
    conversation = ConversationFlow()
    user_id = "test_user"
    
    messages = [
        "Olá",
        "1",  # Musculação
        "João Silva",
        "joao@email.com",
        "11999999999",
        "Ganhar massa muscular",
        "Iniciante"
    ]
    
    for message in messages:
        print(f"\nUser: {message}")
        response = await conversation.handle_message(message, user_id)
        print(f"Agent: {response}")
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(test_agent())