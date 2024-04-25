# Use the official Python 3.11 image
FROM python:3.11

# Install poetry
RUN curl -sSL https://install.python-poetry.org | python -

# Add Poetry executable to the shell path
ENV PATH="${PATH}:/root/.local/bin"

# Use the full path to the Poetry executable
RUN poetry --version

WORKDIR /app
# Copy the app directory contents into the container at /app
COPY . /app

# Install project dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Make port 8000 available to the world outside this container
EXPOSE 80


# Run the application
CMD ["chainlit", "run", "app.py"]
