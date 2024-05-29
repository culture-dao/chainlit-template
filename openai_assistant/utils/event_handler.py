"""
AsyncAssistantEventHandler for Chainlit
"""

import logging
import chainlit as cl
from chainlit import Step
from openai.lib.streaming import AsyncAssistantEventHandler
from openai.types.beta.threads import Run, Text, Message, \
    TextContentBlock, ImageFileContentBlock
from openai.types.beta.threads.runs import RunStep, \
    ToolCallDelta, ToolCall
from utils.annotations import OpenAIAdapter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("chainlit")


class EventHandler(AsyncAssistantEventHandler):

    def __init__(self, client):
        super().__init__()
        self.event_map = {}  # for debugging
        self.current_message = None
        self.client = client  # Because we look up FileObjects in annotations loop.

    async def on_run_step_created(self, run_step: RunStep):
        # lookout for multiple browser tabs when testing.
        logging.debug(f"on_run_step_created {run_step.id}")

    async def on_event(self, event):
        """
        Using this for dev/debugging, so we know exactly what event sequence is going on in a run.
        """
        event_type = type(event).__name__
        if event_type in self.event_map:
            self.event_map[event_type] += 1
        else:
            self.event_map[event_type] = 1

    # async def on_message_created(self, message: Message) -> None:
    #     logging.debug(f'on_message_created: {message.id}')

    async def on_text_created(self, text: Text) -> None:
        logging.info('on_text_created')
        self.current_message = cl.Message(content='')

    async def on_text_delta(self, delta, snapshot):
        await self.current_message.stream_token(delta.value)

    async def on_text_done(self, text: Text) -> None:
        # After the message has been processed and sent handle the annotations and update the message
        message = self.current_event.data
        await process_thread_message(
            message=self.current_message,
            thread_message=message,
            client=self.client
        )
        await self.current_message.send()

    @cl.step
    async def on_tool_call_created(self, tool_call):
        step: Step = cl.context.current_step
        step.name = tool_call.type
        logging.info(f'\ton_tool_call_created {tool_call}')
        if tool_call.type == 'file_search':
            step.input = "Retrieving information"
        await step.send()

    async def on_tool_call_delta(self, tool_call: ToolCallDelta, snapshot):
        logging.info('on_tool_call_delta')
        # stub: this might be better handled on create?
        if tool_call.type == 'function':
            # we don't use this, yet...
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
        logging.debug(f"on_run_step_done {run.id}: {self.event_map}")

    async def on_text_done(self, text: Text) -> None:
        # After the message has been processed and sent handle the annotations and update the message
        message = self.current_event.data
        await process_thread_message(
            message=self.current_message,
            thread_message=message,
            client=self.client
        )


async def process_thread_message(
        message: cl.Message,
        thread_message: Message,
        client
):
    # We asserted earlier that this should only ever be one content object
    content_message = thread_message.content[0]

    # Check if the message content is of type text
    if isinstance(content_message, TextContentBlock):
        # Handle the annotations and get the updated content and elements
        adapter = OpenAIAdapter(thread_message)
        await adapter.main()
        content = adapter.get_content()
        elements = adapter.get_elements()

        # Update the message content with the new text and elements
        message.content = content
        message.elements = elements
        await message.update()
    # Check if the message content is of type image file
    elif isinstance(content_message, ImageFileContentBlock):
        # Retrieve the image file ID
        image_id = content_message.image_file.file_id
        # Asynchronously retrieve the content of the image file
        response = await client.files.with_raw_response.retrieve_content(image_id)
        # Create an image element with the retrieved content
        elements = [
            cl.Image(
                name=image_id,
                content=response.content,
                display="inline",
                size="large",
            ),
        ]
        # Create a new message with no text content but including the image element
        await cl.Message(
                author=thread_message.role,
                content="",
                elements=elements,
            ).send()
    else:
        logger.error("unknown message type", type(content_message))
