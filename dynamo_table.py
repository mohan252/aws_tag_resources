import boto3
import aws_region
import aws_profile
import threading
import sys
import time
from common import continue_prompt

sys.stdout.flush()
_table_name = "Aws_RscTag_Tbl"

# Get the service resource
boto3.setup_default_session(profile_name=aws_profile.get())
dynamodb = boto3.resource("dynamodb", region_name=aws_region.get())

_continue_printing = False


def create():
    global _table_name
    global dynamodb
    global _continue_printing

    print(f"Creating {_table_name} table")
    # Create the DynamoDB table.
    table = dynamodb.create_table(
        TableName=_table_name,
        KeySchema=[
            {"AttributeName": "resource_id", "KeyType": "HASH"},
            {"AttributeName": "tag_name", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "resource_id", "AttributeType": "S"},
            {"AttributeName": "tag_name", "AttributeType": "S"},
        ],
        ProvisionedThroughput={"ReadCapacityUnits": 1, "WriteCapacityUnits": 1},
    )

    _continue_printing = True
    print_status_thread = threading.Thread(target=_print_status)
    print_status_thread.start()

    # Wait until the table exists.
    table.meta.client.get_waiter("table_exists").wait(TableName=_table_name)

    _continue_printing = False
    # Print out some data about the table.
    print("\nFinished creating table.")
    continue_prompt()


def delete():
    global dynamodb
    global _table_name

    if _table_exists():
        table = dynamodb.Table(_table_name)
        table.delete()
        print(f"Deleted {_table_name} Table")
        continue_prompt()
    else:
        print(f"Table {_table_name} not exists")
        continue_prompt()


def delete_all_records():
    global dynamodb
    global _table_name

    if _table_exists():
        table = dynamodb.Table(_table_name)
        scan = table.scan(
            ProjectionExpression="#k,resource_id",
            ExpressionAttributeNames={"#k": "type"},
        )
        with table.batch_writer() as batch:
            for each in scan["Items"]:
                batch.delete_item(
                    Key={"resource_id": each["resource_id"], "type": each["type"]}
                )
        print(f"Deleted all records from {_table_name} Table")
        continue_prompt()
    else:
        print(f"Table {_table_name} not exists")
        continue_prompt()


def insert_records(data):
    global dynamodb
    global _table_name

    if _table_exists():
        table = dynamodb.Table(_table_name)
        with table.batch_writer(
            overwrite_by_pkeys=["resource_id", "tag_name"]
        ) as batch:
            for i in range(len(data)):
                batch.put_item(Item=data[i])


def _table_exists():
    global dynamodb
    global _table_name

    try:
        response = dynamodb.meta.client.describe_table(TableName=_table_name)
        return True
    except dynamodb.meta.client.exceptions.ResourceNotFoundException:
        # do something here as you require
        return False


def _print_status():
    global _continue_printing
    while _continue_printing:
        sys.stdout.write(".")
        time.sleep(1)
        sys.stdout.flush()
