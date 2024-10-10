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
resource "aws_default_vpc" "test" {
  tags = {
    Name = "Default VPC"
  }
}

resource "aws_vpc_endpoint" "ec2" {
  vpc_id            = aws_default_vpc.test.id
  service_name      = "com.amazonaws.us-east-1.ec2"
  vpc_endpoint_type = "Interface"

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
  vpc_id               = aws_default_vpc.test.id
  cidr_block           = "172.31.1.0/24"
  tags = {
    Name = "internal"
  }
}

resource "aws_subnet" "public" {
  depends_on = [ aws_default_vpc.test ]
  vpc_id               = aws_default_vpc.test.id
  cidr_block           = "172.31.2.0/24"
  map_public_ip_on_launch = true
  tags = {
    Name = "public"
  }
}

resource "aws_network_interface" "c1-cp1" {
  subnet_id            = aws_subnet.internal.id
}

resource "aws_network_interface" "c1-node1" {
  subnet_id            = aws_subnet.internal.id
}

resource "aws_network_interface" "c1-node2" {
  subnet_id            = aws_subnet.internal.id
}

resource "aws_network_interface" "c1-node3" {
  subnet_id            = aws_subnet.internal.id
}

resource "aws_eip" "main" {
  domain   = "vpc"
  depends_on = [ aws_route_table_association.public-ig ]
  tags = {
    Name = "main"
  }
}

resource "aws_internet_gateway" "main" {
  depends_on = [ aws_default_vpc.test,
                 aws_subnet.internal,
                 aws_subnet.public
   ]
  tags = {
    Name = "main"
  }
}

resource "aws_internet_gateway_attachment" "main" {
  internet_gateway_id = aws_internet_gateway.main.id
  vpc_id              = aws_default_vpc.test.id
}

resource "aws_route_table" "public-ig" {
  vpc_id               = aws_default_vpc.test.id
  depends_on = [ aws_internet_gateway.main,
                 aws_default_vpc.test
  ]
  route {
    cidr_block             = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "main"
  }
}

resource "aws_route_table_association" "public-ig" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public-ig.id
  depends_on = [ aws_default_vpc.test,
                 aws_subnet.internal,
                 aws_subnet.public,
                 aws_route_table.public-ig
   ]
}

resource "aws_route_table" "private" {
  vpc_id               = aws_default_vpc.test.id
  depends_on = [ aws_nat_gateway.gw ]
  route {
    cidr_block             = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.gw.id
  }
  tags = {
    Name = "main"
  }
}

resource "aws_route_table_association" "internal" {
  subnet_id      = aws_subnet.internal.id
  route_table_id = aws_route_table.private.id
  depends_on = [ aws_route_table.private ]
}

resource "aws_nat_gateway" "gw" {
  allocation_id = aws_eip.main.id
  subnet_id     = aws_subnet.public.id
  tags = {
    Name = "gw"
  }
  depends_on = [ aws_eip.main ]
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

resource "aws_ebs_volume" "c1-node1" {
  availability_zone    = var.az
  size                 = 4
}

resource "aws_ebs_volume" "c1-node2" {
  availability_zone    = var.az
  size                 = 4
}

resource "aws_ebs_volume" "c1-node3" {
  availability_zone    = var.az
  size                 = 4
}
####################################################




############### CONTROL PLANE NODE #####################
resource "aws_instance" "c1-cp1" {
  ami                         = var.ami
  instance_type               = var.instance_type
  user_data                   = filebase64("c1-cp1.tftpl")
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




###################### WORKER NODES ########################
resource "aws_instance" "c1-node1" {
  ami                         = var.ami
  instance_type               = var.instance_type
  user_data                   = filebase64("c1-node1.tftpl")
  key_name                    = aws_key_pair.svcaccount.key_name
  network_interface {
    network_interface_id = aws_network_interface.c1-node1.id
    device_index         = 0
  }
  tags     = {
    Name = "test-c1-node1"
  }
}

resource "aws_instance" "c1-node2" {
  ami                         = var.ami
  instance_type               = var.instance_type
  user_data                   = filebase64("c1-node2.tftpl")
  key_name                    = aws_key_pair.svcaccount.key_name
  network_interface {
    network_interface_id = aws_network_interface.c1-node2.id
    device_index         = 0
  }
  tags     = {
    Name = "test-c1-node2"
  }
}

resource "aws_instance" "c1-node3" {
  ami                         = var.ami
  instance_type               = var.instance_type
  user_data                   = filebase64("c1-node3.tftpl")
  key_name                    = aws_key_pair.svcaccount.key_name
  network_interface {
    network_interface_id = aws_network_interface.c1-node3.id
    device_index         = 0
  }
  tags     = {
    Name = "test-c1-node3"
  }
}
############################################################