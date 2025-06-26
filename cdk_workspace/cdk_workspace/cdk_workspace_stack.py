from aws_cdk import (
    # Duration,
    Stack,
    CfnOutput,
    aws_ec2 as ec2
    # aws_sqs as sqs,
)
from constructs import Construct

class CdkWorkspaceStack(Stack):

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

        # Create control plane node EC2 instance
        c1_cp1 = ec2.Instance(
            self, "c1-cp1",
            instance_type=ec2.InstanceType.of(instance_class=ec2.InstanceClass.T2,
            instance_size=ec2.InstanceSize.MICRO),
            machine_image=ec2.MachineImage.generic_linux({
                "us-east-2": "ami-0d1b5a8c13042c939"
            }),
            vpc=my_vpc,
            key_pair=keyPair,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            user_data_causes_replacement=True
        )

        # Attaching an Elastic IP to keep the DNS name on updates
        ec2.CfnEIP(self, "ElasticIP",
            instance_id=c1_cp1.instance_id
        )

        # Installing packages at instance launch
        c1_cp1.add_user_data("sudo add-apt-repository -y ppa:deadsnakes/ppa",
            "sudo apt install -y python3.10 containerd apt-transport-https ca-certificates curl gpg",
            "sudo rm -f /usr/bin/python3",
            "sudo ln -s /usr/bin/python3.10 /usr/bin/python3",
            "sudo ln -s /usr/bin/python3.10 /usr/bin/python",
            "sudo apt update -y",
            "sudo apt upgrade -y",
            "sudo sed -i 's/^#\s*PasswordAuthentication.*$/PasswordAuthentication yes/' /etc/ssh/sshd_config",
            "sudo sed -i 's/^KbdInteractiveAuthentication.*$/#KbdInteractiveAuthentication no/' /etc/ssh/sshd_config",
            "sudo systemctl restart sshd",
            "sudo printf 'overlay\nbr_netfilter' > /etc/modules-load.d/k8s.conf",
            "sudo modprobe overlay",
            "sudo modprobe br_netfilter",
            "echo 'net.bridge.bridge-nf-call-iptables=1' | sudo tee -a /etc/sysctl.conf",
            "echo 'net.bridge.bridge-nf-call-ip6tables=1' | sudo tee -a /etc/sysctl.conf",
            "sudo sed -i 's/^#net.ipv4.ip_forward.*$/net.ipv4.ip_forward=1/' /etc/sysctl.conf",
            "sudo sysctl -p",
            "sudo mkdir /etc/containerd",
            "sudo containerd config default | tee /etc/containerd/config.toml",
            "sudo sed -i 's/            SystemdCgroup = false/            SystemdCgroup = true/' /etc/containerd/config.toml",
            "sudo systemctl restart containerd",            
            )
        
        CfnOutput(self, "c1_cp1", value=c1_cp1.instance_public_dns_name)

        # Allowing traffic to the c1_cp1 server
        c1_cp1.connections.allow_from_any_ipv4(ec2.Port.tcp(80), "Allow HTTP traffic to c1-cp1")
        c1_cp1.connections.allow_from_any_ipv4(ec2.Port.tcp(22), "Allow SSH traffic to c1-cp1")
        c1_cp1.connections.allow_from_any_ipv4(ec2.Port.tcp(443), "Allow HTTPS traffic to c1-cp1")

        # Create worker nodes
        for i in str(1),str(2),str(3):

            node_name = "c1-node" + i

            c1_node = ec2.Instance(
                self, node_name,
                instance_type=ec2.InstanceType.of(instance_class=ec2.InstanceClass.T2,
                instance_size=ec2.InstanceSize.MICRO),
                machine_image=ec2.MachineImage.generic_linux({
                    "us-east-2": "ami-0d1b5a8c13042c939",
                }),
                vpc=my_vpc,
                key_pair=keyPair,
                vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
                user_data_causes_replacement=True,
            )

            # Installing packages at instance launch
            c1_node.add_user_data("sudo add-apt-repository -y ppa:deadsnakes/ppa",
                "sudo apt install -y python3.10 containerd apt-transport-https ca-certificates curl gpg",
                "sudo rm -f /usr/bin/python3",
                "sudo ln -s /usr/bin/python3.10 /usr/bin/python3",
                "sudo ln -s /usr/bin/python3.10 /usr/bin/python",
                "sudo apt update -y",
                "sudo apt upgrade -y",
                "sudo sed -i 's/^#\s*PasswordAuthentication.*$/PasswordAuthentication yes/' /etc/ssh/sshd_config",
                "sudo sed -i 's/^KbdInteractiveAuthentication.*$/#KbdInteractiveAuthentication no/' /etc/ssh/sshd_config",
                "sudo systemctl restart sshd",
                "sudo printf 'overlay\nbr_netfilter' > /etc/modules-load.d/k8s.conf",
                "sudo modprobe overlay",
                "sudo modprobe br_netfilter",
                "echo 'net.bridge.bridge-nf-call-iptables=1' | sudo tee -a /etc/sysctl.conf",
                "echo 'net.bridge.bridge-nf-call-ip6tables=1' | sudo tee -a /etc/sysctl.conf",
                "sudo sed -i 's/^#net.ipv4.ip_forward.*$/net.ipv4.ip_forward=1/' /etc/sysctl.conf",
                "sudo sysctl -p",
                "sudo mkdir /etc/containerd",
                "sudo containerd config default | tee /etc/containerd/config.toml",
                "sudo sed -i 's/            SystemdCgroup = false/            SystemdCgroup = true/' /etc/containerd/config.toml",
                "sudo systemctl restart containerd",            
                )

            c1_node.connections.allow_from_any_ipv4(ec2.Port.tcp(22), "Allow SSH traffic to worker node")
        
        print ("c1-cp1 IP Address:", CfnOutput(self, "c1-cp1-ip-address", value=c1_cp1.instance_public_ip))
        print ("c1-node1 IP Address:", CfnOutput(self, "c1-node1-ip-address", value=c1_node1.instance_public_ip))
        print ("c1-node2 IP Address:", CfnOutput(self, "c1-node2-ip-address", value=c1_node2.instance_public_ip))
        print ("c1-node3 IP Address:", CfnOutput(self, "c1-node3-ip-address", value=c1_node3.instance_public_ip))
