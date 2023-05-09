FROM public.ecr.aws/lambda/python:3.9

COPY publish_to_eventbridge.py requirements.txt ./

RUN python3.8 -m pip install -r requirements.txt -t .

# Command can be overwritten by providing a different command in the template directly.
CMD ["action.main"]
