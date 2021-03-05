import json
import boto3

from common import continue_prompt
import aws_region

_resource_types = {}


def get_instances(client):
    instances = []
    for reservation in client.describe_instances()["Reservations"]:
        instances.append(
            list(
                map(
                    lambda x: {
                        "resource-id": x["InstanceId"],
                        "type": "instance",
                        "tags": x.get("Tags", None),
                    },
                    reservation["Instances"],
                )
            )
        )
    instances = [item for sublist in instances for item in sublist]
    return instances


def get_vpcs(client):
    return list(
        map(
            lambda x: {
                "resource-id": x["VpcId"],
                "type": "vpc",
                "tags": x.get("Tags", None),
            },
            client.describe_vpcs()["Vpcs"],
        )
    )


def get_images(client):
    return list(
        map(
            lambda x: {
                "resource-id": x["ImageId"],
                "type": "image",
                "tags": x.get("Tags", None),
            },
            client.describe_images(Owners=["self"])["Images"],
        )
    )


def get_subnets(client):
    return list(
        map(
            lambda x: {
                "resource-id": x["SubnetId"],
                "type": "subnet",
                "tags": x.get("Tags", None),
            },
            client.describe_subnets()["Subnets"],
        )
    )


def get_route_tables(client):
    return list(
        map(
            lambda x: {
                "resource-id": x["RouteTableId"],
                "type": "route_table",
                "tags": x.get("Tags", None),
            },
            client.describe_route_tables()["RouteTables"],
        )
    )


def get_snapshots(client):
    return list(
        map(
            lambda x: {
                "resource-id": x["SnapshotId"],
                "type": "route_table",
                "tags": x.get("Tags", None),
            },
            client.describe_snapshots(OwnerIds=["self"])["Snapshots"],
        )
    )


resource_mappings = {
    "vpc": get_vpcs,
    "image": get_images,
    "subnet": get_subnets,
    "route-table": get_route_tables,
    "snapshot": get_snapshots,
    "instance": get_instances,
}


def load_resources():
    global _resource_types
    global ec2

    # ec2_resource = boto3.resource("ec2", region_name=aws_region.get())
    ec2_client = boto3.client("ec2", region_name=aws_region.get())
    resource_types = json.load(open("./resource_types.json"))["resource_types"]

    resources = []

    for resource_type in resource_types:
        resources.append(resource_mappings[resource_type](ec2_client))

    resources = [item for sublist in resources for item in sublist]
    print("resources: ", resources)

    # print(">>>>>>>>>>    EC2 Instances    >>>>>>>>>>>>")
    # instances = get_instances(ec2_client)
    # print("instances: ", instances)

    # # for reservation in ec2_client.describe_instances()["Reservations"]:
    # #     for instance in reservation["Instances"]:
    # #         print(
    # #             "Id: {0}\nTags: {1}\n".format(
    # #                 instance["InstanceId"],
    # #                 instance.get("Tags", None),
    # #             )
    # #         )

    # # vpcs
    # print(">>>>>>>>>>    Vpcs    >>>>>>>>>>>>")
    # vpcs = get_vpcs(ec2_client)
    # print("vpcs: ", vpcs)

    # # for vpc in ec2_client.describe_vpcs()["Vpcs"]:
    # #     print(
    # #         "Id: {0}\nTags: {1}\n".format(
    # #             vpc["VpcId"],
    # #             vpc["Tags"],
    # #         )
    # #     )

    # print(">>>>>>>>>>    Images    >>>>>>>>>>>>")
    # images = get_images(ec2_client)
    # print("images: ", images)

    # print(">>>>>>>>>>    Subnets    >>>>>>>>>>>>")
    # images = get_subnets(ec2_client)
    # print("images: ", images)

    # print(">>>>>>>>>>    RouteTables    >>>>>>>>>>>>")
    # route_tables = get_route_tables(ec2_client)
    # print("route_tables: ", route_tables)

    # print(">>>>>>>>>>    Snapshots    >>>>>>>>>>>>")
    # snapshots = get_snapshots(ec2_client)
    # print("snapshots: ", snapshots)

    continue_prompt()
