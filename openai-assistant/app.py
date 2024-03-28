import json
import logging
import os
from typing import Dict, List

import chainlit as cl
from openai import AsyncOpenAI
from chainlit_utils import process_files, DictToObject, process_tool_call, tool_map
from annotations import build_message_with_annotations
from chainlit.types import ThreadDict
from dotenv import load_dotenv
from openai.types.beta import Thread
from openai.types.beta.threads import (
    MessageContentImageFile,
    MessageContentText,
    ThreadMessage,
)

logging.basicConfig(level=logging.INFO)

load_dotenv()

api_key = os.environ.get("OPENAI_API_KEY")
client = AsyncOpenAI(api_key=api_key)

logger = logging.getLogger("chainlit")


@cl.on_chat_start
async def start_chat():
    # Create a new thread with the OpenAI API
    thread = await client.beta.threads.create()  # type: Thread
    cl.user_session.set("thread", thread)

    # Send the initial welcome message to the user
    await cl.Message(author="AFGE V.S.", content="Hi, I am the AFGE virtual steward! How can I help you today?").send()


@cl.author_rename
def rename(orig_author: str):
    rename_dict = {"assistant": "AFGE V.S."}
    return rename_dict.get(orig_author, orig_author)


@cl.on_chat_resume
async def on_chat_resume(thread: ThreadDict):
    steps = thread.get('steps')

    # Find the right step that has the thread id we need.
    # Once found, retrieve it and pass it to the  on_message function.
    # Since we retrieved it and it's a thread, no modifications are needed to on_message.
    for step in steps:
        if step['input'] != '':
            parsed_input = json.loads(step['input'])
            kwargs = parsed_input.get('kwargs', {})
            thread_id = kwargs.get('thread_id', None)
            logger.info(f"Resuming chat with thread ID: {thread_id}")
            thread = await client.beta.threads.retrieve(thread_id)
            break
    if thread.id is None:
        response_content = "The old thread could not be fetched."
    else:
        response_content = "Welcome back! I'm ready to assist you. How can I help you today?"
    cl.user_session.set("thread", thread)
    await cl.Message(author="AFGE V.S.", content=response_content).send()


async def process_thread_message(
        message_references: Dict[str, cl.Message], thread_message: ThreadMessage
):
    # Loop through each message content with the content and index
    for idx, content_message in enumerate(thread_message.content):
        # Generate a unique ID for each message using the thread ID and index
        id = thread_message.id + str(idx)
        # Check if the message content is of type text
        if isinstance(content_message, MessageContentText):
            # If the message ID already exists in the reference dictionary
            if id in message_references:
                # Retrieve the existing message from references
                msg = message_references[id]

                formatted_message = build_message_with_annotations(thread_message)
                formatted_content = formatted_message.content

                # Update the message content with the new text
                # msg.content = content_message.text.value
                msg.content = formatted_content
                msg.elements = formatted_message.elements

                await msg.update()
            else:

                formatted_message = build_message_with_annotations(thread_message)

                # If the message ID does not exist, create a new message and add it to the references
                message_references[id] = cl.Message(
                    author=thread_message.role, content=formatted_message.content, elements=formatted_message.elements
                )
                # Asynchronously send the newly created message
                await message_references[id].send()
        # Check if the message content is of type image file
        elif isinstance(content_message, MessageContentImageFile):
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

            # If the message ID does not exist in the reference dictionary
            if id not in message_references:
                # Create a new message with no text content but including the image element
                message_references[id] = cl.Message(
                    author=thread_message.role,
                    content="",
                    elements=elements,
                )
                # Asynchronously send the newly created message
                await message_references[id].send()
        else:
            logger.error("unknown message type", type(content_message))


@cl.step(name="Assistant", type="run", root=True)
async def run(thread_id: str, human_query: str, file_ids: List[str] = []):
    # Add the message to the thread
    init_message = await client.beta.threads.messages.create(
        thread_id=thread_id, role="user", content=human_query, file_ids=file_ids
    )

    assistant_id = os.environ.get("ASSISTANT_ID")

    # Create the run
    run = await client.beta.threads.runs.create(
        thread_id=thread_id, assistant_id=assistant_id
    )

    message_references = {}  # type: Dict[str, cl.Message]
    step_references = {}  # type: Dict[str, cl.Step]
    tool_outputs = []
    # Periodically check for updates
    while True:
        thread_message = None

        run = await client.beta.threads.runs.retrieve(
            thread_id=thread_id, run_id=run.id
        )

        # Fetch the run steps
        run_steps = await client.beta.threads.runs.steps.list(
            thread_id=thread_id, run_id=run.id, order="asc"
        )

        for step in run_steps.data:
            # Fetch step details
            run_step = await client.beta.threads.runs.steps.retrieve(
                thread_id=thread_id, run_id=run.id, step_id=step.id
            )
            step_details = run_step.step_details
            # Update step content in the Chainlit UI
            if step_details.type == "message_creation":
                thread_message = await client.beta.threads.messages.retrieve(
                    message_id=step_details.message_creation.message_id,
                    thread_id=thread_id,
                )
                await process_thread_message(message_references, thread_message)

            if step_details.type == "tool_calls":
                for tool_call in step_details.tool_calls:
                    if isinstance(tool_call, dict):
                        tool_call = DictToObject(tool_call)

                    if tool_call.type == "code_interpreter":
                        await process_tool_call(
                            step_references=step_references,
                            step=step,
                            tool_call=tool_call,
                            name=tool_call.type,
                            input=tool_call.code_interpreter.input
                                  or "# Generating code",
                            output=tool_call.code_interpreter.outputs,
                            show_input="python",
                        )

                        tool_outputs.append(
                            {
                                "output": tool_call.code_interpreter.outputs or "",
                                "tool_call_id": tool_call.id,
                            }
                        )

                    elif tool_call.type == "retrieval":
                        await process_tool_call(
                            step_references=step_references,
                            step=step,
                            tool_call=tool_call,
                            name=tool_call.type,
                            input="Retrieving information",
                            output="Retrieved information",
                        )

                    elif tool_call.type == "function":
                        function_name = tool_call.function.name
                        function_args = json.loads(tool_call.function.arguments)

                        function_output = tool_map[function_name](
                            **json.loads(tool_call.function.arguments)
                        )

                        await process_tool_call(
                            step_references=step_references,
                            step=step,
                            tool_call=tool_call,
                            name=function_name,
                            input=function_args,
                            output=function_output,
                            show_input="json",
                        )

                        tool_outputs.append(
                            {"output": function_output, "tool_call_id": tool_call.id}
                        )
            if (
                    run.status == "requires_action"
                    and run.required_action.type == "submit_tool_outputs"
            ):
                await client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread_id,
                    run_id=run.id,
                    tool_outputs=tool_outputs,
                )

        await cl.sleep(2)  # Refresh every 2 seconds

        if run.status is "completed" and thread_message.content is None:
            thread_message.content = "An error occurred, please try again later or contact support"
            await process_thread_message(message_references, thread_message)

        if run.status in ["cancelled", "failed", "completed", "expired"]:
            break


@cl.on_message
async def on_message(message_from_ui: cl.Message):
    thread = cl.user_session.get("thread")  # type: Thread
    files_ids = await process_files(message_from_ui.elements)
    print(thread)
    await run(
        thread_id=thread.id, human_query=message_from_ui.content, file_ids=files_ids
    )
