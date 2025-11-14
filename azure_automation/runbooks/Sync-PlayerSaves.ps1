
param([string]$StorageAccount, [string]$Container)
$saves = Get-AzStorageBlob -Container $Container -Context (Get-AzStorageAccount -Name $StorageAccount).Context
foreach($save in $saves) {
    Write-Output "Syncing: $($save.Name)"
}
