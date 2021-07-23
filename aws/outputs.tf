output "jumper-ip" {
  value = aws_eip.jumper.public_ip
}

output "conductor_address" {
  value = aws_eip.conductor.public_ip
}

output "dc-ip" {
  value = aws_eip.dc_mgmt.public_ip
}
