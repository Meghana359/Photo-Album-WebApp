import json
import boto3
import requests
from requests_aws4auth import AWS4Auth

def get_url_from_elasticsearch(qStr):
    print("Querying ElasticSearch domain for [%s] label" % (qStr))
    region = 'us-east-1' 
    service = 'es'
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
    url = 'https://vpc-photos-lgohg47uxwro3xok5c3rcgu2nu.us-east-1.es.amazonaws.com/photos/_search'
    query = {
                "size": 10,
                "query": {
                    "query_string": {
                      "default_field": "labels",
                      "query": qStr
                    }
                }
            }

    headers = { "Content-Type": "application/json",
                "Access-Control-Allow-Origin": '*'
    }

    # Make the signed HTTP request
    response = requests.post(url, auth=awsauth, headers=headers, data=json.dumps(query))
    # print(response.text)
    return json.loads(response.text)

def parse_url_list(result):
    photos_url_list = []
    result_hits = result["hits"]["hits"]
    for res in result_hits:
        photos_url_list.append("https://photostorebucket.s3.amazonaws.com/" + res["_source"]["objectKey"])
    return photos_url_list

def parse_lex_response(lex_resp, uid):
    timestamp = lex_resp["ResponseMetadata"]["HTTPHeaders"]["date"]
    resp_code = lex_resp["ResponseMetadata"]["HTTPStatusCode"]
    text = lex_resp["message"]
    print("Amazon Lex response: " + text)
    if not (("What do you want to search" in text) or ("Sorry," in text)):
        intent = lex_resp['intentName']
        if intent == 'SearchIntent':
            queryStringList = [slot_val for slot_key, slot_val in lex_resp['slots'].items() if ('qStr' in slot_key and slot_val)]
            return queryStringList
        return None
    return None

def lambda_handler(event, context):
    client = boto3.client('lex-runtime')
    text = event["queryString"]
    uid = "human"
    print("queryString in request: " + text)
    # print("Sending [" + text + "] to Amazon Lex")
    lexResponse = client.post_text(botName='PhotoAlbumSearch', botAlias='Prod', userId=uid, inputText=text)
    # print(lexResponse)
    photos_url_list = []
    queryStringList = parse_lex_response(lexResponse, uid)
    if queryStringList is None:
        return {
            'statusCode': 200,
            'body': ''
        }
    # print("Original queryStringList = ", end='')
    # print(queryStringList)
    queryStringList = list(set(queryStringList))
    # print("Unique queryStringList = ", end='')
    # print(queryStringList)
    for label in queryStringList:
        # print("Searching for " + label)
        result = get_url_from_elasticsearch(label)
        photos_url_list += parse_url_list(result)
        # print(photos_url_list)
    if photos_url_list and (len(photos_url_list) > 0):
        photos_url_list = list(set(photos_url_list))
        print(photos_url_list)
        return {
            'statusCode': 200,
            'body': json.dumps(photos_url_list)
        }
    return {
        'statusCode': 200,
        'body': ''
    }
