# FPV Radar

https://youtu.be/YkmsAgEEuzo  

https://youtu.be/ppq6NCjMSJI (video of another user's build in action. Thanks Colby!)

Monitors the nearby airspace for low flying aircraft.  
I was initially inspired by and made aware of ADSB by xjet (good old Bruce). https://www.youtube.com/watch?v=ggaDvxNtJ2Q  
I waited and waited for him to release his code, but alas he forgot and I ended up implementing my own solution. 
To clarify, this is a standalone device and does not require wifi/and or data plan to work. Check your country for ADSB requirements. 

# License
The code herein written by the Author is released under the terms of the unlicense. https://unlicense.org/

# Required components:

1) Raspberry pi (zero w used in this guide) https://www.banggood.com/custlink/mvDhZjVbBW (don't buy it at banggood unless you have to since it's expensive there)
2) GPS module (e.g. Beitian 220) https://www.banggood.com/custlink/mGmRZjPN0m
3) Buzzer https://www.banggood.com/custlink/GGKdSoHb0F
4) SDR Dongle (e.g. flightaware, rtl-sdr) I am using the flighaware pro stick plus https://flightaware.com/adsb/prostick/ or for something more compact https://www.amazon.com/gp/product/B01K5K3858/ (I haven't tested this one tho)
5) micro usb to USB adapter or HUB (if using pi zero since it doesn't have full size usb ports) I used the Zero4U 4 Port USB Hub
6) 5v voltage regulator for external battery power (optional) - I recommend 2-3A
7) Antenna - mine is homemade, but you can purchase a 1090 one easily https://www.amazon.com/NooElec-ADS-B-Discovery-Antenna-Bundle/dp/B01J9DH9U2/ref=sr_1_6?dchild=1&keywords=1090+antenna&qid=1612488541&sr=8-6
8) Case - I used the top cover for the one here: https://www.thingiverse.com/thing:1886598 I snipped away ap portion of it to glue in the gps.

# Installation

1) Install piaware (version 4 as of this build) https://flightaware.com/adsb/piaware/build  

2) Follow the optional instructions for enabling wifi (modify piaware-config.txt to put in wifi info)  

3) Enable ssh by creating an empty file on the /boot partition of the SD card with the filename of "ssh"  

4) Enable on/off button - While optional, this is highly recommended so that you don't screw up the file system since you won't be able to ssh into the pie to shut down out in the field.  
If you use Raspbian stretch 2017.08.16 or newer, all that is required is to add a line to /boot/config.txt (and reboot for this to take effect):  
dtoverlay=gpio-shutdown,gpio_pin=3  
see https://www.stderr.nl/Blog/Hardware/RaspberryPi/PowerButton.html  
You will also need to wire a momentary switch/button between GPIO3(pin 5) & Ground. Pressing it once will shutdown the system (wait until all the lights die before unplugging) and pressing it again will start up the system.

5) Buzzer (optional) - wire positive to GPIO17 and black to any ground. 

6) Install the following libraries:  
sudo apt-get update  
sudo apt-get install python-requests  
sudo apt install python-gpiozero  
sudo apt install python-geopy  
sudo apt install git  

7) Set up GPS:
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


8) Clone this repo into the home directory.   
Make sure you're in the home directory /home/pi and type "git clone https://github.com/lexfp/fpvradar.git"  
After the command runs, you should have a fpvradar directory with all the files inside.
Make sure the file /home/pi/fpvradar/fpvradar.py exists.   You can type "ls /home/pi/fpvradar/fpvradar.py"  
At this time you should probably go into the code using your favorite editor (type "nano /home/pi/fpvradar/fpvradar.py") and change the values for the different perimeter alarms along with the altitude at which you want to monitor (INNER_PERIMETER_ALARM_MILES, ALTITUDE_ALARM_FEET, etc...). If you want to play with the other options/settings, be sure to test them as I haven't done much testing other than the defaults. Once you finish editing, you can hit ctrl-x to exit and it will ask you if you want to save first. Just answer yes.

