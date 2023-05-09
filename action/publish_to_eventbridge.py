""" This module support the publishing of a message to an AWS SNS topic """
import datetime
import json
import logging
import os
import re
import sys
from typing import Any, Dict, Optional, List

import boto3
from botocore.client import BaseClient
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


class EventbridgeConnection:
    """ create a connection to AWS SNS and perform various operations """
    ACCESS_KEY_REGEX = r'^((?:ASIA|AKIA|AROA|AIDA)([A-Z0-7]{16}))$'
    REGION_REGEX = r'^(us(-gov)?|ap|ca|cn|eu|sa)-(central|(north|south)?(east|west)?)-(\d)'
    SECRET_KEY_REGEX = r'^([a-zA-Z0-9+/]{40})$'
    # pylint: disable=line-too-long
    EVENTBRIDGE_ENDPOINT_REGEX = r'^\w{1,}.\w{1,}$'

    def __init__(self,
                 access_key_id: str = '',
                 secret_access_key: str = '',
                 region_name: str = '',
                 eventbridge_endpoint: str = '',
                 event_bus_name_or_arn: str = '',
                 ):
        self.obfuscated_access_key_id: str = ''
        self.obfuscated_secret_access_key: str = ''

        aki = access_key_id or os.environ.get('AWS_ACCESS_KEY_ID')
        self._access_key_id: str = self._verify_and_set_access_key_id(
            access_key_id=aki,
        )

        sak = secret_access_key or os.environ.get('AWS_SECRET_ACCESS_KEY')
        self.__secret_access_key: str = self._verify_and_set_secret_access_key(
            secret_access_key=sak,
        )

        region = region_name or os.environ.get('AWS_REGION')
        self.region: str = self._verify_and_set_region(
            region=region,
        )

        event_endpoint = eventbridge_endpoint \
                         or os.environ.get('AWS_EVENTBRIDGE_ENDPOINT')
        self.eventbridge_endpoint: str = self._verify_and_set_eventbridge_endpoint(
            endpoint=event_endpoint,
        )

        self.event_bus_name_or_arn = event_bus_name_or_arn or \
                                     os.environ.get('AWS_EVENTBUS_NAME_OR_ARN')

        self.client = self._create_eventbridge_client()

    def _verify_and_set_access_key_id(self, access_key_id: str = '') -> str:
        """
        Verify that the access key is appears valid.

        :param str access_key_id: The AWS IAM user's access key ID. This is a
                                  string of 20 characters
        :return str access_key_id: The verified AWS IAM user's access key id
        """
        if not (access_key_id and isinstance(access_key_id, str)):
            logger.warning(
                f'Malformed access key ID. Expected a string, got '
                f'{type(access_key_id)} for access key '
                f'{str(self.obfuscated_access_key_id)}')
            self._access_key_id = ''
            raise TypeError

        result = re.match(self.ACCESS_KEY_REGEX, access_key_id)

        if not result:
            message = f'The provided AWS access key ID does not appear to be ' \
                      f'valid: {str(access_key_id)}'
            logger.warning(message)
            raise ValueError(message)

        try:
            self.obfuscated_access_key_id = self._obfuscate_key(
                key=access_key_id,
            )
        except Exception as err:
            logger.exception(f'Unable to obfuscate the passed access key ID '
                             f'({self.obfuscated_access_key_id}): {str(err)}')
            raise Exception from err

        return access_key_id

    def _verify_and_set_secret_access_key(self, secret_access_key: str) -> str:
        """
        Verify that the secret access key appears valid.

        :param str secret_access_key: The AWS IAM user's secret access key. This
                                      is a string of 40 characters
        :returns str secret_access_key: The verified AWS IAM user's secret
                                        access key
        """
        if not (secret_access_key and isinstance(secret_access_key, str)):
            logger.warning(
                f'Malformed secret access key. Expected a string, got '
                f'{type(secret_access_key)}')
            self.__secret_access_key = ''
            raise TypeError

        result = re.match(self.SECRET_KEY_REGEX, secret_access_key)

        if not result:
            message = f'The provided AWS secret access key does not appear to ' \
                      f'be valid: {str(secret_access_key)}'
            logger.warning(message)
            raise ValueError(message)

        try:
            self.obfuscated_secret_access_key = self._obfuscate_key(
                key=secret_access_key,
            )
        except Exception as err:
            logger.exception(
                f'Unable to obfuscate the secret access key: {str(err)}')
            raise Exception from err

        return secret_access_key

    def _verify_and_set_region(self, region: str) -> str:
        """
        Verify that the AWS region appears valid.

        :param str region: The AWS region in which to operate
        :returns str region: The verified AWS region in which to operate
        """
        if not (region and isinstance(region, str)):
            logger.warning(
                f'Malformed AWS region. Expected a string, got {type(region)}')
            self.region = ''
            raise TypeError

        result = re.match(self.REGION_REGEX, region)

        if not result:
            message = f'The provided AWS region does not appear to be valid for ' \
                      f'access key ID ({self.obfuscated_access_key_id}): ' \
                      f'{str(region)}'
            logger.warning(message)
            raise ValueError(message)

        return region

    def _verify_and_set_eventbridge_endpoint(self, endpoint: str) -> str:
        """
        Verify that the AWS Eventbridge endpoint appears valid.

        :param str endpoint: The AWS Eventbridge endpoint name
        :returns str endpoint: The verified AWS Eventbridge endpoint
        """
        if not (endpoint and isinstance(endpoint, str)):
            logger.warning(
                f'Malformed SQS queue URL. Expected a string, got '
                f'{type(endpoint)} -- {str(endpoint)}')
            self._queue_url = ''
            raise TypeError

        result = re.match(self.EVENTBRIDGE_ENDPOINT_REGEX, endpoint)

        if not result:
            message = f'The provided SQS queue URL does not appear to be ' \
                      f'valid for access key ID ' \
                      f'({self.obfuscated_access_key_id}): {str(endpoint)}'
            logger.warning(message)
            raise ValueError(message)

        return endpoint

    @staticmethod
    def _obfuscate_key(key: str) -> Optional[str]:
        """
        Obfuscate the sensitive AWS access key ID or secret key ID by
        returning the initial characters, some asterisks and the final 4
        characters.

        :param str key: The key (expected to be an access key ID or secret access key)
        :return str: The obfuscated key or None object
        """
        obfuscated_key: Optional[str] = 'NoParsableKey'
        key_length = len(key)

        if key_length not in (20, 40):
            raise ValueError(
                f'Incorrect key length for obfuscation. Expected 20 or 40, '
                f'got {key_length}')

        if len(key) == 20:
            obfuscated_key = f'{key[:4]}{"*"*12}{key[-4:]}' if key else None
        elif len(key) == 40:
            obfuscated_key = f'{key[:8]}{"*"*28}{key[-4:]}' if key else None

        return obfuscated_key

    def _create_eventbridge_client(self) -> BaseClient:
        """
        Create a simple AWS SQS client. This client can be used with any of the
        AWS SQS endpoints by referencing the client (i.e.
        `self.client.send_message()`)
        """
        eventbridge_client: BaseClient = boto3.client(
            'eventbridge',
            aws_access_key_id=self._access_key_id,
            aws_secret_access_key=self.__secret_access_key,
            region_name=self.region,
        )
        if not (eventbridge_client and isinstance(eventbridge_client, BaseClient)):
            raise ClientError

        return eventbridge_client

    def create_message(self, raw_messages: list, event_source: str, event_bus_name_or_arn: str) -> List:
        if not (raw_messages and isinstance(raw_messages, list)):
            logger.warning(
                f'Malformed raw messages. Expected a list, got '
                f'{type(raw_messages)} -- {str(raw_messages)}')
            raise TypeError

        if not (event_source and isinstance(event_source, str)):
            logger.warning(
                f'Malformed event source. Expected a string, got '
                f'{type(event_source)} -- {str(event_source)}')
            raise TypeError

        if not (event_bus_name_or_arn and isinstance(event_bus_name_or_arn, str)):
            logger.warning(
                f'Malformed event bus name or ARN. Expected a str, got '
                f'{type(event_bus_name_or_arn)} -- {str(event_bus_name_or_arn)}')
            raise TypeError

        messages: list = []

        for raw_message in raw_messages:
            if not (raw_message and isinstance(raw_message, dict)):
                logger.warning(
                    f'Malformed raw message. Expected a dict, got '
                    f'{type(raw_message)} -- {str(raw_message)}')
                continue

            message: dict = {
                'Time': datetime.datetime.now(),
                'Source': event_source,
                'Resources': [],
                'DetailType': event_source,
                'Detail': raw_message,
                'EventBusName': event_bus_name_or_arn,
                'TraceHeader': '',  # todo: fixme
            }

            messages.append(message)

        return messages

    def send_message(self, list_data: list) -> Dict[str, Any]:
        """
        Publish a message to an SNS topic after verifying that it is not too
        large.

        :param dict list_data: A Python list object containing the message
                               to send to AWS Eventbridge
        :return publish_response: A Python dictionary containing the response
                                  from the AWS SNS endpoint
        """
        publish_response: Dict[str, Any] = {}

        if not (list_data and isinstance(list_data, list)):
            logger.warning(
                f'Malformed data to publish to Eventbridge. Expected a list, got '
                f'{type(list_data)}')
            raise TypeError

        try:
            message = json.dumps(list_data)
        except Exception as err:
            logger.exception(f'Unable to translate data to JSON: {str(err)}')
            raise TypeError from err

        message_size = sys.getsizeof(message)

        if message_size >= 262144:
            message = f'The size of the message is too large for SNS. The ' \
                      f'service accepts messages with a byte size of 262,144 ' \
                      f'bytes or less. Total size: {str(message_size)}'
            logger.warning(message)
            raise ValueError(message)

        entries = self.create_message(
            raw_messages=message,
            event_source='github-event',
            event_bus_name_or_arn=self.event_bus_name_or_arn,
        )

        try:
            publish_response = self.client.put_events(
                Entries=[self.eventbridge_endpoint],
                EndpointId=self.eventbridge_endpoint,
            )
            if not (publish_response or isinstance(publish_response, dict)):
                raise Exception(
                    f'Malformed response from SQS send message. Expected a '
                    f'dictionary, got {type(publish_response)} -- '
                    f'{str(publish_response)}')

        except ClientError as err:
            err_msg = err.response.get('Error', {}).get('Code', {})
            if err_msg == 'InvalidParameterValue':
                logger.exception(
                    f'Unable to publish SQS message: {str(err_msg)}')
                raise Exception(err) from err
        except Exception as err:
            raise Exception(err) from err

        return publish_response


def main():
    """ run the action """
    eventbridge_connection = EventbridgeConnection()

    message = os.environ.get('MESSAGE', '')

    try:
        json_message = json.dumps(message)
    except Exception as err:
        err_msg = f'Unable to serialize the message data. Expected a ' \
                  f'serializable object, but got a {type(message)}'
        logger.exception(err_msg)
        raise TypeError from err

    message = {
        'message': json_message,
    }

    response = eventbridge_connection.send_message(
        list_data=message,
    )

    return {
        'statusCode': 200,
        'body': f'Message sent to Eventbridge endpoint '
                f'{eventbridge_connection.event_bus_name_or_arn}/'
                f'{eventbridge_connection.eventbridge_endpoint}!'
    }


if __name__ == '__main__':
    main()
