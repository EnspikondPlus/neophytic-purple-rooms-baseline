# tests/test_agent.py
import pytest
import json
from a2a.types import Message

from utils import send_text_message

# Mock Prompt from Green Agent
STEP_0_PROMPT = """You are solving a Rooms navigation puzzle. Current state (Step 0):
Current Room: 0
Phase: Observation
Keys Held: 0
Steps Remaining: 30

Rooms Visited: [0]
Rooms Inspected: [0, 0, 0, 0, 0, 0, 0, 0]

Room Properties (for inspected rooms, -1 means unknown):
- Locked: [-1, -1, -1, -1, -1, -1, -1, -1]
- Has Key: [-1, -1, -1, -1, -1, -1, -1, -1]
- Is Exit: [-1, -1, -1, -1, -1, -1, -1, -1]

Respond with a JSON object containing your action."""

STEP_1_PROMPT = """Current state (Step 1):
Current Room: 1
Phase: Observation
Rooms Visited: [0, 1]
Rooms Inspected: [0, 0, 0, 0, 0, 0, 0, 0]
..."""

@pytest.mark.asyncio
async def test_rooms_logic_interaction(agent):
    """Test a multi-turn conversation simulating the game."""
    
    # 1. Send Step 0
    context_id = "test_session_123"
    
    print("\nSending Step 0...")
    events = await send_text_message(STEP_0_PROMPT, agent, context_id=context_id)
    
    response_text = ""
    for event in events:
        # Case 1: Direct Message (Streaming or direct response)
        if isinstance(event, Message):
            if event.parts and event.parts[0].root.kind == "text":
                response_text += event.parts[0].root.text
        
        # Case 2: Task Update (Tuple of Task, Update)
        # This is where 'updater.complete()' responses usually live
        elif isinstance(event, tuple):
            task, update = event
            if task.status.message and task.status.message.parts:
                 response_text += task.status.message.parts[0].root.text

    assert response_text != "", "Agent returned no text response"
    
    data = json.loads(response_text)
    assert "command" in data
    print(f"Agent Action 0: {data}")

    # 2. Send Step 1 (Continuation)
    print("Sending Step 1...")
    events_2 = await send_text_message(STEP_1_PROMPT, agent, context_id=context_id)
    
    response_text_2 = ""
    for event in events_2:
        if isinstance(event, Message):
            if event.parts and event.parts[0].root.kind == "text":
                response_text_2 += event.parts[0].root.text
        elif isinstance(event, tuple):
            task, update = event
            if task.status.message and task.status.message.parts:
                 response_text_2 += task.status.message.parts[0].root.text

    data_2 = json.loads(response_text_2)
    assert "command" in data_2
    print(f"Agent Action 1: {data_2}")