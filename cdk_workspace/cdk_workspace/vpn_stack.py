from aws_cdk import (
    NestedStack,
    RemovalPolicy,
    CfnOutput,
    aws_ec2 as ec2,
    aws_s3 as s3,
    aws_route53 as route53,
    aws_route53_targets as targets,
)
from constructs import Construct

class VPNStack(NestedStack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create VPC
        self.my_vpc = ec2.Vpc(
            self, "KubernetesVpc",
            nat_gateways=0,
            max_azs=1,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="PublicSubnet",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                ),
                # ec2.SubnetConfiguration(
                #     name="PrivateWithEgressSubnet",
                #     subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                #     cidr_mask=24
                # ),
                ec2.SubnetConfiguration(
                    name="PrivateVPNsubnet",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24
                )
            ]
        )

        domain_name = "russest3-example.local"

        # Create an S3 bucket for static website hosting
        website_bucket = s3.Bucket(self, "WebsiteBucket",
            bucket_name="russest3-example.local",
            public_read_access=True,
            website_index_document="index.html",
            removal_policy=RemovalPolicy.DESTROY,
            block_public_access=s3.BlockPublicAccess(block_public_acls=False,
                                                      block_public_policy=False,
                                                      ignore_public_acls=True,
                                                      restrict_public_buckets=False)
        )

        # Create a Route 53 Hosted Zone
        hosted_zone = route53.HostedZone(self, "ExampleComHostedZone",
            zone_name=domain_name
        )

        # Create an A record to point to the S3 bucket website endpoint
        route53.ARecord(self, "AliasRecord",
            zone=hosted_zone,
            target=route53.RecordTarget.from_alias(targets.BucketWebsiteTarget(website_bucket)),
            region="us-east-2"
        )

        # Retrieve certificate arns
        server_cert_arn = "arn:aws:acm:us-east-2:014420964653:certificate/abcd03cd-c42f-4538-9acd-a06d4a5fe529"
        client_cert_arn = "arn:aws:acm:us-east-2:014420964653:certificate/5d1558f4-e843-4ea0-b9c2-9682d59a1d9f"

        # Create a security group for the VPN endpoint
        vpn_endpoint_sg = ec2.SecurityGroup(
            self, "VpnEndpointSG",
            vpc=self.my_vpc,
            security_group_name="VpnEndpointSG",
            description="Allow https for vpn",
            allow_all_outbound=True
        )

        # Add an ingress rule to allow SSH traffic from anywhere
        vpn_endpoint_sg.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(22),
            description="Allow SSH traffic"
        )

        # Create a Client VPN endpoint
        client_vpn_endpoint = ec2.CfnClientVpnEndpoint(self, "ClientVpnEndpoint",
            authentication_options=[{
                "type": "certificate-authentication",
                "mutualAuthentication": {
                    "clientRootCertificateChainArn": client_cert_arn
                }
            }],            
            client_cidr_block="10.100.0.0/22",
            connection_log_options={
                "enabled": False
            },
            server_certificate_arn=server_cert_arn,
            vpn_port=443,
            transport_protocol="tcp",
            self_service_portal="enabled",
            security_group_ids = [ vpn_endpoint_sg.security_group_id ],
            description="Client VPN endpoint for secure remote access",
            split_tunnel=True,
            vpc_id=self.my_vpc.vpc_id,
            dns_servers=["8.8.8.8", "8.8.4.4"],
        )

        public_subnets = self.my_vpc.select_subnets(subnet_type=ec2.SubnetType.PUBLIC)

        cfn_client_vpn_target_network_association = ec2.CfnClientVpnTargetNetworkAssociation(self, "MyCfnClientVpnTargetNetworkAssociation",
            client_vpn_endpoint_id=client_vpn_endpoint.ref,
            subnet_id=public_subnets.subnet_ids[0]
        )

        # Create authorization rule
        cfn_client_vpn_authorization_rule = ec2.CfnClientVpnAuthorizationRule(self, "MyCfnClientVPNAuthorizationRule",
            client_vpn_endpoint_id=client_vpn_endpoint.ref,
            authorize_all_groups=True,
            target_network_cidr=self.my_vpc.vpc_cidr_block
        )

        # Output the VPN endpoint ID
        CfnOutput(self, "ClientVpnEndpointId",
            value=client_vpn_endpoint.ref,
            description="Client VPN Endpoint ID"
        )

        CfnOutput(self, "ClientVpnConfigFile",
            value=f"aws ec2 export-client-vpn-client-configuration --client-vpn-endpoint-id {client_vpn_endpoint.ref} --output text > client-config.ovpn",
            description="Command to download VPN configuration"
        )

       # Output the VPC ID
        CfnOutput(
            self, "VpcId",
            value=self.my_vpc.vpc_id,
            description="ID of the VPC with Client VPN Gateway Endpoint"
        )