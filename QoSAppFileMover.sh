#!/bin/bash

# Directory containing QoS-Slicing Java files
qos_slicing_dir="/home/dante/QoS-Slicing/ONOS File"

# Root directory of the ONOS source code
onos_dir="/home/dante/5G-UAV-Emulation-Framework/onos"

# Backup directory for ONOS files
backup_dir="home/dante/onos-backupp"

if [ ! -d "$backup_dir" ]; then
  echo "Creating backup directory at $backup_dir..."
  mkdir -p "$backup_dir"
  if [ $? -ne 0 ]; then
    echo "Failed to create backup directory. Check permissions or path."
    exit 1
  fi
fi

# List of Java files to move
declare -a files=("MeterId.java" "LinkCollectionCompiler.java" "MeterManager.java" "MeterService.java" "MeterServiceAdapter.java" "VirtualNetworkMeterManager.java")

# Loop through each file
for file in "${files[@]}"; do
  echo "Processing $file..."

  # Find the directory that contains the file in the ONOS source
  target_path=$(find $onos_dir -type f -name $file)

  # Check if the target path was found
  if [ -z "$target_path" ]; then
    echo "No target file found for $file"
  else
    target_dir=$(dirname "$target_path")
    # Backup original file if exists
    if [ -f "$target_path" ]; then
      echo "Backing up $target_path..."
      cp "$target_path" "$backup_dir/"
    fi

    # Move the file to the found directory
    echo "Moving $file to $target_dir..."
    cp "$qos_slicing_dir/$file" "$target_dir/"
  fi
done

echo "All files processed."
