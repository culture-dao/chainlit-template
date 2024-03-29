import os

from agency_swarm import set_openai_key
from agency_swarm.agents import Agent
from dotenv import load_dotenv

load_dotenv()


class AgentLoader(Agent):
    def __init__(self, id):
        super().__init__(id=id)


def init_oai(self):
    """
    Initializes the OpenAI assistant for the agent.

    This method handles the initialization and potential updates of the agent's OpenAI assistant. It loads the assistant based on a saved ID, updates the assistant if necessary, or creates a new assistant if it doesn't exist. After initialization or update, it saves the assistant's settings.

    Output:
        self: Returns the agent instance for chaining methods or further processing.
    """

    # check if settings.json exists
    path = self.get_settings_path()

    # load assistant from id
    if self.id:
        self.assistant = self.client.beta.assistants.retrieve(self.id)
        self.instructions = self.assistant.instructions
        self.name = self.assistant.name
        self.description = self.assistant.description
        self.file_ids = self.assistant.file_ids
        self.metadata = self.assistant.metadata
        self.model = self.assistant.model
        # update assistant if parameters are different
        if not self._check_parameters(self.assistant.model_dump()):
            self._update_assistant()
        return self

    self._save_settings()

    return self


def main():
    openai_key = os.getenv("OPENAI_API_KEY")
    set_openai_key(openai_key)
    agent = AgentLoader(id='asst_UdBAhFZsmVSJCJ8THgCpA1tK')
    agent.init_oai()
    print(agent)
    pass


if __name__ == "__main__":
    print('running')
    main()