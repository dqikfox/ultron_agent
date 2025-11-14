# Azure Automation CLI Commands

# List automation keys
az automation account list-keys \
  --resource-group resource \
  --name ultron \
  --subscription 3800ba58-67c9-477b-ab3a-bc02808c38f6

# Show linked workspace
az automation account show-linked-workspace \
  --resource-group resource \
  --name ultron \
  --subscription 3800ba58-67c9-477b-ab3a-bc02808c38f6

# List configurations
az automation configuration list \
  --resource-group resource \
  --account ultron \
  --subscription 3800ba58-67c9-477b-ab3a-bc02808c38f6

# List hybrid runbook worker groups
az automation hrwg list \
  --automation-account-name ultron \
  --resource-group resource \
  --subscription 3800ba58-67c9-477b-ab3a-bc02808c38f6

# List Python3 packages
az automation python3-package list \
  --automation-account-name ultron \
  --resource-group resource \
  --subscription 3800ba58-67c9-477b-ab3a-bc02808c38f6

# List runtime environments
az automation runtime-environment list \
  --resource-group resource \
  --account ultron \
  --subscription 3800ba58-67c9-477b-ab3a-bc02808c38f6

# List source control
az automation source-control list \
  --resource-group resource \
  --account ultron \
  --subscription 3800ba58-67c9-477b-ab3a-bc02808c38f6
