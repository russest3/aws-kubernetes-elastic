terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.location
}

########## VPC #################################
resource "aws_vpc" "vpc-0f362cc922d6593f4" {
  cidr_block = var.cidr
}

resource "aws_vpc_endpoint" "ec2" {
  vpc_id            = aws_vpc.vpc-0f362cc922d6593f4.id
  service_name      = "com.amazonaws.us-east-1.ec2"
  vpc_endpoint_type = "Interface"

  subnet_configuration {
    ipv4      = "172.31.0.10"
    subnet_id = aws_subnet.internal.id
  }

  tags     = {
    Name = "my-endpoint-01"
  }

  subnet_ids = [
    aws_subnet.internal.id
  ]
}

resource "aws_ec2_instance_connect_endpoint" "my-endpoint-connect" {
  subnet_id = aws_subnet.internal.id
}
##########################################################



############### NETWORK CONFIG############################
resource "aws_subnet" "internal" {
  vpc_id               = aws_vpc.vpc-0f362cc922d6593f4.id
  cidr_block           = var.cidr
  availability_zone    = var.az
}

resource "aws_network_interface" "c1-cp1" {
  subnet_id            = aws_subnet.internal.id
}
##############################################################



################ SSH Keys ############################################
resource "aws_key_pair" "svcaccount" {
  key_name             = "ubuntu@dlautobots01.wil.csc.local"
  public_key           = file("~/.ssh/id_rsa.pub")
}
######################################################################



################ EBS ###############################
resource "aws_ebs_volume" "c1-cp1" {
  availability_zone    = var.az
  size                 = 4
}
####################################################




############### CONTROL PLANE NODE #####################
resource "aws_instance" "c1-cp1" {
  ami                         = var.ami
  instance_type               = var.instance_type
  user_data                   = filebase64("script.tftpl")
  key_name                    = aws_key_pair.svcaccount.key_name
  network_interface {
    network_interface_id = aws_network_interface.c1-cp1.id
    device_index         = 0
  }
  tags     = {
    Name = "test-c1-cp1"
  }
}
#######################################