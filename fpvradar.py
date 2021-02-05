import requests
import geopy.distance
import time
import sys
from gps import *
from time import sleep
from gpiozero import Buzzer
from datetime import datetime

# Disclaimer: This code is not pretty. It is written like a script since that is what it is. 
DUMP1090_URL = 'http://127.0.0.1/dump1090-fa/data/aircraft.json'
UNKNOWN = 'Unknown'
LATITUDE = 'lat'
LONGTITUDE = 'lon'
BUZZER_PIN = 17
# seconds between each check
INTERVAL_SECONDS = 3
# set this to false if you don't want a long beep on initial gps lock
initialGPSLockBeep=True 
# I keep this value large so I know the app is running since it will always beep once.
# you can set the value lower to have a quieter system and a 3rd perimeter
OUTER_PERIMETER_ALARM_MILES = 100 
# middle perimeter trigger sets of 2 beeps
MIDDLE_PERIMETER_ALARM_MILES = 5
# inner perimeter trigger sets of 3 beeps
INNER_PERIMETER_ALARM_MILES = 2
# upper limit of altitude at which you want to monitor aircraft
ALTITUDE_ALARM_FEET = 1000
running = True
gpsd = gps(mode=WATCH_ENABLE | WATCH_NEWSTYLE)
buzzer = Buzzer(BUZZER_PIN)
lastKnownLat=UNKNOWN
lastKnownLon=UNKNOWN
# the number of iterations we should try to reuse the last known position 
# set this to -1 if you plan on relocating the unit to a location with poor GPS 
# reception once initial position is established and you don't plan on moving around
# then it will never need the GPS coordinates again if they are not available
LAST_KNOWN_POSITION_REUSE_TIMES = 3
lastKnownPosReuse=0
failedGPSTries=0

def getPositionData(gps):
    nx = gpsd.next()
    # For a list of all supported classes and fields refer to:
    # https://gpsd.gitlab.io/gpsd/gpsd_json.html
    global lastKnownLat
    global lastKnownLon
    global lastKnownPosReuse
    if nx['class'] == 'TPV':
        lastKnownLat = getattr(nx, LATITUDE, UNKNOWN)
        lastKnownLon = getattr(nx, LONGTITUDE, UNKNOWN)
        lastKnownPosReuse=0 #reset counter since we refreshed coords
        #print "Your position: lon = " + str(longitude) + ", lat = " + str(latitude)
        return (lastKnownLat, lastKnownLon)
    else:
        print "NON TPV gps class encountered: "+nx['class']
        if LAST_KNOWN_POSITION_REUSE_TIMES < 0:
    	    return (lastKnownLat, lastKnownLon)
        elif lastKnownPosReuse < LAST_KNOWN_POSITION_REUSE_TIMES:
            lastKnownPosReuse += 1
    	    return (lastKnownLat, lastKnownLon)
    	else:
    	    return(UNKNOWN,UNKNOWN)

def buzz(wait=0.1):
    buzzer.on()
    sleep(wait)
    buzzer.off()
    sleep(0.2)

def checkRadar():
    global failedGPSTries
    global gpsd
    homecoords = getPositionData(gpsd)
    print homecoords
    if (homecoords[0] == UNKNOWN) or (homecoords[1] == UNKNOWN):
        #print "Cannot determine GPS position yet...try #"+str(failedGPSTries)
        #sleep(1)
        failedGPSTries += 1
        if failedGPSTries > 10:
            print "Too many failed GPS tries, initializing new GPS object..."
            failedGPSTries = 0
            gpsd = gps(mode=WATCH_ENABLE | WATCH_NEWSTYLE)
        return
    global initialGPSLockBeep
    if initialGPSLockBeep == True:
    	initialGPSLockBeep=False
       	buzz(1)
        sleep(5)
    r = requests.get(DUMP1090_URL)
    try:
        airplanes = r.json()
    except:
        #print 'Error while getting airplane data'
        return
    outerAlarmTriggered = False
    middleAlarmTriggered = False
    innerAlarmTriggered = False
    for airplane in airplanes['aircraft']:
        try:
            altitude = airplane["alt_baro"]
            planecoords = (airplane[LATITUDE], airplane[LONGTITUDE])
            distanceToPlane = geopy.distance.vincenty(homecoords, planecoords).miles
            if altitude < ALTITUDE_ALARM_FEET:
                if distanceToPlane < INNER_PERIMETER_ALARM_MILES:
                    innerAlarmTriggered = True
                    print 'Inner alarm triggered by '+airplane['flight']+' at '+str(datetime.now())+' with distance '+str(distanceToPlane)
                elif distanceToPlane < MIDDLE_PERIMETER_ALARM_MILES:
                    middleAlarmTriggered = True
                    print 'Middle alarm triggered by '+airplane['flight']+' at ' +str(datetime.now())+' with distance '+str(distanceToPlane)
                elif distanceToPlane < OUTER_PERIMETER_ALARM_MILES:
                    outerAlarmTriggered = True
                    print 'Outer alarm triggered by '+airplane['flight']+' at ' +str(datetime.now())+' with distance '+str(distanceToPlane)
        except KeyError:
            pass
    if innerAlarmTriggered:
        buzz()
        buzz()
        buzz()
    elif middleAlarmTriggered:
        buzz()
        buzz()
    elif outerAlarmTriggered:
        buzz()


try:
    print "Application started!"
    while running:
        checkRadar()
        sys.stdout.flush()
        time.sleep(INTERVAL_SECONDS)

except (ValueError):
	#sometimes we get errors parsing json
    pass

except (KeyboardInterrupt):
    running = False
    print "Applications closed!"

except:
    print "Caught generic exception - continuing"
    sys.stdout.flush()
    pass

