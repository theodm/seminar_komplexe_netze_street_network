# Create Temp Folder in bash
TempFolder="./tmp/$(date +%s)"

# Create Tempfolder if not exists
mkdir -p "$TempFolder"

# Download Street StreetContinuity.zip from GitHub (https://github.com/gabrielspadon/StreetContinuity/archive/refs/heads/master.zip)
# Update 19.11.2023 Mit dem aktuellen Stand von StreetContinuity lässt sich wegen Inkompatiblität der Bibliotheken nicht arbeiten. Daher
# habe ich einen Pull Request mit aktualisierten Bibliotheken und gefixten Code erstellt. Stattdessen wird dieser heruntergeladen.
wget -O "$TempFolder/StreetContinuity.zip" "https://github.com/theodm/StreetContinuity/archive/refs/heads/feature/Update_To_Newer_Libary_Versions.zip"

# Extract StreetContinuity.zip to Temp Folder
unzip -o "$TempFolder/StreetContinuity.zip" -d "$TempFolder"

# # Change working directory to script root
# cd "$(dirname "$0")"

# Create ./src/libs/streetcontinuity folder if it doesn't exist
mkdir -p "./src/libs/streetcontinuity"

# Install into Pip
pip install -e "$TempFolder/StreetContinuity-feature-Update_To_Newer_Libary_Versions"

# Remove Temp Folder
#rm -rf "$TempFolder"
