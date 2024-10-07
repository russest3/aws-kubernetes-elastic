variable "location" {
  type        = string
  description = "The AWS region to use"
  default     = "us-east-1"
}

variable "cidr" {
  type    = string
  default = "172.31.0.0/20"
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
  default = "ami-005fc0f236362e99f"
}