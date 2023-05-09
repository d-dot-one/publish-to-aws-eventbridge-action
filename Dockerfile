FROM python:3.9.16 as base

LABEL "com.github.actions.name"="Publish to an AWS Eventbridge Endpoint"
LABEL "com.github.actions.description"="Publish a message an AWS Eventbridge Endpoint"
LABEL description="Publish a message to an AWS Eventbridge Endpoint"
LABEL homepage="https://github.com/d-dot-one/publish-to-eventbridge-action"
LABEL maintainer="d-dot-one"
LABEL repository="https://github.com/d-dot-one/publish-to-eventbridge-action"

# Setup env
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONFAULTHANDLER 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED=1

FROM base AS python-dependencies

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends apt-utils gcc && \
    pip install --upgrade pip && \
    pip install pipenv

COPY Pipfile .
COPY Pipfile.lock .

RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy

FROM python-dependencies as runtime

COPY --from=python-dependencies /.venv /.venv
ENV PATH="/.venv/bin:$PATH"
ENV PYTHONPATH=".:$PATH"

ARG USER_NAME="publish"
ARG GROUP_NAME="github-action"
ARG HOME_DIR="/usr/${USER_NAME}"

RUN mkdir ${HOME_DIR} && \
    groupadd ${GROUP_NAME} &&  \
    useradd -d ${HOME_DIR} -s /bin/bash -g ${GROUP_NAME} ${USER_NAME} && \
    chown -R ${USER_NAME}:${GROUP_NAME} ${HOME_DIR}

RUN pipenv install --deploy --verbose

WORKDIR ${HOME_DIR}
USER ${USER_NAME}

LABEL version="0.1.1"

COPY action/publish_to_eventbridge.py ${HOME_DIR}
COPY action/__init__.py ${HOME_DIR}

RUN echo "#!/bin/bash\npipenv run python /usr/${USER_NAME}/publish_to_eventbridge.py" > ./entrypoint.sh && \
    chmod u+x ./entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
