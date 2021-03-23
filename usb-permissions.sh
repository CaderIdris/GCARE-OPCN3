#!/usr/bin/env bash
cd "/media/$USER/"  # Change directory to the user's media directory, removeable media should be present here
directory_name="/media/$USER/"  # Save path to media directory as variable
for usb_device in */ ; do  # Iterate over all folders in media directory
  echo -e "Modifying permissions for: ${directory_name}/${usb_device}"
  device_info=$(df -T | grep usb_device | tr -s ' ' )  # Get device info, with multispace delimeters reduced to 1 space
  device_location=$(echo $device_info | cut -d' ' -f1) # Get first value from df (device path)
  filesystem_type=$(echo $device_info | cut -d' ' -f2) # Get second value from df (Filesystem)
  echo "Device location: ${device_location}"
  echo "Filesystem: ${filesystem_type}"
  sudo bash -c "grep '${directory_name}/${usb_device}' /etc/fstab || sudo printf '\n$device_location ${directory_name}/${usb_device} $filesystem_type defaults 0 2\n' >> /etc/fstab" # If the device isn't in fstab, add it in
done


echo -e "\n Finished updating USB permissions"
