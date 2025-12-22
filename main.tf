terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    # While Terraform often downloads this automatically, 
    # it is good practice to declare the random provider.
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

# --- Variables ---
variable "resource_group_name" {
  default = "demo-rg-dsvm-llm01"
}

variable "location" {
  default = "polandcentral"
}

variable "vm_name" {
  default = "demo-dsvm-llm-01"
}

variable "vm_size" {
  default = "Standard_NC4as_T4_v3"
}

variable "admin_username" {
  default = "azuser"
}

# Pass your public key file content or raw string here
variable "ssh_public_key" {
  description = "The SSH public key data."
  type        = string
  sensitive   = true
}

# --- Resources ---

# 1. Resource Group
resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location
}

# 2. Networking (VNet, Subnet, Public IP, NSG)
resource "azurerm_virtual_network" "vnet" {
  name                = "${var.vm_name}-vnet"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
}

resource "azurerm_subnet" "subnet" {
  name                 = "default"
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.0.0.0/24"]
}

# Used to generate a unique string similar to uniqueString() in Bicep
resource "random_id" "id" {
  byte_length = 4
}

resource "azurerm_public_ip" "pip" {
  name                = "${var.vm_name}-ip"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  allocation_method   = "Static"
  sku                 = "Standard"
  # FIXED: Changed unique_id.id.hex to random_id.id.hex
  domain_name_label   = lower("${var.vm_name}-${substr(random_id.id.hex, 0, 6)}")
}

resource "azurerm_network_security_group" "nsg" {
  name                = "${var.vm_name}-nsg"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  security_rule {
    name                       = "SSH"
    priority                   = 1000
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "JupyterHub"
    priority                   = 1010
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "8000"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "Marimo"
    priority                   = 1020
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "2718"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
}

resource "azurerm_subnet_network_security_group_association" "nsg_assoc" {
  subnet_id                 = azurerm_subnet.subnet.id
  network_security_group_id = azurerm_network_security_group.nsg.id
}

# 3. Network Interface
resource "azurerm_network_interface" "nic" {
  name                = "${var.vm_name}-nic"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  ip_configuration {
    name                          = "ipconfig1"
    subnet_id                     = azurerm_subnet.subnet.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.pip.id
  }
}

# 4. Virtual Machine (DSVM)
resource "azurerm_linux_virtual_machine" "vm" {
  name                = var.vm_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  size                = var.vm_size
  admin_username      = var.admin_username
  
  # Ensure SSH authentication is used
  disable_password_authentication = true

  network_interface_ids = [
    azurerm_network_interface.nic.id,
  ]

  admin_ssh_key {
    username   = var.admin_username
    public_key = var.ssh_public_key
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "StandardSSD_LRS"
    disk_size_gb         = 150
  }

  # Matches your Bicep imageReference
  source_image_reference {
    publisher = "microsoft-dsvm"
    offer     = "ubuntu-2204"
    sku       = "2204-gen2"
    version   = "latest"
  }
}

# 5. Custom Script Extension (Runs deploy.sh)
resource "azurerm_virtual_machine_extension" "install_dependencies" {
  name                 = "install-dependencies"
  virtual_machine_id   = azurerm_linux_virtual_machine.vm.id
  publisher            = "Microsoft.Azure.Extensions"
  type                 = "CustomScript"
  type_handler_version = "2.1"
  auto_upgrade_minor_version = true

  settings = jsonencode({
    "fileUris": [
      "https://raw.githubusercontent.com/tzcnsrkn/llm-azure-demo-workspace/refs/heads/main/deploy.sh"
    ]
  })

  protected_settings = jsonencode({
    "commandToExecute": "bash deploy.sh"
  })
}

# --- Outputs ---
output "ssh_command" {
  value = "ssh ${var.admin_username}@${azurerm_public_ip.pip.fqdn}"
}

output "marimo_url" {
  value = "http://${azurerm_public_ip.pip.fqdn}:2718"
}

output "public_ip_address" {
  value = azurerm_public_ip.pip.ip_address
}