variable "key_name" {
  description = "The key name to use for the instance"
  default     = "solar_data_cluster" # replace with your EC2 key pair name
}

variable "aws_region" {
  description = "The AWS region where resources will be created."
  default     = "eu-north-1" # Default to Paris, France region. Change if needed.
  type        = string
}
