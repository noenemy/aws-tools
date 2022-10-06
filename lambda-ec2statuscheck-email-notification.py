import json
import boto3
import logging

import time
import datetime
import random
from time import sleep

print('Loading function')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):

    print("Received event: " + json.dumps(event, indent=2))
    message = json.loads(event['Records'][0]['Sns']['Message'])
    #message = json.loads(event['Message']) -- for local testing only

    #logger.info(message)

    #Retrieve SNS message items
    accountId = message['AWSAccountId']
    alarmName = message['AlarmName']
    instanceId = message['Trigger']['Dimensions'][0]['value']
    statusChangeTime = message['StateChangeTime']
    
    ec2 = boto3.client('ec2')
    response = ec2.describe_instances(InstanceIds = [instanceId])
    instance = response['Reservations'][0]['Instances'][0]
    
    # get private IP address
    privateIPAddress = instance['PrivateIpAddress']
    
    # get hostName
    hostName = '(N/A)'
    for tag in instance['Tags']:
        if tag['Key'] == 'Name':
            hostName = tag['Value']
    
    #Build message body
    subject = "Instance status checks failed. " + instanceId
    
    body = "Hello,\n"
    body += "The monitoring system found that an instance staus checks failure occurred as below.\n"
    body += "\nAccount Id : " + accountId
    body += "\nInstance Id : " + instanceId
    body += "\nHost Name : " + hostName
    body += "\nPrivate IP Address : " + privateIPAddress
    body += "\nEvent Time : " + statusChangeTime
    body += "\n\nPlease take a look.\n\n"

    logger.info(subject)
    logger.info(body)
    
    # send email using SES
    ses = boto3.client("ses", region_name="ap-northeast-2")
    CHARSET = "UTF-8"
    SENDER_EMAIL = "sender@email.com"
    RECEPIENT_EMAIL = "recepient@email.com"
    
    response = ses.send_email(
        Destination={
            "ToAddresses": [
                RECEPIENT_EMAIL,
            ],
        },
        Message={
            "Body": {
                "Text": {
                    "Charset" : CHARSET,
                    "Data" : body,
                }
            },
            "Subject": {
                "Charset" : CHARSET,
                "Data" : subject,

            },
        },
        Source=SENDER_EMAIL)
        
    return
