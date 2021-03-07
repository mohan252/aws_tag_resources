import json
import boto3

from common import continue_prompt
import aws_region
from dynamo_table import insert_records

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
            }
            if x.get("Tags", None) == None
            else list(
                map(
                    lambda y: {
                        "resource_id": x[id_field],
                        "type": type,
                        "tag_name": y["Key"],
                        "tag_value": y["Value"],
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


def get_vpcs(client):
    return flatten(transform_data(client.describe_vpcs()["Vpcs"], "VpcId", "vpc"))


def get_images(client):
    return flatten(
        transform_data(
            client.describe_images(Owners=["self"])["Images"], "ImageId", "image"
        )
    )


def get_subnets(client):
    return flatten(
        transform_data(client.describe_subnets()["Subnets"], "SubnetId", "subnet")
    )


def get_route_tables(client):
    return flatten(
        transform_data(
            client.describe_route_tables()["RouteTables"], "RouteTableId", "route_table"
        )
    )


def get_snapshots(client):
    return flatten(
        transform_data(
            client.describe_snapshots(OwnerIds=["self"])["Snapshots"],
            "SnapshotId",
            "snapshot",
        )
    )


def get_security_groups(client):
    return flatten(
        transform_data(
            client.describe_security_groups()["SecurityGroups"],
            "GroupId",
            "security_group",
        )
    )


def get_volumes(client):
    return flatten(
        transform_data(client.describe_volumes()["Volumes"], "VolumeId", "volume")
    )


def get_customer_gateways(client):
    return flatten(
        transform_data(
            client.describe_customer_gateways()["CustomerGateways"],
            "CustomerGatewayId",
            "customer_gateway",
        )
    )


def get_dhcp_options(client):
    return flatten(
        transform_data(
            client.describe_dhcp_options()["DhcpOptions"],
            "DhcpOptionsId",
            "dhcp_option",
        )
    )


def get_internet_gateways(client):
    return flatten(
        transform_data(
            client.describe_internet_gateways()["InternetGateways"],
            "InternetGatewayId",
            "internet_gateway",
        )
    )


def get_network_acls(client):
    return flatten(
        transform_data(
            client.describe_network_acls()["NetworkAcls"],
            "NetworkAclId",
            "network_acl",
        )
    )


def get_network_interfaces(client):
    return flatten(
        transform_data(
            client.describe_network_interfaces()["NetworkInterfaces"],
            "NetworkInterfaceId",
            "network_interface",
        )
    )


def get_reserved_instances(client):
    return flatten(
        transform_data(
            client.describe_reserved_instances()["ReservedInstances"],
            "ReservedInstancesId",
            "reserved_instance",
        )
    )


def get_spot_instances_requests(client):
    return flatten(
        transform_data(
            client.describe_spot_instance_requests()["SpotInstanceRequests"],
            "SpotInstanceRequestId",
            "spot_instances_requests",
        )
    )


def get_vpn_connections(client):
    return flatten(
        transform_data(
            client.describe_vpn_connections()["VpnConnections"],
            "VpnConnectionId",
            "vpn_connection",
        )
    )


def get_vpn_gateways(client):
    return flatten(
        transform_data(
            client.describe_vpn_gateways()["VpnGateways"],
            "VpnGatewayId",
            "vpn_gateway",
        )
    )


resource_mappings = {
    "vpc": get_vpcs,
    "image": get_images,
    "subnet": get_subnets,
    "route-table": get_route_tables,
    "snapshot": get_snapshots,
    "instance": get_instances,
    "security-group": get_security_groups,
    "volume": get_volumes,
    "customer-gateway": get_customer_gateways,
    "dhcp-options": get_dhcp_options,
    "internet-gateway": get_internet_gateways,
    "network-acl": get_network_acls,
    "network-interface": get_network_interfaces,
    "reserved-instances": get_reserved_instances,
    "spot-instances-request": get_spot_instances_requests,
    "vpn-connection": get_vpn_connections,
    "vpn-gateway": get_vpn_gateways,
}


def load_resources():
    global _resource_types
    global ec2

    # ec2_resource = boto3.resource("ec2", region_name=aws_region.get())
    ec2_client = boto3.client("ec2", region_name=aws_region.get())
    resource_types = json.load(open("./resource_types.json"))["resource_types"]

    resources = []
    for resource_type in resource_types:
        resources.extend(resource_mappings[resource_type](ec2_client))

    for resource in resources:
        print(resource)
    insert_records(resources)
    continue_prompt()
