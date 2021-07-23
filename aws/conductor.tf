data "template_file" "conductor" {
  template = file("conductor_cloud_init.tpl")

  vars = {
    conductor_ip = aws_eip.conductor.public_ip
    authority_name = var.authority_name
    dns_servers = jsonencode(var.dns_servers)
    interNodeSecurity = var.interNodeSecurity
    interRouterSecurity = var.interRouterSecurity
    lan_ipAddress = var.dc_internal_address
    lan_pciAddress = var.lan_pciAddress
    lan_prefixLength = var.lan_prefixLength
    location = var.location
    locationCoordinates = var.locationCoordinates
    mgmt_gateway = var.mgmt_gateway
    mgmt_ipAddress = var.dc_mgmt_address
    mgmt_pciAddress = var.mgmt_pciAddress
    mgmt_prefixLength = var.mgmt_prefixLength
    neighborhood_name = var.neighborhood_name
    ntp_servers = jsonencode(var.ntp_servers)
    routerName = var.routerName
    wan_gateway = var.mgmt_gateway
    wan_ipAddress = var.dc_external_address
    wan_pciAddress = var.wan_pciAddress
    wan_prefixLength = var.wan_prefixLength
    management_tenant = var.management_tenant
    wan_floating_ip = aws_eip.dc_external.public_ip
  }
}

data "template_cloudinit_config" "conductor" {
  gzip = false
  base64_encode = false

  part {
    content_type = "text/cloud-config"
    content      = data.template_file.conductor.rendered
  }
}

resource "aws_network_interface" "conductor_external" {
  subnet_id       = aws_subnet.external.id
  private_ips     = [var.conductor_address]
  security_groups = [aws_security_group.conductor_mgmt.id]

  tags = {
    Name          = "128T FSE POC Conductor external"
  }
}

resource "aws_instance" "conductor" {
  ami               = var.t128_ami
  instance_type     = var.t128_conductor_flavor
  key_name          = var.key_name
  user_data         = data.template_cloudinit_config.conductor.rendered

  tags = {
    Name                 = "128T FSE POC Conductor"
    node-name            = "conductor"
    router-name          = "conductor"
    disable-interactive  = "true"
  }

  root_block_device {
    delete_on_termination = true
    volume_size = "60"
  }

  network_interface {
    network_interface_id = aws_network_interface.conductor_external.id
    device_index         = 0
  }
}

resource "aws_eip" "conductor" {
  vpc        = true

  tags = {
    Name          = "128T FSE POC Conductor"
  }
}

resource "aws_eip_association" "conductor" {
  allocation_id        = aws_eip.conductor.id
  network_interface_id = aws_network_interface.conductor_external.id
}
