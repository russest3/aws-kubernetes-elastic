from aws_cdk import (
    NestedStack,
)
from constructs import Construct

class VPNStack(NestedStack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create VPC
        my_vpc = ec2.Vpc(
            self, "KubernetesVpc",
            nat_gateways=0
        )

        keyPair = ec2.KeyPair.from_key_pair_attributes(self, "KeyPair",
            key_pair_name="KubernetesKeyPair",
            type=ec2.KeyPairType.RSA
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
                                                      ignore_public_acls=False,
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

        # Create a Client VPN endpoint
        # Need to add a target network association
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
            description="Client VPN endpoint for secure remote access",
            split_tunnel=True,
            vpc_id=my_vpc.vpc_id,
            dns_servers=["8.8.8.8", "8.8.4.4"]
        )

        # Create authorization rule
        # client_vpn_endpoint.add_authorization_rule("Rule",
        #     cidr="10.0.10.0/32",
        #     group_id="group-id"
        # )