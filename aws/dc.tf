data "template_file" "dc" {
  template = file("dc_cloud_init.tpl")

  vars = {
    conductor_address = var.conductor_address
  }
}

data "template_cloudinit_config" "dc" {
  gzip = false
  base64_encode = false

  part {
    content_type = "text/cloud-config"
    content      = data.template_file.dc.rendered
  }
}

resource "aws_network_interface" "dc_mgmt" {
  subnet_id       = aws_subnet.external.id
  private_ips     = [var.dc_mgmt_address]
  security_groups = [aws_security_group.router_mgmt.id]

  tags = {
    Name          = "128T FSE POC Router mgmt"
  }
}

resource "aws_network_interface" "dc_external" {
  subnet_id       = aws_subnet.external.id
  private_ips     = [var.dc_external_address]
  security_groups = [aws_security_group.waypoint.id]
  source_dest_check = false

  tags = {
    Name          = "128T FSE POC DC external"
  }
}

resource "aws_network_interface" "dc_internal" {
  subnet_id       = aws_subnet.internal.id
  private_ips     = [var.dc_internal_address]
  security_groups = [aws_security_group.waypoint.id]
  source_dest_check = false

  tags = {
    Name          = "128T FSE POC DC internal"
  }
}

resource "aws_instance" "dc" {
  ami               = var.t128_ami
  instance_type     = var.t128_router_flavor
  key_name          = var.key_name
  user_data         = data.template_cloudinit_config.dc.rendered

  tags = {
    Name                 = "128T FSE POC DC Router"
  }

  root_block_device {
    delete_on_termination = true
    volume_size = "60"
  }

  network_interface {
    network_interface_id = aws_network_interface.dc_mgmt.id
    device_index         = 0
  }

  network_interface {
    network_interface_id = aws_network_interface.dc_external.id
    device_index         = 1
  }

  network_interface {
    network_interface_id = aws_network_interface.dc_internal.id
    device_index         = 2
  }
}

resource "aws_eip" "dc_mgmt" {
  vpc        = true

  tags = {
    Name          = "128T FSE POC DC Router Mgmt"
  }
}

resource "aws_eip_association" "dc_mgmt" {
  allocation_id        = aws_eip.dc_mgmt.id
  network_interface_id = aws_network_interface.dc_mgmt.id
}

resource "aws_eip" "dc_external" {
  vpc        = true

  tags = {
    Name          = "128T FSE POC DC Router External"
  }
}

resource "aws_eip_association" "dc_external" {
  allocation_id        = aws_eip.dc_external.id
  network_interface_id = aws_network_interface.dc_external.id
}
