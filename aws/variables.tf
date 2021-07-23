variable "aws_region" {default = "us-east-2"}
variable "aws_availability_zone" {default = "us-east-2a"}
variable "vpc_cidr_range" {default = "192.168.0.0/23"}
variable "external_subnet" {default = "192.168.0.0/24"}
variable "internal_subnet" {default = "192.168.1.0/24"}
variable "loopback_management" {default = "10.53.0.0/24"}
variable "t128_conductor_flavor" {default = "t2.large"}
variable "t128_router_flavor" {default = "c5.xlarge"}
variable "t128_ami" {}
variable "jumper_ami_name" {default = "*Amazon Linux*"}
variable "key_name" {}
variable "dc_mgmt_address" {default = "192.168.0.10"}
variable "dc_external_address" {default = "192.168.0.20"}
variable "dc_internal_address" {default = "192.168.1.20"}
variable "conductor_address" {default = "192.168.0.100"}
variable "jumper_internal_address" {default = "192.168.1.30"}
variable "jumper_flavor" {default = "t2.micro"}

# These are just included for output
variable "authority_name" {default = "L3NID_Authority"}
variable "routerName" {default = "l3niddc"}
variable "management_tenant" {default = "mgmt"}
variable "locationCoordinates" {default = "+33.7601772-084.3585778/"}
variable "location" {default = "Atlanta, GA"}
variable "interNodeSecurity" {default = "internal"}
variable "mgmt_pciAddress" {default = "0000:00:05.0"}
variable "mgmt_prefixLength" {default = "24"}
variable "mgmt_gateway" {default = "192.168.0.1"}
variable "wan_pciAddress" {default = "0000:00:06.0"}
variable "lan_pciAddress" {default = "0000:00:07.0"}
variable "lan_prefixLength" {default = "24"}
variable "interRouterSecurity" {default = "internal"}
variable "neighborhood_name" {default = "datacenter"}
variable "dns_servers" {default = ["1.1.1.1", "1.0.0.1"]}
variable "ntp_servers" {default = ["8.8.8.8"]}
variable "lan_ipAddress" {default = "192.168.1.1"}
variable "mgmt_ipAddress" {default = "172.25.1.15"}
variable "wan_gateway" {default = "172.25.3.1"}
variable "wan_ipAddress" {default = "172.25.3.20"}
variable "wan_prefixLength" {default = "24"}
variable "wan_floating_ip" {default = "172.25.3.20"}
