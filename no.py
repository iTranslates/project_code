import board
import busio
import adafruit_ssd1306
import time
import datetime
from PIL import Image, ImageDraw, ImageFont
import speech_recognition as sr
import picamera
import RPi.GPIO as GPIO

import os
os.system("sudo amixer cset numid=1 0")


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
def take_picture_and_transcribe():
    with picamera.PiCamera() as camera, sr.Microphone(sample_rate=16000, chunk_size=1024) as source:
        camera.start_preview()
        time.sleep(1)
        timestamp = time.strftime('%Y%m%d%H%M%S')
        filename = '/home/pi/image_{}.jpg'.format(timestamp)
        camera.capture(filename)
        camera.stop_preview()
        print("Picture taken!")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)

        try:
            # recognize speech using Google Speech Recognition
            text = r.recognize_google(audio)
            print("Speech Transcription:", text)

        except sr.UnknownValueError:
            # display error message on OLED display if speech cannot be transcribed
            text = ''
            print("Speech could not be transcribed")

        except sr.RequestError as e:
            # display error message on OLED display if there is an error with the API
            text = ''
            print("API error: ", e)

        # update OLED display with speech and image information
        oled.fill(0)
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()

        # Update date and time strings
        now = datetime.datetime.now()
        new_date_string = now.strftime("%a, %b %d %Y")
        new_time_string = now.strftime("%I:%M %p")

        # Create message to display on OLED
        if text:
            lines = text.split('\n')
            if len(lines) > 0:
                if len(lines[0]) > 20:
                    message1 = lines[0][:20]  # truncate first line to 20 characters
                    if len(lines[0]) > 40:
                        message2 = lines[0][20:40]  # add a new line if first line exceeds 40 characters
                        if len(lines[0]) > 60:
                            message3 = lines[0][40:60]  # add a new line if first line exceeds 60 characters
                            if len(lines[0]) > 80:
                                message4 = lines[0][60:80]  # add a new line if first line exceeds 80 characters
                            else:
                                message4 = lines[0][60:]  # add the remaining characters to the last line
                        else:
                            message3 = lines[0][40:]  # add the remaining characters to the last line
                    else:
                        message2 = lines[0][20:]  # add the remaining characters to the last line
                else:
                    message1 = lines[0]  # set the first line if it's less than or equal to 20 characters
            if len(lines) > 1:
                message3 = lines[1][:20]  # truncate second line to 20 characters
                if len(lines[1]) > 20:
                    message4 = lines[1][20:]  # add the remaining characters to the last line

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
            message4 = ''
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
