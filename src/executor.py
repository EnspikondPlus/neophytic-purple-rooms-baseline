from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import (
    Task,
    TaskState,
    InvalidRequestError,
)
from a2a.utils.errors import ServerError
from a2a.utils import (
    new_agent_text_message,
    new_task,
    get_message_text,
)

from agent import BaselinePurpleAgent

TERMINAL_STATES = {
    TaskState.completed,
    TaskState.canceled,
    TaskState.failed,
    TaskState.rejected
}

class Executor(AgentExecutor):
    def __init__(self):
        # Maps context_id -> Agent Instance
        self.agents: dict[str, BaselinePurpleAgent] = {}

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        msg = context.message
        if not msg:
            raise ServerError(error=InvalidRequestError(message="Missing message in request"))

        task = context.current_task
        if task and task.status.state in TERMINAL_STATES:
            raise ServerError(error=InvalidRequestError(message=f"Task {task.id} already processed"))

        if not task:
            task = new_task(msg)
            await event_queue.enqueue_event(task)

        context_id = task.context_id
        
        # State Management:
        # If context_id is missing, generate one, but for this benchmark 
        # the Green Agent usually sends one to maintain the session.
        if not context_id:
            context_id = "default_session"

        agent = self.agents.get(context_id)
        if not agent:
            print(f"🟣 Creating new Purple Agent for context: {context_id}")
            agent = BaselinePurpleAgent()
            self.agents[context_id] = agent
        
        # Check if the prompt indicates a reset (optional safety)
        prompt = get_message_text(msg)
        if "Step 0" in prompt:
            # Reset the agent's internal memory
            agent.reset()

        updater = TaskUpdater(event_queue, task.id, context_id)
        await updater.start_work()

        try:
            # Select action
            action = agent.select_action(prompt)
            response_text = agent.format_action(action)
            
            print(f"🟣 Replying: {response_text}")

            # Return action to green agent
            await updater.complete(new_agent_text_message(response_text, context_id=context_id, task_id=task.id))
            
        except Exception as e:
            print(f"Task failed with agent error: {e}")
            await updater.failed(new_agent_text_message(f"Agent error: {e}", context_id=context_id, task_id=task.id))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        pass