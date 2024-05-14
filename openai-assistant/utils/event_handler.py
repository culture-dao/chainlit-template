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

        self.message_references: Dict[str, cl.Message] | {} = {}
        self.openAIMessage: Message | None = None
        self.current_event: AssistantStreamEvent | None = None

    async def on_run_step_created(self, run_step: RunStep):
        logging.info(f"on_run_step_created {run_step.id}")

    async def on_event(self, event):
        event_type = type(event).__name__
        if event_type in self.event_map:
            self.event_map[event_type] += 1
        else:
            self.event_map[event_type] = 1

    async def on_text_created(self, text: Text) -> None:
        logging.info('on_text_created')

    async def on_message_created(self, message: Message) -> None:
        logging.info(f'on_message_created: {message.id}')

        cl_message = cl.Message(content='')

        # Update the references so the OpenAI message id maps to the Chainlit message
        self.message_references[message.id] = cl_message

        # Send the empty message to the UI
        await cl_message.send()

    async def on_message_delta(self, delta: MessageDelta, snapshot: Message):

        # This should probably be on some 'done' event
        self.openAIMessage = snapshot

        # Make sure we only have 1 content object in the lists
        # OAI usually returns one, but let's not assume
        if len(delta.content) > 1:
            logging.error("Content length was more than 1!")
            raise ValueError("Content length must be 1 or less.")

        cl_message = self.message_references[snapshot.id]
        cl_message.content = snapshot.content[0].text.value

        # Update the message in the UI/persistence
        await cl_message.update()
        # self.message_references[snapshot.id] = cl_message

    async def on_text_done(self, text: Text) -> None:
        pass

    @cl.step
    async def on_tool_call_created(self, tool_call):
        step = cl.context.current_step
        step.name = tool_call.type
        logging.info(f'\ton_tool_call_created {tool_call}')
        if tool_call.type == 'file_search':
            step.input = "Retrieving information"
            print("Retrieving information")
        await step.send()

    # Not used?
    async def on_tool_call_delta(self, tool_call: ToolCallDelta, snapshot):
        logging.info('on_tool_call_delta')
        # this might be better handled on create?
        if tool_call.type == 'function':
            # function handler, check pending status, submit tool outputs
            pass

    @cl.step
    async def on_tool_call_done(self, tool_call: ToolCall) -> None:
        """
        On tool call actually gets thrown three times during the normal course of events,
        in the thread.run.step.completed event and once in the thread.run.completed event. Since the tool_call
        doesn't get cleared between runs, we have to make sure we're not triggering it during the message creation runs.
        """
        step = cl.context.current_step

        if (isinstance(self.current_event.data, Run)  # thread.run.completed
                or self.current_event.data.type != 'tool_calls'):  # thread.run.step.completed
            await step.remove()
            return

        step.name = tool_call.type
        logging.info(f'\ton_tool_call_done {tool_call}: {self.current_event.event}')
        if tool_call.type == 'file_search':
            step.output = "Retrieved information"
            print("Retrieved information")
        elif tool_call.type == 'code_interpreter':
            if tool_call.code_interpreter.input:
                print(tool_call.code_interpreter.input, end="", flush=True)
            if tool_call.code_interpreter.outputs:
                print("\n\noutput >", flush=True)
                for output in tool_call.code_interpreter.outputs:
                    if output.type == "logs":
                        print(f"\n{output.logs}", flush=True)
        await step.update()

    async def on_run_step_done(self, run):
        logging.info(f"on_run_step_done {run.id}: {self.event_map}")

    @property
    def current_event(self) -> AssistantStreamEvent | None:
        return self._current_event

    @current_event.setter
    def current_event(self, event: AssistantStreamEvent):
        self._current_event = event
