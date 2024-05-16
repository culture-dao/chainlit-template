import json
import os
from datetime import datetime
from typing import List, Dict, Any

import chainlit as cl
from dotenv import load_dotenv
from openai.types.beta.threads.runs import RunStep
from openai.types.beta.threads.runs.tool_calls_step_details import ToolCall
from openai.types.beta.vector_stores import VectorStoreFile

from utils.assistant_handler import assistant_handler
from utils.event_handler import EventHandler
from utils.openai_utils import initialize_openai_client

ASSISTANT_NAME = os.getenv('ASSISTANT_NAME')


async def handle_tool_call(step_details, step_references, step, tool_outputs):
    tool_map = {}
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


async def step_logic(
        thread_id: str,
        human_query: str,
        file_ids: List[VectorStoreFile],
        client=None
):
    # Add the message to the thread
    await client.beta.threads.messages.create(
        thread_id=thread_id, role="user", content=human_query, attachments=file_ids
    )

    client = initialize_openai_client()
    load_dotenv(dotenv_path='../', override=True)

    e = EventHandler(client=client)

    assistant = assistant_handler.find_by_name(ASSISTANT_NAME)
    assistant_id = assistant.id

    if assistant_id is not None:
        async with client.beta.threads.runs.stream(
                thread_id=thread_id,
                assistant_id=assistant_id,
                event_handler=e,
        ) as stream:
            await stream.until_done()
    else:
        raise ValueError("Couldn't pull assistant id from .env")


async def process_tool_call(
        step_references: Dict[str, cl.Step],
        step: RunStep,
        tool_call: ToolCall,
        name: str,
        input: Any,
        output: Any,
        show_input: str = None,
):
    cl_step: cl.Step | None = None
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
