# Simple Raspberry PI Internet radio using one button
# Nicolas - March 2015

import RPi.GPIO as GPIO
import os
from subprocess import Popen
import atexit
from time import sleep
import random

#Set up Display
from RPLCD import CharLCD
'''GPIO pin (BCM) for LCD
#RS : GPIO23      was GPIO25
#E : GPIO24
#D4 : GPIO4       was GPIO23
#D5 : GPIO17
#D6 : GPIO27
#D7 : GPIO22'''
lcd = CharLCD(cols=16, rows=2, pin_rw=None, pin_rs=23, pin_e=24, pins_data=[4,17,27,22], numbering_mode=GPIO.BCM)

# Switch definitions (BCM)
CHANNEL_UP = 13 #GPIO13

# Define radio station and create a playlist
radioname = []
frequence = []
radiourl = []
radioinit = 1

radioname.append("Chante France")
frequence.append("90.9 FM")
radiourl.append("http://stream.chantefrance.com/stream_chante_france.mp3")

radioname.append("Cherie FM")
frequence.append("91.3 FM")	
radiourl.append("http://adwzg3.tdf-cdn.com/8473/nrj_178499.mp3")

radioname.append("BFM Business")
frequence.append("96.4 FM")	
radiourl.append("http://mp3lg4.tdf-cdn.com/10161/bfmbusiness.mp3")
	
radioname.append("Radio FG")
frequence.append("98.2 FM")	
radiourl.append("http://radiofg.impek.com/fg.mp3")
	
radioname.append("Radio Classique")
frequence.append("101.1 FM")
radiourl.append("http://radioclassique.ice.infomaniak.ch/radioclassique-high.mp3")

radioname.append("Radio Nova")
frequence.append("101.5 FM")	
radiourl.append("http://ice15.infomaniak.ch:80/radionova-high.mp3")
	
radioname.append("Oui FM")
frequence.append("102.3 FM")
radiourl.append("http://ouifm.ice.infomaniak.ch/ouifm-high.mp3")	
	
radioname.append("Europe 1")
frequence.append("104.7 FM")	
radiourl.append("http://mp3lg4.tdf-cdn.com/9240/lag_180945.mp3")
	
radioname.append("France Info")
frequence.append("105.5 FM")
radiourl.append("http://mp3.live.tv-radio.com/franceinfo/all/franceinfo.mp3")

# Register exit routine
def finish():
	lcd.clear()
	lcd.cursor_pos = (0, 3)
	lcd.write_string("Stopping...")	
	exec_command("service mpd stop")		
	GPIO.cleanup()
	print("Radio stopped")
atexit.register(finish)

# Execute system command sub-routine
def exec_command(cmd):
	result = ""
	p = os.popen(cmd)
	for line in p.readline().split('\n'):
		result = result + line
	return result

### Main routine ###
if __name__ == "__main__":
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(CHANNEL_UP,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)

	omxp = Popen(['omxplayer','/home/pi/Desktop/Nicolas/radio-start.mp3'])
	lcd.clear()
	lcd.cursor_pos = (0, 1)
	lcd.write_string("Connecting...")	
	
	exec_command("service mpd start")
	exec_command("mpc clear")

	sleep(1)
		
	for i in range(len(radioname)-1):
		exec_command("mpc add " + radiourl[i])
	
	radioinit = random.randint(0, len(radioname)-1)        #there are 9 elements in the array (0 to 8)
	current_pls_no = radioinit + 1                         #init the item in the playlist based on random radioname element
	max_pls_no = len(radioname)                            #there are 9 elements in the array; and hence 9 radio stations in mpd
	
	exec_command("mpc play " + str(current_pls_no))        #start with a random radio station in the list
	exec_command("mpc volume 90")
	
	current = exec_command("mpc current")
	print "Streaming... " + current
	print radioname[radioinit]
	print "press CTRL + C to stop"
	
	# Update the LCD display with radio 's name
	lcd.clear()
	offset = int((16 - len(radioname[current_pls_no - 1]))/2)
	lcd.cursor_pos = (0, offset)
	lcd.write_string(radioname[current_pls_no - 1])
	offset = int((16 - len(frequence[current_pls_no - 1]))/2)
	lcd.cursor_pos = (1, offset)     
	lcd.write_string(frequence[current_pls_no - 1])
	
	while True:
		sleep(0.001) # do not use all the cpu power
		newChannel = False
		
		if GPIO.input(CHANNEL_UP):
			count = 0
			#omxp = Popen(['omxplayer','/home/pi/Desktop/Nicolas/radio-beep.mp3'])
		
			while GPIO.input(CHANNEL_UP): #call: is button still pressed
				sleep(0.001)              # do not use all the cpu power
				count += 0.01
				
			if count<15:      #if this is a short press
				if current_pls_no < max_pls_no:
					exec_command("mpc next")
					current_pls_no += 1
				elif current_pls_no == max_pls_no:
					exec_command("mpc play 1")
					current_pls_no = 1				
				newChannel = True
				
			elif count>=15:    #if this is a long press
				lcd.clear()
				lcd.cursor_pos = (0, 2)
				lcd.write_string("Stopping...")	
				omxp = Popen(['omxplayer','/home/pi/Desktop/Nicolas/radio-start.mp3'])
				sleep(0.5)
				exec_command("sudo halt")
	
		if newChannel:
			#////////////update Display on LCD////////////
			lcd.clear()
			offset = int((16 - len(radioname[current_pls_no - 1]))/2)
			lcd.cursor_pos = (0, offset)
			lcd.write_string(radioname[current_pls_no - 1])
			offset = int((16 - len(frequence[current_pls_no - 1]))/2)
			lcd.cursor_pos = (1, offset)     
			lcd.write_string(frequence[current_pls_no - 1])
						
		sleep(0.2)
