import json
import os
from datetime import datetime
from typing import List, Dict, Any
import chainlit as cl
from chainlit.logger import logger
from openai.types.beta.threads import (
    Message as ThreadMessage,
    TextContentBlock as MessageContentText,
    ImageFileContentBlock as MessageContentImageFile
)
from openai.types.beta.threads.runs import RunStep
from openai.types.beta.threads.runs.tool_calls_step_details import ToolCall

from annotations import build_message_with_annotations


async def process_thread_message(
        message_references: Dict[str, cl.Message],
        thread_message: ThreadMessage,
        client
):
    # Loop through each message content with the content and index
    for idx, content_message in enumerate(thread_message.content):
        # Generate a unique ID for each message using the thread ID and index
        id = thread_message.id + str(idx)
        # Check if the message content is of type text
        if isinstance(content_message,
                      MessageContentText):
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


async def step_logic(
        thread_id: str,
        human_query: str,
        file_ids: List[str] = [],
        client=None
):
    # Add the message to the thread
    await client.beta.threads.messages.create(
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

        if run.status == "completed" and thread_message.content is None:
            thread_message.content = "An error occurred, please try again later or contact support"
            await process_thread_message(message_references, thread_message)

        if run.status in ["cancelled", "failed", "completed", "expired"]:
            break


async def process_tool_call(
        step_references: Dict[str, cl.Step],
        step: RunStep,
        tool_call: ToolCall,
        name: str,
        input: Any,
        output: Any,
        show_input: str = None,
):
    cl_step = None
    update = False
    if tool_call.id not in step_references:
        cl_step = cl.Step(
            name=name,
            type="tool",
            parent_id=cl.context.current_step.id,
            show_input=show_input,
        )
        step_references[tool_call.id] = cl_step
    else:
        update = True
        cl_step = step_references[tool_call.id]

    if step.created_at:
        cl_step.start = datetime.fromtimestamp(step.created_at).isoformat()
    if step.completed_at:
        cl_step.end = datetime.fromtimestamp(step.completed_at).isoformat()
    cl_step.input = input
    cl_step.output = output

    if update:
        await cl_step.update()
    else:
        await cl_step.send()


class DictToObject:
    def __init__(self, dictionary):
        for key, value in dictionary.items():
            if isinstance(value, dict):
                setattr(self, key, DictToObject(value))
            else:
                setattr(self, key, value)

    def __str__(self):
        return "\n".join(f"{key}: {value}" for key, value in self.__dict__.items())
