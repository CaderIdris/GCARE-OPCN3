#!/usr/bin/env bash

# These extras are designed specifically to setup the use cases for our group, though others may find them useful.
RUN_SH=$(readlink -f "./run.sh")
echo "Creating desktop shortcut"
echo "#!/usr/bin/env xdg-open" > ~/Desktop/OPCN3.desktop
echo "" >> ~/Desktop/OPCN3.desktop
echo "[Desktop Entry]" >> ~/Desktop/OPCN3.desktop
echo "Version=0" >> ~/Desktop/OPCN3.desktop
echo "Type=Application" >> ~/Desktop/OPCN3.desktop
echo "Terminal=true" >> ~/Desktop/OPCN3.desktop
echo "Exec=$RUN_SH" >> ~/Desktop/OPCN3.desktop
echo "Name=OPCN3" >> ~/Desktop/OPCN3.desktop
echo "Comment=" >> ~/Desktop/OPCN3.desktop
echo "Icon=" >> ~/Desktop/OPCN3.desktop

sudo chmod +x ~/Desktop/OPCN3.desktop  # Make it executable
sudo dbus-launch gio set ~/Desktop/OPCN3.desktop metadata::trusted true  # Allows user to click on shortcut to run it
