terraform {
  cloud {
    organization = var.organization_name

    workspaces {
      name = var.workspace_name
    }
  }
}
