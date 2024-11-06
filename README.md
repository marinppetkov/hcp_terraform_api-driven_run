# Automate HCP Terraform API-driven Run Workflow
This repository contains a Python script to automate and manage HCP Terraform runs using the [Terraform API](https://developer.hashicorp.com/terraform/cloud-docs/api-docs/run).
## Usage
```bash
usage: HCP Terraform API driven workflow [-h] [-o ORGANIZATION] [-w WORKSPACE]

Triggers runs in HCP Terraform

options:
  -h, --help                                   show this help message and exit
  -o ORGANIZATION, --organization ORGANIZATION Specify your organization name
  -w WORKSPACE,    --workspace WORKSPACE       Specify your HCP Terraform API-driven workspace
```
Environment variable
- **TOKEN** - HCP Terraform [API token](https://developer.hashicorp.com/terraform/cloud-docs/users-teams-organizations/api-tokens)
    - If this is missing, the script will attempt to obtain an API token from  [credentials.tfrc.json](credentials.tfrc.json) or will prompt the user to enter one.

### Optional Configuration
The script includes a `variables.py` file where you can set the HCP Terraform organization and workspace. If these are defined here, you don’t need to specify them each time you run the script, simplifying repeated use.
