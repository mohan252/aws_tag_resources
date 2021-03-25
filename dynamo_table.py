import boto3
import aws_region
import aws_profile
import threading
import sys
import time
import csv
from common import continue_prompt

sys.stdout.flush()
_table_name = "Aws_RscTag_Tbl"

# Get the service resource
boto3.setup_default_session(profile_name=aws_profile.get())
dynamodb = boto3.resource("dynamodb", region_name=aws_region.get())


def create():
    global _table_name
    global dynamodb
    global _continue_printing

    if _table_exists():
        print("Table already exists. Delete the table and try again")
        continue_prompt()
        return
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

    start_print_progress()

    # Wait until the table exists.
    table.meta.client.get_waiter("table_exists").wait(TableName=_table_name)
    stop_print_progress()

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


def delete_all_records(prompt=True):
    global dynamodb
    global _table_name

    if _table_exists():
        table = dynamodb.Table(_table_name)
        scan = table.scan(
            ProjectionExpression="#k,resource_id",
            ExpressionAttributeNames={"#k": "tag_name"},
        )
        with table.batch_writer() as batch:
            for each in scan["Items"]:
                batch.delete_item(
                    Key={
                        "resource_id": each["resource_id"],
                        "tag_name": each["tag_name"],
                    }
                )
        print(f"Deleted all records from {_table_name} Table")
        if prompt == True:
            continue_prompt()
    else:
        print(f"Table {_table_name} not exists")
        if continue_prompt == True:
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


def export_csv(csv_file_path):
    global dynamodb
    global _table_name

    if _table_exists():
        table = dynamodb.Table(_table_name)
        response = table.scan()
        data = response["Items"]

        while "LastEvaluatedKey" in response:
            response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
            data.extend(response["Items"])
        keys = data[0].keys()
        with open(csv_file_path, "w", newline="") as output_file:
            dict_writer = csv.DictWriter(
                output_file,
                ["resource_id", "type", "tag_name", "tag_value", "delete(y/n)"],
            )
            dict_writer.writeheader()
            dict_writer.writerows(data)

        print("Export completed.")
        continue_prompt()


def import_data_from_csv(csv_file_path, replace=True):
    global dynamodb
    global _table_name

    if _table_exists():
        table = dynamodb.Table(_table_name)
        if replace == True:
            delete_all_records(prompt=False)
        print("Importing data")
        start_print_progress()
        with open(csv_file_path) as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=",")
            for row in csv_reader:
                table.put_item(Item=row)
        stop_print_progress()
        print("Import completed.")
        continue_prompt()


def get_all_items():
    global dynamodb
    global _table_name

    data = []
    if _table_exists():
        table = dynamodb.Table(_table_name)
        response = table.scan()
        data = response["Items"]

        while "LastEvaluatedKey" in response:
            response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
            data.extend(response["Items"])
    return data


def _table_exists():
    global dynamodb
    global _table_name

    try:
        response = dynamodb.meta.client.describe_table(TableName=_table_name)
        return True
    except dynamodb.meta.client.exceptions.ResourceNotFoundException:
        return False


_continue_printing = False


def _print_status():
    global _continue_printing
    while _continue_printing:
        sys.stdout.write(".")
        time.sleep(1)
        sys.stdout.flush()


def create_global_function():
    global _print_status

    def _print_status():
        global _continue_printing
        while _continue_printing:
            sys.stdout.write(".")
            time.sleep(1)
            sys.stdout.flush()
        print("\n")


create_global_function()


def start_print_progress():
    global _continue_printing
    _continue_printing = True
    threading.Thread(target=_print_status).start()


def stop_print_progress():
    global _continue_printing
    _continue_printing = False