9) Turn fpvradar into a service which automatically starts:
/lib/systemd/system/fpvradar.service (move included fpvradar.service file to /lib/systemd/system)    
sudo systemctl daemon-reload  
sudo systemctl enable fpvradar.service    
If you need to check if it is running after you reboot, you can use the status command:  
sudo systemctl status fpvradar.service  
If things appear running but they still don't work, then move on to the next steps and check the logs.  

10) Persistent LOGS (Optional)  
set your time zone (https://en.wikipedia.org/wiki/List_of_tz_database_time_zones):  
sudo timedatectl set-timezone America/New_York  
sudo mkdir -p /var/log/journal
sudo nano /etc/systemd/journald.conf
change/add the following:  
Storage=persistent
To see the logs you can use the following commands (you can also use -2,-3 to go back even further):  
sudo journalctl -b 0 -u fpvradar.service (current boot logs)  
sudo journalctl -b -1 -u fpvradar.service (previous boot logs) 

11) Power  
You can power your pi from the regular USB port or an external battery. If using an external battery, you'll need to use a 5v regulator. There are a few ways to wire up the PI to be powered from a battery, but I went with hooking up a 5v regulator to the 5v rails. You can google the different options.

12) Screen (optional)  
The reason I did not add a screen to this like Bruce did was for a multitude of reasons. Since I fly fpv, I would not be looking at the screen most of the time and it would only consume extra power. I also wanted it to be as compact and inexpensive as possible. Should you want to add a screen, however, there is an easy solution. If you carry a cell phone, simply create a hotspot with the same wifi name/password as you used at your home router. While you're out in the field, it will not find your home router, but will connect to your phone instead. Once it connects to your phone, you will need to find the IP address of the Pi. If your phone doesn't let you see it by default, you'll need to install an hotspot manager app such as https://play.google.com/store/apps/details?id=com.catchy.tools.mobilehotspot.dp&hl=en_US&gl=US which will show it to you. Once you find the ip, simply enter it in your browser on the phone and it will show you a map with surrounding planes (default piaware screen). 

## Troubleshooting  
Most of the issues I've experienced are from the GPS not getting signal while testing indoors. You will also need to double check your wiring to make sure everything is hooked up correctly. Try writing code to test each component separately (buzzer, gps).

## Future  
Adding a second dongle to monitor 978 as well.  
Instead of using gps data from the PI, feed telemetry position data from the plane back into the PI. Maybe bluetooth?  
If someone wants to design a better 3d printed case for this, I would be happy to link to it.  

## FAQ: 

How good is the range?  
Depends on your antenna. I use the pro stick which has an internal filter. Coupled with my home made antenna, I can often see aircraft in other states over 100 miles away. This is with the antenna sitting on my desk inside my house. Since you'll be using this outside, I can't imagine that you would have any issues unless you used a really poor antenna.

Can I use other Pis?  
Yes, you should be able to use almost any. My initial prototype (these pics are my 2nd prototype) was a Pi 3 model B from 2016. Unfortunately, I burned that one up by wiring up a voltage regulator to it without checking the inputs/outputs. Since I knew the concept worked, I wanted to build the second one to be as small/compact as possible.  

Do you sell these?  
No. My time is worth a lot to me, so go build your own.  

Why do you have switches on yours?  
The white switch is the momentary on/off switch to turn the pi on and off out in the field. Unplugging is a bad idea as you can corrupt your file system in which case you have to reformat the card and start from scratch. The black switch is if I am at home and I don't want to use the GPS/buzzer and I just want to monitor aircraft around me instead.  

What is the approximate cost?  
For the setup I have, the cost of the components are around $50. This doesn't include the antenna which I made myself.  

How much testing has gone into this?  
Almost none (except for my own). Seriously, I haven't tested a lot of the conditions in there since they are useless to me, so some things may not work. Please test everything yourself and let me know if you find any bugs. 

Are there alternate cases?  
Here's a design by Colby Terry: https://www.thingiverse.com/thing:4756697?fbclid=IwAR1rNRHUoMtD9yErSb5yf0OHlEy4OJyrLd6rC7ygGXJgEToh9D8qGnDaD9E 
