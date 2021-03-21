#!/usr/bin/env bash
cd "/media/$USER/"
directory_name=$(pwd)
for usb_device in */ ; do
  echo -e "Modifying permissions for: ${directory_name}/${usb_device}"
  device_info=$(df -T | grep "/media/$USER/"  | tr -s ' ' )
  #echo $device_info
  device_location=$(echo $device_info | cut -d' ' -f1)
  filesystem_type=$(echo $device_info | cut -d' ' -f2)
  echo "Device location: ${device_location}"
  echo "Filesystem: ${filesystem_type}"
  sudo bash -c "grep '${directory_name}/${usb_device}' /etc/fstab || sudo printf '\n${directory_name}/${usb_device} $device_location $filesystem_type defaults 0 2\n' >> /etc/fstab"
done


echo -e "\n Finished updating USB permissions"
