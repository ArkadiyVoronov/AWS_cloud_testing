import boto3
import sys
import os



# Определяем, запущен ли тест в CI (вне Docker)
in_ci = os.getenv("CI", "false").lower() == "true"

endpoint = "http://host.docker.internal:4566" if not in_ci else "http://localhost:4566"





def test_s3():
    s3 = boto3.client(
        's3',
        endpoint_url='http://localhost:4566',
        aws_access_key_id='test',
        aws_secret_access_key='test',
        region_name='us-east-1'
    )
    bucket_name = 'test-bucket-ci'
    s3.create_bucket(Bucket=bucket_name)
    s3.put_object(Bucket=bucket_name, Key='ci-test.txt', Body=b'OK')
    obj = s3.get_object(Bucket=bucket_name, Key='ci-test.txt')
    assert obj['Body'].read() == b'OK'
    print("✅ S3 test passed")

def test_dynamodb():
    dynamodb = boto3.resource(
        'dynamodb',
        endpoint_url='http://localstack:4566',
        aws_access_key_id='test',
        aws_secret_access_key='test',
        region_name='us-east-1'
    )
    table = dynamodb.create_table(
        TableName='TestTableCI',
        KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
        BillingMode='PAY_PER_REQUEST'
    )
    table.wait_until_exists()
    table.put_item(Item={'id': '1', 'value': 'CI works!'})
    response = table.get_item(Key={'id': '1'})
    assert response['Item']['value'] == 'CI works!'
    print("✅ DynamoDB test passed")

if __name__ == "__main__":
    test_s3()
    test_dynamodb()
    print("🎉 All LocalStack tests passed!")
