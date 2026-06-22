$repoUrl = "https://raw.githubusercontent.com/mthtclone/simple-stable-difussion-generator/main/version.json"

try {
    Write-Host "Fetching version info..."

    $v = Invoke-RestMethod $repoUrl

    Write-Host "Remote version:" $v.version

    if (!(Test-Path "version.txt")) {
        Set-Content version.txt "0.0.0"
    }

    $local = Get-Content version.txt
    Write-Host "Local version:" $local

    if ([version]$v.version -gt [version]$local) {

        Write-Host "Update available"

        Invoke-WebRequest $v.url -OutFile update.zip

        Write-Host "Download complete"

        if (Test-Path "temp_update") {
            Remove-Item temp_update -Recurse -Force
        }

        Expand-Archive update.zip -DestinationPath temp_update -Force

        $folder = Get-ChildItem temp_update | Select-Object -First 1

        Copy-Item -Path (Join-Path temp_update $folder.Name\*) -Destination . -Recurse -Force

        Set-Content version.txt $v.version

        Remove-Item update.zip -Force
        Remove-Item temp_update -Recurse -Force

        Write-Host "Update applied"
    }
    else {
        Write-Host "Already up to date"
    }
}
catch {
    Write-Host "ERROR:"
    Write-Host $_.Exception.Message
}
Write-Host "Update finished"