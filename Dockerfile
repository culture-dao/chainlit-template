# Use the official Python 3.10 image from Replit
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install poetry
RUN curl -sSL https://install.python-poetry.org | python -

# Add Poetry executable to the shell path
ENV PATH="${PATH}:/root/.local/bin"

# Use the full path to the Poetry executable
RUN poetry --version

# Copy the current directory contents into the container at /app
COPY . /app

# Install project dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV NAME World

# Run the application
CMD ["poetry", "run", "chainlit", "run", "openai-assistant/app.py"]
