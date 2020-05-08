import json
import elasticsearch
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from datetime import datetime
import boto3
import elasticsearch.helpers

def indexData(photo,bucket,labels):
    host = 'vpc-photos-lgohg47uxwro3xok5c3rcgu2nu.us-east-1.es.amazonaws.com' 
    region = 'us-east-1' 
    
    service = 'es'
    credentials = boto3.Session().get_credentials()
    access_key='AKIAXLVHGGD7V47MHFZY'
    secret_key='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'

    awsauth = AWS4Auth(access_key,secret_key, region, service)
    es = Elasticsearch(
        hosts = [{'host': host, 'port': 443}],
        http_auth = awsauth,
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection
    )
    
    date_timestamp = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    print(date_timestamp)
    
    document = {
        'objectKey': photo,
        'bucket': bucket,
        'createdTimestamp': date_timestamp,
        'labels': labels
    }
    
    es.index(index="photos", doc_type="_doc", id=date_timestamp, body=document)
    
    print(es.get(index="photos", doc_type="_doc", id=date_timestamp))
    
    # es_response = elasticsearch.helpers.scan(es,
    #     index='photos',
    #     doc_type='_doc',
    #     query={"query": { "match_all" : {}}}
    # )

    # for item in es_response:
    #     print(json.dumps(item))

def detectLables(photo,bucket):
    labels_detected=[]
    client=boto3.client('rekognition','us-east-1')
    result = client.detect_labels(
        Image={
            "S3Object": {
                "Bucket": bucket,
                "Name": photo
            }
        },
        MinConfidence= 75,
    )
    print(result)
    for label in result['Labels']:
        labels_detected.append(label['Name'])
    return labels_detected

def lambda_handler(event, context):
  
    print(event)
    for entry in event['Records']:
        bucket=entry['s3']['bucket']['name']
        photo=entry['s3']['object']['key']
        print(bucket)
        print(photo)
    labels= detectLables(photo,bucket)
    print(labels)
    indexData(photo,bucket,labels)
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
