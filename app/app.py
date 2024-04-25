import chainlit as cl
from chainlit.input_widget import TextInput, Select
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig
from dotenv import load_dotenv

load_dotenv()

""" @cl.on_chat_start
async def on_chat_start_settings():

    settings = await cl.ChatSettings(
        [
            
            TextInput(
                id="Product Name",
                label="Product Name/Type/Category", 
                initial=""),
            TextInput(
                id="Client Name",
                label="Client Name", 
                initial=""),
            TextInput(
                id="What They Do", 
                label="What they do/sell",
                initial=""),
            TextInput(
                id="Other", 
                label="Additional Context", 
                initial=""),
        ]
    ).send()

    await setup_agent(settings) """

@cl.on_settings_update
async def setup_agent(settings):
    print("on_settings_update", settings)

@cl.set_chat_profiles
async def chat_profile():
    return [
        cl.ChatProfile(
            name="GPT-4 Turbo",
            markdown_description="The underlying LLM model is **GPT 4**.",
            icon="https://png.pngitem.com/pimgs/s/66-668806_openai-logo-openai-logo-elon-musk-hd-png.png",
        ),
        cl.ChatProfile(
            name="Claude Opus",
            markdown_description="The underlying LLM model is **Claude Opus**.",
            icon="https://res.cloudinary.com/apideck/image/upload/w_196,f_auto/v1675531888/marketplaces/ckhg56iu1mkpc0b66vj7fsj3o/listings/anthropic-logo_fb47aaa7-9725-42fb-9aeb-889c99cdccf0_r4xcuu.png",
        ),
        cl.ChatProfile(
            name="Mixtral 8x7b",
            markdown_description="The underlying LLM model is **Mixtral 8x7b**.",
            icon="https://docs.mistral.ai/img/logo-dark.svg",
        ),
        cl.ChatProfile(
            name="Google Gemini",
            markdown_description="The underlying LLM model is **Google Gemini**.",
            icon="https://img-s-msn-com.akamaized.net/tenant/amp/entityid/BB1i0xCB.img?w=512&h=512&m=6",
        )            
            ] 
#testing discord bot webhook

@cl.on_chat_start
async def on_chat_start():

    settings = await cl.ChatSettings(
        [
            Select(
                id="Template",
                label="Prompt Template",
                values=["Google Ads 1", "Google Ads 2", "YouTube - HBSUPS", "Facebook Ads 1"],
                initial_index=0),
            TextInput(
                id="Product Name",
                label="Product Name/Type/Category", 
                initial=""),
            TextInput(
                id="Client Name",
                label="Client Name", 
                initial=""),
            TextInput(
                id="What They Do", 
                label="What they do/sell",
                initial=""),
            TextInput(
                id="url", 
                label="url", 
                initial=""),
            TextInput(
                id="Other", 
                label="Additional Context", 
                initial=""),
        ]
    ).send()

    await setup_agent(settings)


    text_content = """
    
Persona: You are a world-class direct response copywriter with years of expert knowledge of all the Google Ads headlines and descriptions with the highest click-through rates and engagement rates. 

Your task: Using the text in the section called "Data:" below and visceral emotional language, write curiosity-based direct response ad copy for Google Ads.

Context: This is for Google Ads to persuade people to buy [PRODUCT NAME or TYPE or CATEGORY] from [CLIENT NAME], a [WHAT THEY DO / SELL] company.

Instructions for your output:

1) [Generate your responses without quotation marks]
2) [Write 15 short headlines that are 30 characters or less, each on a new line]
3) [Write 4 long descriptions that are 90 characters or less, each on a new line]
4) [Use novel ideas and emotional visceral language that give the reader new insights using the "Data:" section below]
5) [Voice and style guide: Write at a 5th grade level in a conversational, relatable style as if you were explaining something to a friend. Use clear, compelling, and simple language, even when explaining complex topics.]

Goal: Each headline and each description should be new, unique, and different from the previous one.

Data:
    """
    elements = [
        cl.Text(
            name="Google Ads Prompt",
            content=text_content,
            display="page",)
                ]
    model = ChatOpenAI(model="gpt-4-0125-preview", streaming=True)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a world-class direct response copywriter with years of expert knowledge of all the Google Ads headlines and descriptions with the highest click-through rates and engagement rates.",),
            ("human", "{question}"),
        ]
    )
    runnable = prompt | model | StrOutputParser()
    cl.user_session.set("runnable", runnable)


    await cl.Avatar(
        name="Mira",
        url="https://firebasestorage.googleapis.com/v0/b/speakwiz-app.appspot.com/o/public%2F0v171bjk_.png?alt=media&token=4e2d4729-564e-4f5b-9567-2ddf9037273b",
    ).send()

    await cl.Message(
        content="Welcome, ClickMaker! How can I help you today?",
        author="Mira",
        elements=elements,
        ).send()
    
    
@cl.on_message
async def on_message(message: cl.Message):
    runnable = cl.user_session.get("runnable")  # type: Runnable

    msg = cl.Message(
        content="",
        author="Mira")

    async for chunk in runnable.astream(
        {"question": message.content},
        config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    ):
        await msg.stream_token(chunk)

    await msg.send()
    #  chat_profile = cl.user_session.get("chat_profile")  ### This is a bit redundant, but I could add it later maybe.
    
    