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

NOW = time.time()
ISONOW = datetime.datetime.utcfromtimestamp(NOW).isoformat()
THEN = NOW - 300
ISOTHEN = datetime.datetime.utcfromtimestamp(THEN).isoformat()

def lambda_handler(event, context):

    print("Received event: " + json.dumps(event, indent=2))
    message = json.loads(event['Records'][0]['Sns']['Message'])
    
    #logger.info("Message!!!")
    #logger.info(message)

    #Retrieve SNS message items
    accountId = message['AWSAccountId']
    alarmName = message['AlarmName']
    instanceId = message['Trigger']['Dimensions'][0]['value']
    statusChangeTime = message['StateChangeTime']

    #Build case message
    subject_message = "Instance status checks failed. " + instanceId
    
    case_message = "Hello,\n"
    case_message += "Our monitoring system found that an instance staus checks failure happenend as below.\n"
    case_message += "\nAccountId : " + accountId
    case_message += "\nInstance ID : " + instanceId
    case_message += "\nEvent Time : " + statusChangeTime
    case_message += "\n\nPlease let us know what caused the failure.\n\n"

    logger.info(subject_message)
    logger.info(case_message)

    # random delay for consistency
    sleep(random.uniform(1,10))
    
    support = boto3.client('support', region_name='us-east-1')
    case_list = support.describe_cases(afterTime=ISOTHEN, language='en', maxResults=100, includeResolvedCases=False)
    
    #logger.info(case_list)
    check_flag = False

    if len(case_list['cases']) == 0:
        check_flag = True
    else:
        for i in case_list['cases']:
            if subject_message.find(instanceId) != -1:
                check_flag = False
            else:
                check_flag = True
    
    if check_flag:
        logger.info("Creating a new support case...")
        case_id = support.create_case(serviceCode='amazon-elastic-compute-cloud-linux', categoryCode='instance-issue',severityCode='urgent', subject=subject_message, communicationBody=case_message, language='en')
        logger.info(case_id)
    else:
        logger.info("Case creation canceled due to the duplicate issue")
        
    return