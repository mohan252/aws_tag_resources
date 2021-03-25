import json
import boto3
from pprint import pprint

from common import continue_prompt
import aws_region
import dynamo_table

_resource_types = {}


def flatten(regular_list):
    result = []
    for item1 in regular_list:
        if isinstance(item1, list):
            for item2 in item1:
                result.append(item2)
        else:
            result.append(item1)
    return result


def transform_data(data, id_field, type):
    return list(
        map(
            lambda x: {
                "resource_id": x[id_field],
                "type": type,
                "tag_name": "null",
                "tag_value": "null",
                "delete(y/n)": "",
            }
            if x.get("Tags", None) == None
            else list(
                map(
                    lambda y: {
                        "resource_id": x[id_field],
                        "type": type,
                        "tag_name": y["Key"],
                        "tag_value": y["Value"],
                        "delete(y/n)": "",
                    },
                    x["Tags"],
                )
            ),
            data,
        )
    )


def get_instances(client):
    instances = []
    for reservation in client.describe_instances()["Reservations"]:
        instances.extend(
            transform_data(reservation["Instances"], "InstanceId", "instance")
        )
    return flatten(instances)


resource_mappings = {
    "instance": get_instances,
    "vpc": lambda client: flatten(
        transform_data(client.describe_vpcs()["Vpcs"], "VpcId", "vpc")
    ),
    "image": lambda client: flatten(
        transform_data(
            client.describe_images(Owners=["self"])["Images"], "ImageId", "image"
        )
    ),
    "subnet": lambda client: flatten(
        transform_data(client.describe_subnets()["Subnets"], "SubnetId", "subnet")
    ),
    "route-table": lambda client: flatten(
        transform_data(
            client.describe_route_tables()["RouteTables"], "RouteTableId", "route_table"
        )
    ),
    "snapshot": lambda client: flatten(
        transform_data(
            client.describe_snapshots(OwnerIds=["self"])["Snapshots"],
            "SnapshotId",
            "snapshot",
        )
    ),
    "security-group": lambda client: flatten(
        transform_data(
            client.describe_security_groups()["SecurityGroups"],
            "GroupId",
            "security_group",
        )
    ),
    "volume": lambda client: flatten(
        transform_data(client.describe_volumes()["Volumes"], "VolumeId", "volume")
    ),
    "customer-gateway": lambda client: flatten(
        transform_data(
            client.describe_customer_gateways()["CustomerGateways"],
            "CustomerGatewayId",
            "customer_gateway",
        )
    ),
    "dhcp-options": lambda client: flatten(
        transform_data(
            client.describe_dhcp_options()["DhcpOptions"],
            "DhcpOptionsId",
            "dhcp_option",
        )
    ),
    "internet-gateway": lambda client: flatten(
        transform_data(
            client.describe_internet_gateways()["InternetGateways"],
            "InternetGatewayId",
            "internet_gateway",
        )
    ),
    "network-acl": lambda client: flatten(
        transform_data(
            client.describe_network_acls()["NetworkAcls"],
            "NetworkAclId",
            "network_acl",
        )
    ),
    "network-interface": lambda client: flatten(
        transform_data(
            client.describe_network_interfaces()["NetworkInterfaces"],
            "NetworkInterfaceId",
            "network_interface",
        )
    ),
    "reserved-instances": lambda client: flatten(
        transform_data(
            client.describe_reserved_instances()["ReservedInstances"],
            "ReservedInstancesId",
            "reserved_instance",
        )
    ),
    "spot-instances-request": lambda client: flatten(
        transform_data(
            client.describe_spot_instance_requests()["SpotInstanceRequests"],
            "SpotInstanceRequestId",
            "spot_instances_requests",
        )
    ),
    "vpn-connection": lambda client: flatten(
        transform_data(
            client.describe_vpn_connections()["VpnConnections"],
            "VpnConnectionId",
            "vpn_connection",
        )
    ),
    "vpn-gateway": lambda client: flatten(
        transform_data(
            client.describe_vpn_gateways()["VpnGateways"],
            "VpnGatewayId",
            "vpn_gateway",
        )
    ),
}


def apply():
    ec2Client = boto3.client("ec2", region_name=aws_region.get())
    data = dynamo_table.get_all_items()
    for item in data:
        delete = item["delete(y/n)"]
        if delete == "y":
            print(
                f'Deleting tag for resource -> {item["resource_id"]}, type -> {item["type"]}, tag -> {item["tag_name"]}, value -> {item["tag_value"]}'
            )
            ec2Response = ec2Client.delete_tags(
                DryRun=False,
                Resources=[item["resource_id"]],
                Tags=[{"Key": item["tag_name"], "Value": item["tag_value"]}],
            )
        else:
            print(
                f'Applying tag for resource -> {item["resource_id"]}, type -> {item["type"]}, tag -> {item["tag_name"]}, value -> {item["tag_value"]}'
            )
            ec2Response = ec2Client.create_tags(
                DryRun=False,
                Resources=[item["resource_id"]],
                Tags=[{"Key": item["tag_name"], "Value": item["tag_value"]}],
            )
    continue_prompt()


def load_resources():
    global _resource_types
    global ec2

    # ec2_resource = boto3.resource("ec2", region_name=aws_region.get())
    ec2_client = boto3.client("ec2", region_name=aws_region.get())
    resource_types = json.load(open("./resource_types.json"))["resource_types"]

    resources = []
    for resource_type in resource_types:
        tag = resource_mappings[resource_type](ec2_client)
        resources.extend(tag)

    for resource in resources:
        print(resource)
    dynamo_table.insert_records(resources)
    continue_prompt()
