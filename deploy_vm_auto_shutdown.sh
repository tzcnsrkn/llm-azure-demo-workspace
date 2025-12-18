#!/bin/bash
set -e  # Exit immediately if any command fails

# ==============================================================================
# Azure Logic App Automation: Auto-Shutdown VM
# ==============================================================================
# Creates a Consumption Logic App that triggers daily at 18:00
# to deallocate a given Virtual Machine. Uses Managed Identity for secure
# authentication.
# ==============================================================================

# --- Parameters ---
RG_NAME="<rg_name>"
VM_NAME="<vm_name>"
LOGIC_APP_NAME="logic-app-auto-shutdown-${VM_NAME}"
LOCATION="<region_name>"
SUBSCRIPTION_ID=$(az account show --query id -o tsv)

# --- Colors for Output ---
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting Auto-Shutdown Logic App setup...${NC}"

# 1. Create Resource Group (if not exists)
echo -e "${BLUE}Checking Resource Group: ${RG_NAME}...${NC}"
az group create --name "$RG_NAME" --location "$LOCATION" --output none

# 2. Create the Logic App with minimal inline definition
echo -e "${BLUE}Creating Logic App: ${LOGIC_APP_NAME}...${NC}"
MSYS_NO_PATHCONV=1 az logic workflow create \
  --resource-group "$RG_NAME" \
  --location "$LOCATION" \
  --name "$LOGIC_APP_NAME" \
  --definition '{"definition": {"$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#", "contentVersion": "1.0.0.0", "triggers": {}, "actions": {}}}' \
  --output none

if [ $? -ne 0 ]; then
    echo "Error: Failed to create Logic App. Exiting."
    exit 1
fi

# 3. Enable SAMI
echo -e "${BLUE}Enabling Managed Identity for Logic App...${NC}"
az logic workflow update \
  --resource-group "$RG_NAME" \
  --name "$LOGIC_APP_NAME" \
  --set identity.type="SystemAssigned" \
  --output none

# 4. Get the Principal ID of the Logic App
LOGIC_APP_PRINCIPAL_ID=$(az logic workflow show \
  --resource-group "$RG_NAME" \
  --name "$LOGIC_APP_NAME" \
  --query "identity.principalId" -o tsv)

echo -e "${GREEN}Logic App Managed Identity ID: ${LOGIC_APP_PRINCIPAL_ID}${NC}"

# 5. Get the Resource ID of the VM
echo -e "${BLUE}Fetching VM Resource ID...${NC}"
VM_ID=$(az vm show --resource-group "$RG_NAME" --name "$VM_NAME" --query id -o tsv)

if [ -z "$VM_ID" ]; then
    echo "Error: VM '$VM_NAME' not found in resource group '$RG_NAME'. Please check your parameters."
    exit 1
fi

# 6. Assign Role to Logic App Identity
echo -e "${BLUE}Assigning 'Virtual Machine Contributor' role to Logic App Identity on the VM...${NC}"
sleep 15 

# Avoid Git Bash converting paths
MSYS_NO_PATHCONV=1 az role assignment create \
  --assignee "$LOGIC_APP_PRINCIPAL_ID" \
  --role "Virtual Machine Contributor" \
  --scope "$VM_ID" \
  --output none

# 7. Define the Workflow JSON
echo -e "${BLUE}Deploying Workflow Definition...${NC}"

# Create workflow.json with "escaped" $schema
cat <<'EOF' > workflow.json
{
    "definition": {
        "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
        "actions": {
            "Deallocate_Virtual_Machine": {
                "inputs": {
                    "authentication": {
                        "type": "ManagedServiceIdentity"
                    },
                    "method": "POST",
                    "uri": "VM_ID_PLACEHOLDER/deallocate?api-version=2023-03-01"
                },
                "runAfter": {},
                "type": "Http"
            }
        },
        "contentVersion": "1.0.0.0",
        "outputs": {},
        "parameters": {},
        "triggers": {
            "Recurrence": {
                "recurrence": {
                    "frequency": "Day",
                    "interval": 1,
                    "schedule": {
                        "hours": [
                            18
                        ],
                        "minutes": [
                            0
                        ]
                    }
                },
                "type": "Recurrence"
            }
        }
    }
}
EOF

# Replace placeholder with actual VM_ID
sed -i "s|VM_ID_PLACEHOLDER|https://management.azure.com${VM_ID}|g" workflow.json

# 8. Update Logic App with the Workflow
MSYS_NO_PATHCONV=1 az logic workflow create \
  --resource-group "$RG_NAME" \
  --location "$LOCATION" \
  --name "$LOGIC_APP_NAME" \
  --definition @workflow.json \
  --output none

# Cleanup temporary json
rm workflow.json

echo -e "${GREEN}Success! Logic App '${LOGIC_APP_NAME}' created.${NC}"
echo -e "${GREEN}It will shut down VM '${VM_NAME}' every day at 18:00.${NC}"
