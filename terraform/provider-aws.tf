provider "aws" {
  region = var.region

  default_tags {
    tags = {
      "environment" = var.environment
      "workspace"   = var.workspace_name
    }
  }
}
