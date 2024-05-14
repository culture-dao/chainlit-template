import logging
from typing import Dict
from typing_extensions import override

import chainlit as cl
from openai.lib.streaming import AsyncAssistantEventHandler
from openai.types.beta import AssistantStreamEvent
from openai.types.beta.threads import Run, Text, Message, MessageDelta
from openai.types.beta.threads.runs import RunStep, \
    ToolCallDelta, ToolCall

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EventHandler(AsyncAssistantEventHandler):

    def __init__(self):
        super().__init__()
        self.event_map = {}  # for debugging
        self.run: Run | None = None
        self.run_step: RunStep | None = None
        self.message: cl.Message | None = None
        self.message_references: Dict[str, cl.Message] | {} = {}
        self.openAIMessage: Message | None = None
        self.current_event: AssistantStreamEvent | None = None

    async def on_text_created(self, text: Text) -> None:
        logging.info('on_text_created')

    async def on_message_created(self, message: Message) -> None:
        # Init empty message in UX
        logging.info(f'on_message_created: {message.id}')
        cl_message = cl.Message(content='')
        self.message_references[message.id] = cl_message
        await cl_message.send()
        self.message = cl_message

    async def on_message_delta(self, delta: MessageDelta, snapshot: Message):
        # print(delta.content[0].text.value, end="", flush=True)
        self.openAIMessage = snapshot
        logging.info(f'{snapshot.id}: {delta.content[0].text.value}')
        if len(delta.content) > 1:
            logging.error("Content length was more than 1!")
            raise ValueError("Content length must be 1 or less.")
        self.message.content = snapshot.content[0].text.value
        self.message_references[snapshot.id].content = snapshot.content[0].text.value
        await self.message.update()

    async def on_tool_call_created(self, tool_call):
        logging.info('on_tool_call_created')
        print(f"\nassistant > {tool_call.type}\n", flush=True)
        if tool_call.type == 'file_search':
            print("Retrieving information")

    # Not used?
    async def on_tool_call_delta(self, tool_call: ToolCallDelta, snapshot):
        logging.info('on_tool_call_delta')
        # this might be better handled on create?
        if tool_call.type == 'function':
            # function handler, check pending status, submit tool outputs
            pass

    async def on_tool_call_done(self, tool_call: ToolCall) -> None:
        logging.info('on_tool_call_done')
        if tool_call.type == 'file_search':
            print("Retrieved information")
        elif tool_call.type == 'code_interpreter':
            if tool_call.code_interpreter.input:
                print(tool_call.code_interpreter.input, end="", flush=True)
            if tool_call.code_interpreter.outputs:
                print("\n\noutput >", flush=True)
                for output in tool_call.code_interpreter.outputs:
                    if output.type == "logs":
                        print(f"\n{output.logs}", flush=True)

    async def on_run_step_done(self, run):
        logging.info(self.event_map)
        logging.info(self.message)

    async def on_event(self, event):
        event_type = type(event).__name__
        if event_type in self.event_map:
            self.event_map[event_type] += 1
        else:
            self.event_map[event_type] = 1
        if type(event).__name__ != 'ThreadMessageDelta':
            pass

    @property
    def current_event(self) -> AssistantStreamEvent | None:
        return self._current_event

    @current_event.setter
    def current_event(self, event: AssistantStreamEvent):
        self._current_event = event
