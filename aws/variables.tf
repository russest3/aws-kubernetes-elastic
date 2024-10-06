variable "location" {
  type        = string
  description = "The AWS region to use"
  default     = "us-east-1"
}

variable "cidr" {
  type    = string
  default = "10.0.0.0/16"
}

variable "az" {
  type    = string
  default = "us-east-1e"
}

variable "instance_type" {
  type    = string
  # default = "t3.small"
  default    = "t2.micro"
}

variable "ami" {
  type    = string
  default = "ami-0866a3c8686eaeeba"
}