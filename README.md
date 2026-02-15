# NeuroFlow Firmware

## Build Instructions

1. Flash Raspberry Pi OS (64-bit) to the Raspberry Pi 5

2. SSH into the system from laptop terminal  
<code> ssh brain@braindrain.local </code>

3. Update the OS and enable I2C + auto login  
<code>sudo apt update  
sudo apt full-upgrade -y  
sudo reboot  
sudo raspi-config </code>

4. Install dependencies and clone the repository  
Install global dependencies:  
<code>sudo apt install python3-venv python3-pip python3-dev git liblgpio-dev python3-lgpio unclutter -y</code> 
<code>sudo apt install build-essential swig python3-dev -y</code>
 
Clone repository:  
<code>cd ~
git clone git@github.com:aidankirwin/braindrain-fw.git  
cd pump-controller
</code>  

Clone project dependencies in a venv:  
<code>
python3 -m venv venv  
source venv/bin/activate  
pip install --upgrade pip 
pip install adafruit-circuitpython-ads1x15 gpiozero lgpio
</code>

5. Hide Desktop and Remove Screensaver
- Hide desktop
<code>
mkdir -p ~/.config/pcmanfm/LXDE-pi
nano ~/.config/pcmanfm/LXDE-pi/desktop-items-0.conf
</code>
<code>
[*]
wallpaper_mode=color
desktop_bg=#000000
desktop_fg=#ffffff
show_trash=0
show_mounts=0
</code>

- Remove screensaver 
<code>nano /home/brain/kiosk_setup.sh</code>
<code>
#!/bin/bash

export DISPLAY=:0
export XAUTHORITY=/home/brain/.Xauthority

xset s off
xset -dpms
xset s noblank

unclutter -idle 0 -root &
</code>
<code>
chmod +x /home/brain/kiosk_setup.sh
</code>

6. Configure Systemd to Auto-start App

Create the service file:  
<code>sudo nano /etc/systemd/system/braindrain.service</code>

Paste: 
<code>

[Unit]
Description=BrainDrain GUI App
After=graphical.target
Wants=graphical.target

[Service]
User=brain
Environment=DISPLAY=:0
Environment=XAUTHORITY=/home/brain/.Xauthority
WorkingDirectory=/home/brain/brain_drain_fw

ExecStartPre=/home/brain/kiosk_setup.sh
ExecStart=/home/brain/brain_drain_fw/venv/bin/python main.py

Restart=always
RestartSec=2

StandardOutput=journal
StandardError=journal

[Install]
WantedBy=graphical.target

</code>

Enable and start:  
<code>
sudo systemctl daemon-reload
sudo systemctl enable braindrain.service
sudo systemctl start braindrain.service  
</code>