resource "aws_network_interface" "jumper_internal" {
  subnet_id       = aws_subnet.internal.id
  private_ips     = [var.jumper_internal_address]
  security_groups = [aws_security_group.waypoint.id]

  tags = {
    Name          = "128T FSE POC Jumper internal"
  }
}

resource "aws_instance" "jumper" {
  ami               = data.aws_ami.jumper_ami.id
  instance_type     = var.jumper_flavor
  key_name          = var.key_name

  tags = {
    Name                 = "128T FSE POC Jumper"
  }

  root_block_device {
    delete_on_termination = true
  }

  network_interface {
    network_interface_id = aws_network_interface.jumper_internal.id
    device_index         = 0
  }
}

resource "aws_eip" "jumper" {
  vpc        = true

  tags = {
    Name          = "128T FSE POC Jumper"
  }
}

resource "aws_eip_association" "jumper" {
  allocation_id        = aws_eip.jumper.id
  network_interface_id = aws_network_interface.jumper_internal.id
}

