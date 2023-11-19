
# Create Temp Folder in Powershell
$TempFolder = New-Item -ItemType Directory -Path "$env:TEMP\StreetContinuity" -Force

# Download Street StreetContinuity.zip from GitHub (https://github.com/gabrielspadon/StreetContinuity/archive/refs/heads/master.zip)
# Update 19.11.2023 Mit dem aktuellen Stand von StreetContinuity lässt sich wegen Inkompatiblität der Bibliotheken nicht arbeiten. Daher
# habe ich einen Pull Request mit aktualisierten Bibliotheken und gefixten Code erstellt. Stattdessen wird dieser heruntergeladen.
Invoke-WebRequest -Uri "https://github.com/theodm/StreetContinuity/archive/refs/heads/feature/Update_To_Newer_Libary_Versions.zip" -OutFile "$env:TEMP\StreetContinuity\StreetContinuity.zip"

# Extract StreetContinuity.zip to Temp Folder
Expand-Archive -Path "$env:TEMP\StreetContinuity\StreetContinuity.zip" -DestinationPath "$env:TEMP\StreetContinuity"

# Change workign directory to script root
Set-Location -Path $PSScriptRoot

# Create .\src\libs\streetcontinuity folder if it doesn't exist
New-Item -ItemType Directory -Path ".\libs\streetcontinuity" -Force

# Copy Extracted Files to Script root and .\src\libs\streetcontinuity
Copy-Item -Path "$env:TEMP\StreetContinuity\StreetContinuity-master\*" -Destination ".\libs\streetcontinuity" -Recurse -Force

# Install into Pip
pip install -e ".\libs\streetcontinuity" --user

# Remove Temp Folder
Remove-Item -Path "$env:TEMP\StreetContinuity" -Recurse -Force

