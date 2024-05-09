import logging
from typing import Dict

import chainlit as cl
from openai.lib.streaming import AsyncAssistantEventHandler
from openai.types.beta import AssistantStreamEvent
from openai.types.beta.threads import Run, Text, Message, MessageDelta
from openai.types.beta.threads.runs import RunStep, RunStepDelta, ToolCallDeltaObject, FunctionToolCallDelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EventHandler(AsyncAssistantEventHandler):

    def __init__(self):
        super().__init__()
        self.event_map = {}  # for debugging
        self.run: Run | None = None
        self.run_step: RunStep | None = None
        self.message_content: str | None = None
        self.message_references: Dict[str, cl.Message] = {}
        self.message: cl.Message | None = None
        self.current_event: AssistantStreamEvent | None = None

    async def on_text_created(self, text: Text) -> str:
        self.message_content = text.value

        print("\nassistant > ", end="", flush=True)

        return self.message_content

    async def on_message_created(self, message: Message) -> None:

        self.message = cl.Message(content='')

        message_id = message.id
        # Add the message to message references when it's created
        if message_id:
            self.message_references[message_id] = self.message

        self.message_references[message.id] = self.message
        await self.message_references[message.id].send()

    async def on_message_delta(self, delta: MessageDelta, snapshot: Message):
        print(delta.content[0].text.value, end="", flush=True)

        if snapshot.id in self.message_references:
            self.message_references[snapshot.id] = self.message

        # Update the message content
        self.message.content = snapshot.content[0].text.value
        await self.message.update()

    async def on_tool_call_created(self, tool_call):
        print(f"\nassistant > {tool_call.type}\n", flush=True)

    async def on_tool_call_delta(self, delta, snapshot):
        if delta.type == 'code_interpreter':
            if delta.code_interpreter.input:
                print(delta.code_interpreter.input, end="", flush=True)
            if delta.code_interpreter.outputs:
                print(f"\n\noutput >", flush=True)
                for output in delta.code_interpreter.outputs:
                    if output.type == "logs":
                        print(f"\n{output.logs}", flush=True)

    async def on_run_step_delta(self, delta: RunStepDelta, snapshot: RunStep) -> None:
        if isinstance(delta.step_details.type, ToolCallDeltaObject):
            for tool_call in delta.step_details.tool_calls:
                if isinstance(tool_call,FunctionToolCallDelta):
                    # check if step status is pending,
                    # call tool, submit results &c..
                    pass




    async def on_run_step_done(self, run):
        logging.info(self.event_map)
        logging.info(self.message)

    async def on_event(self, event):
        event_type = type(event).__name__
        if event_type in self.event_map:
            self.event_map[event_type] += 1
        else:
            self.event_map[event_type] = 1

    @property
    def current_event(self) -> AssistantStreamEvent | None:
        return self._current_event

    @current_event.setter
    def current_event(self, event: AssistantStreamEvent):
        self._current_event = event
