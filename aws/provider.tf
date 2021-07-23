provider "aws" {
  insecure   = true
  region     = var.aws_region
}

data "aws_ami" "jumper_ami" {
  owners = ["amazon"]
  most_recent = true
  filter {
    name = "name"
    values = [var.jumper_ami_name]
  }
}

data "template_file" "user_data" {
  template = file("cloud_init.tpl")
}
