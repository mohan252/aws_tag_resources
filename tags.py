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


def get_security_groups(client):
    return list(
        map(
            lambda x: {
                "resource-id": x["GroupId"],
                "type": "security_group",
                "tags": x.get("Tags", None),
            },
            client.describe_security_groups()["SecurityGroups"],
        )
    )


def get_volumes(client):
    return list(
        map(
            lambda x: {
                "resource-id": x["VolumeId"],
                "type": "volume",
                "tags": x.get("Tags", None),
            },
            client.describe_volumes()["Volumes"],
        )
    )


def get_customer_gateways(client):
    return list(
        map(
            lambda x: {
                "resource-id": x["CustomerGatewayId"],
                "type": "customer_gateway",
                "tags": x.get("Tags", None),
            },
            client.describe_customer_gateways()["CustomerGateways"],
        )
    )


def get_dhcp_options(client):
    return list(
        map(
            lambda x: {
                "resource-id": x["DhcpOptionsId"],
                "type": "dhcp_option",
                "tags": x.get("Tags", None),
            },
            client.describe_dhcp_options()["DhcpOptions"],
        )
    )


def get_internet_gateways(client):
    return list(
        map(
            lambda x: {
                "resource-id": x["InternetGatewayId"],
                "type": "internet_gateway",
                "tags": x.get("Tags", None),
            },
            client.describe_internet_gateways()["InternetGateways"],
        )
    )


def get_network_acls(client):
    return list(
        map(
            lambda x: {
                "resource-id": x["NetworkAclId"],
                "type": "network_acl",
                "tags": x.get("Tags", None),
            },
            client.describe_network_acls()["NetworkAcls"],
        )
    )


def get_network_interfaces(client):
    return list(
        map(
            lambda x: {
                "resource-id": x["NetworkInterfaceId"],
                "type": "network_interface",
                "tags": x.get("Tags", None),
            },
            client.describe_network_interfaces()["NetworkInterfaces"],
        )
    )


def get_reserved_instances(client):
    return list(
        map(
            lambda x: {
                "resource-id": x["ReservedInstancesId"],
                "type": "reserved_instance",
                "tags": x.get("Tags", None),
            },
            client.describe_reserved_instances()["ReservedInstances"],
        )
    )


def get_spot_instances_requests(client):
    return list(
        map(
            lambda x: {
                "resource-id": x["SpotInstanceRequestId"],
                "type": "spot_instances_requests",
                "tags": x.get("Tags", None),
            },
            client.describe_spot_instance_requests()["SpotInstanceRequests"],
        )
    )


def get_vpn_connections(client):
    return list(
        map(
            lambda x: {
                "resource-id": x["VpnConnectionId"],
                "type": "vpn_connection",
                "tags": x.get("Tags", None),
            },
            client.describe_vpn_connections()["VpnConnections"],
        )
    )


def get_vpn_gateways(client):
    return list(
        map(
            lambda x: {
                "resource-id": x["VpnGatewayId"],
                "type": "vpn_gateway",
                "tags": x.get("Tags", None),
            },
            client.describe_vpn_gateways()["VpnGateways"],
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
        resources.append(resource_mappings[resource_type](ec2_client))

    resources = [item for sublist in resources for item in sublist]
    for resource in resources:
        print(json.dumps(resource))
    continue_prompt()
