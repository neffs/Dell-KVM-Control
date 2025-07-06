# Dell-KVM-Control

I use multiple inputs of my Dell U3419W display and wanted a way to quickly switch between these inputs, without a Windows PC with Dell Display Manager.

This code uses (like Dell Display Manager) the Display Data Channel (DDC), a I2C based channel between PC and display.

* RP2040 Board
* I2C Level Converter to HDMI DDC PINs
* 5 Buttons:
** 3 Inputs
** PBP
** Switch USB between PBP inputs
* Display for current input and Volume
