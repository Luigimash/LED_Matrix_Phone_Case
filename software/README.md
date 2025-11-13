# LED Matrix Phone Case Software

This is the software used to control my LED matrix phone case, which is a 28 row 20 column LED display. It's connected to various GPIO pins on my STM32WB55RGV6 microcontroller. 

This software will hopefully allow me to upload photos and short videos/gifs/animations, turn them into 28x20 grayscale bitmap image sequences, and then play the static images or animations back on the display. 

For now, we're focusing on code that doesn't actually live on the microcontroller. The ideal flow is that the microcontroller only receives the end result animation, and doesn't do any of the computation for crunching images/video etc into the 28x20 format. That should be handled by another device, such as a phone or a laptop. The software written here will be used on said phone or laptop (most likely a phone as I will be turning it into a phone app at some point)

# Software/Hardware Stack
Microcontroller will be connected to phone via Bluetooth. We want to upload a sequence of data representing an animation (sequence of frames) that fit on the 28x80 display, probably as an 8 bit grayscale bitmap, to the microcontroller. 

User should have some sort of interface with which to upload photos/short videos/gifs, do basic manipulation (resize and crop), and then we handle the conversion to bitmap and upload to device. 

We're going to build this for iOS first, probably using a native iOS Swift stack. 
- AVFoundation for loading and decoding video and gif into a sequence of frames
- UIKit / SwiftUI for file picker 
- Core Image to do grayscale and basic image color transforms
- Core Graphics for resizing, cropping, byte array conversion 
- CoreBluetooth 


Before building for iOS though, we should probably prove out the uploading byte array pipeline on a PC first where it'll be easier to debug and troubleshoot. For this, we would have to:
1. Build all the MCU code first and make it handle bluetooth communications 
2. Build an app (probably Python) with very basic API and GUI to allow generic upload of gifs and short videos, allow user to define the 28x20 bounding box over the image(s), convert it to byte array animation, then upload to the MCU (whose bluetooth connection hopefully works!)

In Python, tech stack can be something like:
- Pillow for image processing
- imageio (which is a python ffmpeg wrapper kind of) to extract frames for us to feed to Pillow
  - Alternatively just do FFMPEG calls directly 
- NumPy for array manipulation if needed
- PyQt6 or Tkinter for GUI 
- bleak for Bluetooth Low Energy handling

At the end of the day I don't think we need rock solid bulletproofing - if the user uploads a variable framerate video that's their fault and im not dealing with that, for example. If we have gifs and short videos working I'll be very happy