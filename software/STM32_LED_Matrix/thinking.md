This folder will be where the firmware uploaded to the STM32 LED matrix lives. Remember we have one megabyte of flash memory, and that the code you generate could take somewhere between 20-80kb.

I think high level interaction flow is: 
1. From iOS/bluetooth app, generate a series of bitmap images for each frame in the animation, each 20x28 arrays of 8 bits (0-256 values of brightness), meaning one frame is 560 bytes. Upon initial data transfer, probably first seek alignment on the number of frames being transmitted.
  - during transfer, we should do hash checking after each frame is transmitted to ensure data validity - BLE is pretty finnicky I imagine
2. Microcontroller stores the large arrays in flash memory 
3. Microcontroller runs a compilation process - we need to convert the 20x28 frames into a long list of register DMA r/w. The problem here is that turning on one LED is two bytes (toggling A and C GPIO registers), and we want multiple stops of brightness so we can't just generate a single 1.12kb array for the frame and then run through that as fast as possible, else we would get uniform brightness; so we need to generate an appropriate number of brightness stops. 

The main limiter here would be the number of frames and the resolution of brightness stops. If we had 10 different brightness stops, we would hypothetically need 11.2kb for one frame, and then for a 12fps 5 second animation, we'd have 60 frames and thus take up 672kb. It adds up fast! 

The alternative (and we would have to experiment if this would even work) is, for every frame, to deal with brightness stops on the fly. We have 256kb of SRAM so we should be able to guarantee storing the *entire* animation inside (for a 12fps animation at 2 bytes per pixel, we could do up to 19 seconds), and then when displaying the frame, we could maintain full 256 stops of brightness by "turning off" pixels that are on after some number of display cycles according to their brightness level. So if we did 256 cycles of turning on and off every pixel in the display, and some pixel had a brightness of 200, we would turn off that pixel after 200 cycles, and then turn it back on at the start of the next 256 pixel cycle. 

But I'm not sure if doing r/w to flash memory like this will be responsive enough for our display. Moreover, this would *really* burn through the erase/write cycles (flash memory is typically rated for 10k-100k cycles). 

I think going with the "compiling into memory" approach, albeit limiting in terms of brightness stops, framerate and thus animation length, will be far more consistent, less computationally intensive at runtime, and won't burn out the flash memory. 

Actually maybe the best is some hybrid approach:
  - In compilation stage, store the list of "initial" BSRR and MODER register states for each frame, and a 2d integer array with a width equal to the number of brightness stops, where each brightness stop lists every pin number that corresponds to that expected brightness 
  -  At display runtime, load the register state arrays and the brightness array into SRAM
  - Count the number of display cycles (# of times we iterate through and turn on/off each pixel for the frame) using a clock or a counter, set some static period as a multiple of the resolution of brightness stops we want (maybe 256 cycle runs before counter resets, with 64 brightness stops, such that four LED cycles can pass before another round of LEDs are turned off)
  - Start pushing to the display. In a separate thread, compare the counter of LED display cycles to the brightness stops threshold. When the counter passes the # of cycles that some LEDs should be turned on, iterate through the array listing pixels of a certain brightness stop, and turn off the LEDs that should be off now. 
  - When we reach the end of the cycle's period, restore all of the LEDs to the "initial" BSRR and MODER state. 
  - When it's time to go to the next frame, instead of restoring the LEDs to the "initial" BSRR and MODER state, set them to the next frame's initial BSRR and MODER state. 

4. Do DMA memory transfer from the arrays of register MODER and BSRR into the appropriate registers on a recurring loop to drive the display 
