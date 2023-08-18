from steamship.agents.functional import FunctionsBasedAgent
from steamship.agents.llms.openai import ChatOpenAI
from steamship.agents.mixins.transports.steamship_widget import SteamshipWidgetTransport
from steamship.agents.schema.message_selectors import MessageWindowMessageSelector
from steamship.agents.service.agent_service import AgentService
from steamship.agents.tools.image_generation import DalleTool
from steamship.agents.tools.search import SearchTool
from steamship.utils.repl import AgentREPL


class MyCachingAssistant(AgentService):
    """MyCachingAssistant is an example AgentService that exposes a single test endpoint
    for trying out Agent-based invocations. It is configured with two simple Tools
    to provide an overview of the types of tasks it can accomplish (here, search
    and image generation)."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs, use_llm_cache=True, use_action_cache=True)
        self.set_default_agent(
            FunctionsBasedAgent(
                tools=[
                    SearchTool(),
                    DalleTool(),
                ],
                llm=ChatOpenAI(self.client, temperature=0),
                conversation_memory=MessageWindowMessageSelector(k=2),
            )
        )

        # This Mixin provides HTTP endpoints that connects this agent to a web client
        self.add_mixin(SteamshipWidgetTransport(client=self.client, agent_service=self))


if __name__ == "__main__":
    # AgentREPL provides a mechanism for local execution of an AgentService method.
    # This is used for simplified debugging as agents and tools are developed and
    # added.
    AgentREPL(MyCachingAssistant, agent_package_config={}).run()
