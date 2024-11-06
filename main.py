import requests
import os, json
import tarfile
import argparse
from variables import organzation,workspace, TerraformConfig

parser = argparse.ArgumentParser(
    prog        ='HCP Terraform API driven workflow',
    description = "Triggers runs in HCP Terraform"
)
parser.add_argument('-o', '--organization', default=organzation, help="Specify your organization name")
parser.add_argument('-w', '--workspace', default=workspace, help="Specify your HCP Terraform API-driven workspace" )
parser.add_argument('-d', '--directory', default=TerraformConfig, help="Specify the location of your Terraform configuration files" )
args = parser.parse_args()
# organzation = "marin-tests"
# workspace = "api-driven-python"
organzation = args.organization
workspace = args.workspace
TerraformConfig = args.directory
CONFIG_ARCHIVE_NAME = "configuration.tar.gz"
### Get API token

def getToken():
    try:
        TOKEN=os.environ["TOKEN"]
        print("Using exsting token")
    except KeyError:
        print("Token not set")
        print("Checking terraform credentials file")
        try:
            token_file = open(f"{os.path.expanduser("~")}/.terraform.d/credentials.tfrc.json", "r")
            TOKEN= json.load(token_file)["credentials"]["app.terraform.io"]["token"]
            token_file.close()
        except FileNotFoundError:
            TOKEN = input("File not found please provide valid token=")
        else:
            print("Using token from local terraform credential file")
            return TOKEN
    except:
        print("some other error")
        return -1
    else: 
        print("Env variable TOKEN will be used")
        return TOKEN

### Creating archive with Terraform configuration files located in sub dir TerraformConfig

def configFileCreate():
    if os.getcwd != os.path.dirname(__file__):
        os.chdir(os.path.dirname(__file__))
    ConfigurationFiles = tarfile.open(name=CONFIG_ARCHIVE_NAME,mode="x:gz")
    os.chdir(f"{os.path.dirname(__file__)}/{TerraformConfig}") #Need to change current dir as its going to add the whole TerraformConfig dir to the archive
    # Walk through all files in sub dir and adding the terraform configuration only
    # Not going to work in case there are local terraform modules 
    for file in os.listdir():
        if file.split(".")[-1] == "tf":
            ConfigurationFiles.add(file)
    ConfigurationFiles.close()

def configFileDelete():
    if os.getcwd != os.path.dirname(__file__):
        os.chdir(os.path.dirname(__file__))
    os.remove(path=CONFIG_ARCHIVE_NAME)

### Checking if the tar.gz confguration archive exists and choose if the existsing will be used.
def configFileSelect():
    try:
        configFileCreate()
    except FileExistsError:
        print("The configuration file already exists.")
        print("Removing the file")
        configFileDelete()
        configFileCreate()


# Upload the configuration version
# https://developer.hashicorp.com/terraform/cloud-docs/api-docs/run

def configVersionCreate(TOKEN, organzation, workspace):
    # Get the workspace ID
    HCP_headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/vnd.api+json"}
    URL_get_ws = f"https://app.terraform.io/api/v2/organizations/{organzation}/workspaces/{workspace}"
    result = requests.get(headers=HCP_headers, url=URL_get_ws)
    result.raise_for_status()
    workspace_id = result.json()["data"]["id"]

    # Create a Configuration Version
    URL_cv_url = f"https://app.terraform.io/api/v2/workspaces/{workspace_id}/configuration-versions"
    os.chdir(os.path.dirname(__file__))
    payload_file = open("create_cv.json", "r")
    payload = json.load(payload_file)
    payload_file.close()
    create_cv = requests.post(headers=HCP_headers, json=payload, url=URL_cv_url)
    create_cv.raise_for_status()
    filesUploadURL= create_cv.json()["data"]["attributes"]["upload-url"]
    
    # Upload Configuration Files
    configuration_file = open(CONFIG_ARCHIVE_NAME, "rb")
    configuration_binary = configuration_file.read()
    configuration_file.close()
    requests.put(headers={"Content-Type": "application/octet-stream"}, data=configuration_binary, url=filesUploadURL)
if __name__ == "__main__":
    configFileSelect() #This function can be replaced with configFileCreate() if this file is deleted after each call.
    configVersionCreate(getToken(), organzation, workspace)
    configFileDelete()