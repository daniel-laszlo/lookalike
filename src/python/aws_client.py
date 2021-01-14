#!/usr/bin/env python
import boto3
import tempfile
import traceback
import json
import os

from lookalike import decide_between_presidents

# input_bucket_name = 'celebritylookalike'
# sqsqueue_name = 'LookalikeSubmittedJobsQueue'
# aws_region = 'eu-west-2'
# api_gateway_url = 'https://8lxphbfn9a.execute-api.eu-west-2.amazonaws.com/production'

input_bucket_name = os.environ['INPUT_BUCKET_NAME']
sqsqueue_name = os.environ['SQS_JOB_QUEUE']
aws_region = os.environ['AWS_REGION']
api_gateway_url = os.environ['API_GATEWAY_URL']

s3 = boto3.client('s3', region_name=aws_region)
sqs = boto3.resource('sqs', region_name=aws_region)
api_gateway = boto3.client('apigatewaymanagementapi', endpoint_url=api_gateway_url, region_name=aws_region)

queue = sqs.get_queue_by_name(QueueName=sqsqueue_name)


def process_images():
    """Process the image

    No real error handling in this sample code. In case of error we'll put
    the message back in the queue and make it visible again. It will end up in
    the dead letter queue after five failed attempts.
    """
    for message in queue.receive_messages(VisibilityTimeout=120, WaitTimeSeconds=20, MaxNumberOfMessages=10, MessageAttributeNames=['All']):
        try:
            if not message.message_attributes:
                print(f'Got message with no message_attributes present. {message}')
                message.change_visibility(VisibilityTimeout=0)
                continue
            connection_id = message.message_attributes.get('connectionId').get('StringValue')
            s3_key = message.message_attributes.get('s3Key').get('StringValue')
            print(f'Got message with connection_id {connection_id} and s3_key {s3_key}')

            file_path = download_file(s3_key)
            response = decide_between_presidents(file_path)
            print(response)
            send_message_to_connection(connection_id, response)
        except Exception as e:
            message.change_visibility(VisibilityTimeout=0)
            traceback.print_exc()
            continue
        else:
            print('Deleting message from queue\n===========================================================')
            message.delete()


def download_file(s3_key):
    with tempfile.NamedTemporaryFile(mode='wb', delete=False) as fp:
        s3.download_fileobj(input_bucket_name, s3_key, fp)
        print(f'Downloaded object from s3. Bucket: {input_bucket_name}, file_key: {s3_key}, saved to: {fp.name}')
        return fp.name


def send_message_to_connection(connection_id, message):
    print(f'post_to_connection: {message}, {connection_id}')
    data = json.dumps({'response': message, 'action': 'jobfinished'})
    response = api_gateway.post_to_connection(Data=data,
                                              ConnectionId=connection_id)
    print(f'Response from api gateway: {response}')


def main():
    i = 0
    while True:
        print(f'Polling for messages on queue... {i}')
        i += 1
        process_images()


if __name__ == "__main__":
    main()
