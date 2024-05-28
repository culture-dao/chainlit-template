from io import BytesIO

import chainlit as cl
from chainlit.element import ElementBased

from utils.openai_utils import initialize_openai_client

client = initialize_openai_client()


def init():
    @cl.on_audio_chunk
    async def on_audio_chunk(chunk: cl.AudioChunk):
        if chunk.isStart:
            buffer = BytesIO()
            buffer.name = f"input_audio.{chunk.mimeType.split('/')[1]}"
            cl.user_session.set("audio_buffer", buffer)
            cl.user_session.set("audio_mime_type", chunk.mimeType)
        cl.user_session.get("audio_buffer").write(chunk.data)

    @cl.on_audio_end
    async def on_audio_end(elements: list[ElementBased]):
        audio_buffer: BytesIO = cl.user_session.get("audio_buffer")
        audio_buffer.seek(0)
        audio_file = audio_buffer.read()
        audio_mime_type: str = cl.user_session.get("audio_mime_type")

        input_audio_el = cl.Audio(
            mime=audio_mime_type, content=audio_file, name=""
        )

        await cl.Message(
            author="You",
            content="",
            type="user_message",
            elements=[input_audio_el, *elements]
        ).send()

        whisper_input = (audio_buffer.name, audio_file, audio_mime_type)
        transcription = await speech_to_text(whisper_input)

        message = await cl.Message(
            author="You",
            type="user_message",
            content=transcription,
            elements=[]
        ).send()

        on_message = cl.config.code.on_message

        await on_message(message)


@cl.step(type="tool", name="Transcription")
async def speech_to_text(audio_file):
    current_step = cl.context.current_step
    try:
        current_step.output = "Running transcription..."
        await current_step.update()

        response = await client.audio.transcriptions.create(
            model="whisper-1", file=audio_file
        )

        current_step.output = "Transcription completed"
        await current_step.update()

        return response.text

    except Exception as e:
        error_message = f"Error during transcription: {str(e)}"
        current_step.output = error_message
        await current_step.update()
        return error_message
