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
resource "aws_vpc" "test" {
  cidr_block = var.cidr
}
##########################################################



############### NETWORK CONFIG############################
resource "aws_subnet" "internal" {
  vpc_id               = aws_vpc.test.id
  cidr_block           = var.cidr
  availability_zone    = var.az
}

resource "aws_network_interface" "c1-cp1" {
  subnet_id            = aws_subnet.internal.id
}
##############################################################



################ SSH Keys ############################################
resource "aws_key_pair" "svcaccount" {
  key_name             = "svcaccount-key"
  public_key           = file("~/.ssh/id_rsa.pub")
}
######################################################################



################ EBS ###############################
resource "aws_ebs_volume" "c1-cp1" {
  availability_zone    = var.az
  size                 = 4
}
####################################################




############### IAM ##################################################
resource "aws_iam_user" "ec2admin" {
  name = "ec2"
  path = "/system/"
}

resource "aws_iam_role_policy_attachment" "ec2admin" {
  role       = aws_iam_role.ec2admin.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2FullAccess"
}

resource "aws_iam_instance_profile" "ec2admin" {
  name = "ec2admin"
  role = aws_iam_role.ec2admin.name
}

resource "aws_iam_role" "ec2admin" {
  name       =    "ec2admin"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      },
    ]
  })
}

resource "aws_iam_access_key" "ec2admin" {
  user    = aws_iam_user.ec2admin.name
}

output "secret" {
  value = aws_iam_access_key.ec2admin.encrypted_secret
}
############################################################




############### CONTROL PLANE NODE #####################
resource "aws_instance" "c1-cp1" {
  ami                         = var.ami
  instance_type               = var.instance_type
  user_data                   = filebase64("script.tftpl")
  key_name                    = aws_key_pair.svcaccount.key_name
  iam_instance_profile        = aws_iam_instance_profile.ec2admin.name
  network_interface {
    network_interface_id = aws_network_interface.c1-cp1.id
    device_index         = 0
  }
  tags     = {
    Name = "test-c1-cp1"
  }
}
#######################################