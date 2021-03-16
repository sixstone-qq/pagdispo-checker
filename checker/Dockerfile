# Follows: https://www.docker.com/blog/containerized-python-development-part-1/
# https://www.pybootcamp.com/blog/how-to-write-dockerfile-python-apps/
# First stage
FROM python:3.8 AS builder
COPY requirements.txt .

RUN pip install -U \
    pip \
    setuptools \
    wheel

# install dependencies to the local user directory (eg. /root/.local)
RUN pip install --user -r requirements.txt

# Second stage
FROM python:3.8-slim
WORKDIR /app

# Copy the deps from first stage image
COPY --from=builder /root/.local /root/.local
COPY . .

# Update PATH env var to have deps ready
ENV PATH=/root/.local:$PATH

ARG GIT_HASH
ENV GIT_HASH=${GIT_HASH:-dev}

CMD [ "python", "-m", "pagdispo.checker" ]
