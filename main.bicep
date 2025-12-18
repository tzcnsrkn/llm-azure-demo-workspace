targetScope = 'subscription'

param rgName string = 'demo-rg-dsvm-llm'
param location string = 'polandcentral'

@description('The name of the Virtual Machine')
param vmName string = 'demo-dsvm-llm-01'

@description('Username for the Virtual Machine')
param adminUsername string = 'azuser'

@description('Type of authentication to use on the Virtual Machine. SSH Public Key is recommended.')
@allowed([
  'sshPublicKey'
  'password'
])
param authenticationType string = 'sshPublicKey'

@description('SSH Key or Password for the Virtual Machine. SSH key is recommended.')
@secure()
param adminPasswordOrKey string

@description('The size of the VM')
param vmSize string = 'Standard_NC4as_T4_v3'

// Create the Resource Group
resource newRG 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: rgName
  location: location
}

// Deploy all resources into the Resource Group
module vmResources 'dsvm_resources.bicep' = {
  name: 'vmResourcesDeployment'
  scope: newRG
  params: {
    location: location
    vmName: vmName
    adminUsername: adminUsername
    authenticationType: authenticationType
    adminPasswordOrKey: adminPasswordOrKey
    vmSize: vmSize
  }
}

output sshCommand string = vmResources.outputs.sshCommand
output marimoUrl string = vmResources.outputs.marimoUrl
output publicIpAddress string = vmResources.outputs.publicIpAddress
