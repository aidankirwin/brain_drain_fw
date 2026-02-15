# NeuroFlow Firmware

## Build Instructions

1. Flash Raspberry Pi OS Lite (64-bit) to the Raspberry Pi 5

2. SSH into the system from laptop terminal  
<code> ssh brain@braindrain.local </code>

3. Update the OS and enable I2C  
<code>sudo apt update  
sudo apt full-upgrade -y  
sudo reboot  
sudo raspi-config </code>

4. Install dependencies and clone the repository  
Install global dependencies:  
<code>sudo apt install python3-venv python3-pip python3-dev git -y</code>  
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
pip install adafruit-circuitpython-ads1x15 gpiozero PyQt6 pyqtgraph
</code>

5. Configure Systemd to Auto-start App

Create the service file:  
<code>sudo nano /etc/systemd/system/braindrain.service</code>

Paste: 
<code>

[Unit]
Description=BrainDrain App
After=graphical.target

[Service]
User=brain
Environment=DISPLAY=:0
Environment=XAUTHORITY=/home/brain/.Xauthority
ExecStart=/home/brain/brain_drain_fw/venv/bin/python /home/brain/brain_drain_fw/main.py
WorkingDirectory=/home/brain/brain_drain_fw
Restart=always
RestartSec=2

[Install]
WantedBy=graphical.target

</code>

Enable and start:  
<code>
sudo systemctl daemon-reload  
sudo systemctl enable braindrain.service  
sudo systemctl start braindrain.service  
</code>