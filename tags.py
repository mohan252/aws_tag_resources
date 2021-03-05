import json
import boto3

from common import continue_prompt
import aws_region

_resource_types = {}


def load_resources():
    global _resource_types
    global ec2

    # ec2_resource = boto3.resource("ec2", region_name=aws_region.get())
    ec2_client = boto3.client("ec2", region_name=aws_region.get())
    print(">>>>>>>>>>    EC2 Instances    >>>>>>>>>>>>")
    for reservation in ec2_client.describe_instances()["Reservations"]:
        for instance in reservation["Instances"]:
            print(
                "Id: {0}\nTags: {1}\n".format(
                    instance["InstanceId"],
                    instance.get("Tags", None),
                )
            )

    # vpcs
    print(">>>>>>>>>>    Vpcs    >>>>>>>>>>>>")
    for vpc in ec2_client.describe_vpcs()["Vpcs"]:
        print(
            "Id: {0}\nTags: {1}\n".format(
                vpc["VpcId"],
                vpc["Tags"],
            )
        )

    print(">>>>>>>>>>    Images    >>>>>>>>>>>>")
    for image in ec2_client.describe_images(Owners=["self"])["Images"]:
        print(
            "Id: {0}\nTags: {1}\n".format(
                image["ImageId"],
                image["Tags"],
            )
        )

    print(">>>>>>>>>>    Subnets    >>>>>>>>>>>>")
    for subnet in ec2_client.describe_subnets()["Subnets"]:
        print(
            "Id: {0}\nTags: {1}\n".format(
                subnet["SubnetId"],
                subnet.get("Tags", None),
            )
        )

    print(">>>>>>>>>>    RouteTables    >>>>>>>>>>>>")
    for route_table in ec2_client.describe_route_tables()["RouteTables"]:
        print(
            "Id: {0}\nTags: {1}\n".format(
                route_table["RouteTableId"],
                route_table.get("Tags", None),
            )
        )

    print(">>>>>>>>>>    RouteTables    >>>>>>>>>>>>")
    for route_table in ec2_client.describe_route_tables()["RouteTables"]:
        print(
            "Id: {0}\nTags: {1}\n".format(
                route_table["RouteTableId"],
                route_table.get("Tags", None),
            )
        )

    print(">>>>>>>>>>    Snapshots    >>>>>>>>>>>>")
    for snapshot in ec2_client.describe_snapshots(OwnerIds=["self"])["Snapshots"]:
        print(
            "Id: {0}\nTags: {1}\n".format(
                snapshot["SnapshotId"],
                snapshot.get("Tags", None),
            )
        )

    _resource_types = json.load(open("./resource_types.json"))
    continue_prompt()
