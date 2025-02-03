import json
import boto3


sns_client = boto3.client("sns")

region_name = "us-west-2"
session = boto3.session.Session()
secrets_manager = session.client(
    service_name='secretsmanager',
    region_name=region_name
)


def get_secret(secret_name):
    response = secrets_manager.get_secret_value(SecretId=secret_name)
    return json.loads(response["SecretString"])


secrets = get_secret("cx-app")
SNS_TOPIC_ARN = secrets["SNS_TOPIC_ARN"]

def lambda_handler(event, context):
    messages = []

    for record in event["Records"]:
        print(f"Start handling record: {record}")
        body = record["body"]

        try:
            parsed_body = json.loads(body)
        except json.JSONDecodeError:
            parsed_body = body

        messages.append(parsed_body)

    combined_message = json.dumps({"messages": messages}, indent=2, ensure_ascii=False)

    response = sns_client.publish(
        TopicArn=SNS_TOPIC_ARN,
        Message=combined_message
    )

    return {"statusCode": 200, "body": f"Batch messages processed. Batch size: {len(messages)}"}
