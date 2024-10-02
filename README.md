# terraform-azure-kubernetes-elastic
Automation to build a Kubernetes cluster with Dashboard running ElasticSearch using Terraform in the cloud

## Requirements
- Ensure you have ansible >=2.15 installed
- Azure client installed locally
    -   https://learn.microsoft.com/en-us/cli/azure/install-azure-cli
- Be logged in as the service account to be used for the cluster
    - Generate a SSH key for this user:
        - ssh-keygen -t rsa -b 4096
- Ensure you have exported the following Azure environmental variables:
    - ARM_CLIENT_ID
    - ARM_CLIENT_SECRET
    - ARM_SUBSCRIPTION_ID
    - ARM_TENANT_ID
- Login to the Azure CLI
    - $ az login --use-device-code


## Running the automation
<pre>$ ansible-playbook automated_install.yml -i localhost,</pre>

You will be prompted for a service account username and password.  This is the credentials to login to the Windows Jump Box.  The name should match your currently logged in user that has an SSH key generated in ~/.ssh/id_rsa.

The automation will create the resource group resources necessary in Azure to run a 4 node Kubernetes cluster with Dashboard hosting various services offered.

## Accessing the nodes:
Kubernetes nodes will have IP addresses in the range of 10.0.0.4 to 10.0.0.8

Review the output of the automation for the IP address of the nodes.  By default you can SSH to the Kubernetes control plane node using:
<pre>
ssh localhost -p 2224   # for control plane node IP = 10.0.0.4
ssh localhost -p 2225   # for control plane node IP = 10.0.0.5
ssh localhost -p 2226   # for control plane node IP = 10.0.0.6
ssh localhost -p 2227   # for control plane node IP = 10.0.0.7
</pre>

The Jumpbox can be accessed via the Azure Portal
Need to get screenshots of this process

