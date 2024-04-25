```
Title: OpenAI Assistant API with Chainlit
Tags: [openai, assistant-api]
```

# OpenAI Assistant API with Chainlit

This is a fork of the chainlit-cookbook example. We have addded some annotation handling code to it, and have updated it to the new V2 API, but it is not end to end complete. 

## Features

- **Interactive UI**: Chainlit provides an interactive user interface for inputting queries and displaying responses.

## Quickstart

To get started with the OpenAI Assistant API with Chainlit, follow these steps:

1. Clone the repository and navigate to the `openai-assistant` directory.
2. Install the required dependencies using `pip install -r requirements.txt`.
3. Set up your environment variables by creating a `.env` file with your `OPENAI_API_KEY` and `ASSISTANT_ID`.
4. ~~~Run the `create_assistant.py` script to create an assistant instance.~~~ Create Assistant has not been updated for the V2 endpoint, so you best create one manually and load the ID into your env. 
5. Start the Chainlit app by running `app.py`.

You should also be able to use the Dockerfile to build and run the app as well, although you will have to pass all needed env vars.