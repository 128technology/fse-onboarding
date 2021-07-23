resource "aws_vpc" "t128_vpc" {
  cidr_block = var.vpc_cidr_range

  tags = {
    Name = "128T FSE POC VPC"
  }
}

resource "aws_internet_gateway" "vpc_gw" {
  vpc_id = aws_vpc.t128_vpc.id
  tags = {
    Name = "128T FSE POC VPC GW"
  }
}

resource "aws_route_table" "external_rt" {
  vpc_id = aws_vpc.t128_vpc.id
  tags = {
    Name = "128T FSE POC External Route Table"
  }
}

resource "aws_route" "external_default" {
  route_table_id = aws_route_table.external_rt.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id = aws_internet_gateway.vpc_gw.id
}

resource "aws_subnet" "external" {
  vpc_id = aws_vpc.t128_vpc.id
  availability_zone = var.aws_availability_zone
  cidr_block = var.external_subnet
  tags = {
    Name = "128T FSE POC External Subnet"
  }
}

resource "aws_route_table_association" "external" {
  subnet_id = aws_subnet.external.id
  route_table_id = aws_route_table.external_rt.id
}

resource "aws_route_table" "internal_rt" {
  vpc_id = aws_vpc.t128_vpc.id
  tags = {
    Name = "128T FSE POC Internal Route Table"
  }
}

resource "aws_route" "internal_default" {
  route_table_id = aws_route_table.internal_rt.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id = aws_internet_gateway.vpc_gw.id
}

resource "aws_route" "loopback_mgmt" {
  route_table_id = aws_route_table.internal_rt.id
  destination_cidr_block = var.loopback_management
  network_interface_id = aws_network_interface.dc_internal.id
}

resource "aws_subnet" "internal" {
  vpc_id = aws_vpc.t128_vpc.id
  availability_zone = var.aws_availability_zone
  cidr_block = var.internal_subnet
  tags = {
    Name = "128T FSE POC External Subnet"
  }
}

resource "aws_route_table_association" "internal" {
  subnet_id = aws_subnet.internal.id
  route_table_id = aws_route_table.internal_rt.id
}

resource "aws_security_group" "waypoint" {
  name = "T128 FSE POC SG: waypoint_allow_all"
  vpc_id = aws_vpc.t128_vpc.id

  tags = {
    Name = "128T FSE POC SG: waypoint_allow_all"
  }

  ingress {
    from_port = 0
    to_port   = 0
    protocol  = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port = 0
    to_port   = 0
    protocol  = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "router_mgmt" {
  name = "router_mgmt"
  vpc_id = aws_vpc.t128_vpc.id

  tags = {
    Name = "128T FSE POC SG: router management"
  }

  ingress {
    from_port = 22
    to_port   = 22
    protocol  = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port = 443
    to_port   = 443
    protocol  = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port = 0
    to_port   = 0
    protocol  = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "conductor_mgmt" {
  name = "conductor_mgmt"
  vpc_id = aws_vpc.t128_vpc.id

  tags = {
    Name = "128T FSE POC SG: conductor management"
  }

  ingress {
    from_port = 22
    to_port   = 22
    protocol  = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port = 443
    to_port   = 443
    protocol  = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port = 930
    to_port   = 930
    protocol  = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port = 4505
    to_port   = 4506
    protocol  = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port = 3006
    to_port   = 3006
    protocol  = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port = 5000
    to_port   = 5000
    protocol  = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port = 0
    to_port   = 0
    protocol  = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "jumper_mgmt" {
  name = "server_mgmt"
  vpc_id = aws_vpc.t128_vpc.id

  tags = {
    Name = "128T FSE POC SG: jumper management"
  }

  ingress {
    from_port = 22
    to_port   = 22
    protocol  = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
