# Start from the official Python base image.
# FROM python:3.11
FROM ubuntu:latest

# Update package manager (apt-get)
# and install (with the yes flag `-y`)
# Python and Pip
RUN apt-get update && apt-get install -y python3.11 python3-pip

# Set the current working directory to /code.
# This is where we'll put the requirements.txt file and the app directory.
WORKDIR docker/

# Copy the file with the requirements to the docker directory.
# Copy only the file with the requirements first, not the rest of the code.
# As this file doesn't change often, Docker will detect it and use the cache for this step,
# enabling the cache for the next step too.
COPY ./requirements.txt /docker/requirements.txt

# Install the package dependencies in the requirements file.
# The --no-cache-dir option tells pip to not save the downloaded packages locally, as that is only if pip
# was going to be run again to install the same packages, but that's not the case when working with containers.
# The --no-cache-dir is only related to pip, it has nothing to do with Docker or containers.
RUN pip install --no-cache-dir --upgrade -r /docker/requirements.txt

# Copy the ./app directory inside the /docker directory.
# As this has all the code which is what changes most frequently the Docker cache won't be used for this or
# any following steps easily.
# So, it's important to put this near the end of the Dockerfile, to optimize the container image build times.
COPY ./app /docker/app

ENV PYTHONPATH "${PYTHONPATH}:/docker/app/"
ENV AM_I_IN_A_DOCKER_CONTAINER Yes

# Set the command to run the uvicorn server.
# CMD takes a list of strings, each of these strings is what you would type in the command line separated by spaces.

# This command will be run from the current working directory, the same /docker directory you set above
# with WORKDIR /docker.

VOLUME models /docker/
COPY models /docker/models

# Because the program will be started at /docker and inside of it is the directory ./app with your code,
# Uvicorn will be able to see and import app from app.main.
CMD ["uvicorn", "app.churn_app:app", "--host", "0.0.0.0", "--port", "80"]
