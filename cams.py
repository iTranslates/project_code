import board
import busio
import adafruit_ssd1306
import time
import datetime
from PIL import Image, ImageDraw, ImageFont
import speech_recognition as sr
import picamera
import RPi.GPIO as GPIO

# Set up the GPIO pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Set up OLED display
i2c = busio.I2C(board.SCL, board.SDA)
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3C, reset=None)

# Set up speech recognition
r = sr.Recognizer()
mic = sr.Microphone(sample_rate=16000, chunk_size=1024)

# Create a function to take a picture
def take_picture():
    with picamera.PiCamera() as camera:
        camera.start_preview()
        time.sleep(2)
        timestamp = time.strftime('%Y%m%d%H%M%S')
        filename = '/home/pi/image_{}.jpg'.format(timestamp)
        camera.capture(filename)
        camera.stop_preview()
        print("Picture taken!")

# Set up initial display message
date_string = ''
time_string = ''
speech_text = ''
message1 = ''
message2 = ''
message3 = ''
message = 'Say something!'

# Continuously listen for and transcribe speech
while True:
    with mic as source:
        r.adjust_for_ambient_noise(source)  # adjust for ambient noise
        oled.fill(0)  # clear OLED display
        
        # Create blank image for drawing.
        image = Image.new("1", (oled.width, oled.height))
        
        # Get drawing object to draw on the image.
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()
        
        # Update date and time strings
        now = datetime.datetime.now()
        new_date_string = now.strftime("%a, %b %d %Y")
        new_time_string = now.strftime("%I:%M %p")
        
        # Update display message with speech text or date and time strings
        if speech_text:
            lines = speech_text.split('\n')
            if len(lines) > 0:
                message1 = lines[0][:20]  # truncate message to 20 characters
                if len(lines[0]) > 20:
                    message2 = lines[0][20:][:20]  # add a new line if message exceeds 20 characters
                if len(lines) > 1:
                    message3 = lines[1][:20]  # truncate message to 20 characters
                    if len(lines[1]) > 20:
                        message4 = lines[1][20:][:20]  # add a new line if message exceeds 20 characters
                    

            # Draw message on OLED display
            draw.text((0, 0), message1, font=font, fill=255)
            draw.text((0, 10), message2, font=font, fill=255)
            draw.text((0, 20), message3, font=font, fill=255)
            draw.text((0, 30), message4, font=font, fill=255)

            oled.image(image)
            oled.show()   
        else:
            message1 = new_date_string
            message2 = new_time_string
            message3 = ''
            draw.text((0, 0), message1, font=font, fill=255)
            draw.text((0, 10), message2, font=font, fill=255)
            oled.image(image)
            oled.show()
        
        audio = r.listen(source)

    try:
        # recognize speech using Google Speech Recognition
        text = r.recognize_google(audio)
        
        # Update speech text with transcribed text
        speech_text = text

    except sr.UnknownValueError:
        # display error message on OLED display if speech cannot be transcribed
        speech_text = ''
        
    except sr.RequestError as e:
        # display error message on OLED display if there is an error with the API
        speech_text = 'API error: ' + str(e)

    # wait a short time before listening again
    time.sleep(0.1)
    
    # Continuously check if the button is pressed
    if GPIO.input(24) == GPIO.LOW:
        take_picture()
        time.sleep(0.2)
