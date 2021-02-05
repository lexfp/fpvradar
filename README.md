# FPV Radar

Monitors the nearby airspace for low flying aircraft.

# Required components:

1) Raspberry pi (zero w used in this guide)
2) GPS module (e.g. Beitian 220)
3) Buzzer
4) SDR Dongle (e.g. flightaware, rtl-sdr) I am using the flighaware pro stick plus
5) micro usb to USB adapter or HUB (if using pi zero since it doesn't have full size usb ports) I used the Zero4U 4 Port USB Hub
6) 5v voltage regulator for external battery power (optional)

# Installation

1) Install piaware (version 4 as of this build) https://flightaware.com/adsb/piaware/build  

2) Follow the optional instructions for enabling wifi (modify piaware-config.txt to put in wifi info)  

3) Enable ssh by creating an empty file on the /boot partition of the SD card with the filename of "ssh"  

4) Enable on/off button - While optional, this is highly recommended so that you don't screw up the file system since you won't be able to ssh into the pie to shut down out in the field.  
If you use Raspbian stretch 2017.08.16 or newer, all that is required is to add a line to /boot/config.txt (and reboot for this to take effect):  
dtoverlay=gpio-shutdown,gpio_pin=3  
see https://www.stderr.nl/Blog/Hardware/RaspberryPi/PowerButton.html  
You will also need to wire a momentary switch/button between GPIO3(pin 5) & Ground. Pressing it once will shutdown the system (wait until all the lights die before unplugging) and pressing it again will start up the system.

5) Install the following libraries:  
sudo apt-get update  
sudo apt-get install python-requests  
sudo apt install python-gpiozero  
sudo apt install python-geopy  
sudo apt install git  

6) Set up GPS:
For reference, you can use the following site (but follow my instructions instead since they differ a bit):    
https://maker.pro/raspberry-pi/tutorial/how-to-use-a-gps-receiver-with-raspberry-pi-4  
You can use various GPS modules, but I have chosen to use the Beitian 220. For wiring, you can use any of the 5v and grounds. I chose pins 4 & 6. The GPS rx will go to the tx on the pi and vice versa. In the case of the beitian 220, the green wire will go to pin 8 (GPIO14) and the white wire will go to pin 10 (GPIO15).  
Next, you should ssh into your pi and type "sudo raspi-config". Select Interfacing options and then Serial. Enable the serial interface while keeping the login shell disabled.  
Next install the gps software: "sudo apt-get install gpsd gpsd-clients"  
You can test if it works by "cat /dev/serial0". If you see no output, then chances are you may have to switch the tx/rx wires on the GPS (white and green).  
Next add the pi user to the dialout group: "sudo adduser pi dialout"  
Lastly, in order to have this take effect on startup, "sudo nano /etc/default/gpsd"  
Comment out the DEVICES and GPSD_OPTIONS lines and add these lines to the end of the file:  
GPSD_OPTIONS="/dev/serial0"  
GPSD_SOCKET="/var/run/gpsd.sock"  
After rebooting, you can test if everything works with either "sudo gpsmon" or "sudo cgps -s"  


7) Clone this repo into the home directory. Make sure the path /home/pi/fpvradar/fpvradar.py is correct.

8) Turn fpvradar into a service which automatically starts:
/lib/systemd/system/fpvradar.service (move included fpvradar.service file to /lib/systemd/system)    
sudo systemctl daemon-reload  
sudo systemctl enable fpvradar.service    

9) Persistent LOGS (Optional)  
set your time zone (https://en.wikipedia.org/wiki/List_of_tz_database_time_zones):  
sudo timedatectl set-timezone America/New_York  
sudo mkdir -p /var/log/journal
sudo nano /etc/systemd/journald.conf
change/add the following:  
Storage=persistent
To see the logs you can use the following commands (you can also use -2,-3 to go back even further):  
sudo journalctl -b 0 -u fpvradar.service (current boot logs)  
sudo journalctl -b -1 -u fpvradar.service (previous boot logs) 

10) Power  
You can power your pi from the regular USB port or an external battery. If using an external battery, you'll need to use a 5v regulator. 

10) Troubleshooting  
Most of the issues I've experienced are from the GPS not getting signal while testing indoors. You will also need to double check your wiring to make sure everything is hooked up correctly. Try writing code to test each component separately (buzzer, gps).
