import openai
from openai.types.beta.assistant import ToolResources, ToolResourcesCodeInterpreter, ToolResourcesFileSearch, Assistant


class OpenAIAssistantManager:
    def __init__(self, api_key: str):
        self.client = openai.Client(api_key=api_key)

    def create_assistant(self, assistant_data) -> Assistant:
        tool_resources = ToolResources(
            code_interpreter=ToolResourcesCodeInterpreter(file_ids=assistant_data.get("file_ids")),
            file_search=ToolResourcesFileSearch(vector_store_ids=assistant_data.get("vector_store_ids"))
        )
        assistant = Assistant(
            name=assistant_data["name"],
            description=assistant_data["description"],
            instructions=assistant_data["instructions"],
            model=assistant_data["model"],
            tools=assistant_data["tools"],
            tool_resources=tool_resources
        )
        try:
            response = self.client.beta.assistants.create(**assistant.dict())
            return response
        except Exception as e:
            print(f"Failed to create assistant: {e}")

