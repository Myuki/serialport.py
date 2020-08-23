#!/usr/bin/env python3

import serial
import serial.tools.list_ports
import sys
import threading
import time

from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from typing import Any

# Get serial port name
def getComList():
  try:
    portList: list = list(serial.tools.list_ports.comports())
    portComList: list = []
    for port in portList:
      portComList.append(port[0])
    return portComList
  except Exception as e:
    print(e)

# Receive data from serial port in independent thread
def receiveDataThread(serialPort: serial.Serial, receiveDataText: ScrolledText):
  print("Receive thread start")
  while True:
    if serialPort.is_open:
      try:
        readData = serialPort.readall()
        if len(readData) > 0:
          print(bytes(readData).decode("utf-8"))
          receiveDataText.insert(END, bytes(readData).decode("utf-8"))
      except Exception as e:
        print(e)
        time.sleep(1)
    else:
      print("Port is closed, receive thread exit")
      sys.exit(1)

# Show messagebox in independent thread
def showMessage(title: str, message: str):
  thread = threading.Thread(target=messagebox.showinfo, args=(title, message))
  thread.start()

if __name__ == "__main__":
  # Init serialPort object
  serialPort = serial.Serial()
  serialPort.timeout = 0.5

  # Init GUI
  root = Tk()
  root.title("serialport.py")
  windowWidth = 500
  windowHeight = 370

  # Receive Text
  receiveDataText = ScrolledText(root, width=43, height=16)
  receiveDataText.grid(row=0, column=0, rowspan=7)

  settingsLabel: Label = Label(root, text="Settings").grid(column=1, row=0, columnspan=2)
  # Port COM
  comLabel: Label = Label(root, text="Port").grid(column=1, row=1)
  comCombo = ttk.Combobox(root, state="readonly", width=8)
  comCombo.grid(column=2, row=1)
  # Get and check port com list
  portComList = getComList()
  if len(portComList) > 0:
    comCombo["values"] = portComList
    comCombo.current(0)
  else:
    showMessage(title="Message", message="No port detected")

  # Speed
  speedLabel: Label = Label(root, text="Speed").grid(column=1, row=2)
  speedCombo = ttk.Combobox(root, state="readonly", width=8)
  speedCombo.grid(column=2, row=2)
  speedCombo["values"] = ("9600", "19200", "38400", "115200")
  speedCombo.current(0)

  # Data Bits
  dateBitsLabel: Label = Label(root, text="Data Bits").grid(column=1, row=3)
  dataBitsCombo = ttk.Combobox(root, state="readonly", width=8)
  dataBitsCombo.grid(column=2, row=3)
  dataBitsCombo["values"] = ("8", "7", "6", "5")
  dataBitsCombo.current(0)

  # Stop Bits
  stopBitsLabel: Label = Label(root, text="Stop Bits").grid(column=1, row=4)
  stopBitsCombo = ttk.Combobox(root, state="readonly", width=8)
  stopBitsCombo.grid(column=2, row=4)
  stopBitsCombo["values"] = ("1", "1.5", "2")
  stopBitsCombo.current(0)

  # Parity Bits
  parityLabel: Label = Label(root, text="Parity Bits").grid(column=1, row=5)
  parityCombo = ttk.Combobox(root, state="readonly", width=8)
  parityCombo.grid(column=2, row=5)
  parityCombo["values"] = ("N", "O", "E")
  parityCombo.current(0)

  # Data Format Button
  dataFormatLabel: Label = Label(root, text="Format").grid(column=1, row=6)
  dataFormatCombo = ttk.Combobox(root, state="readonly", width=8)
  dataFormatCombo.grid(column=2, row=6)
  dataFormatCombo["values"] = ("ASCII", "UTF-8", "Hex")
  dataFormatCombo.current(0)

  operationLabel: Label = Label(root, text="Send").grid(column=0, row=7, columnspan=2)

  # Send Text Input
  sendText = Text(root, width=45, height=5)
  sendText.grid(row=8, column=0, rowspan=2)

  # Open/Close Button
  operateButtonText = StringVar()
  operateButtonText.set("Open Port")
  operateButton = Button(root, textvariable=operateButtonText, width=9)
  operateButton.grid(column=1, row=8, columnspan=2)

  def operateButtonListener():
    # Check and set port
    serialPort.port = comCombo.get()
    if serialPort.port == None:
      showMessage(title="Message", message="No port")
      return
    serialPort.baudrate = int(speedCombo.get())
    serialPort.bytesize = int(dataBitsCombo.get())
    serialPort.stopbits = float(stopBitsCombo.get())
    serialPort.parity = parityCombo.get()
    # Open port
    if operateButton["text"] == "Open Port":
      if serialPort.is_open:
        showMessage(title="Message", message="Port is opened")
      else:
        try:
          print("Open", serialPort.port)
          serialPort.open()
          if serialPort.is_open:
            operateButtonText.set("Close Port")
            receiveDataText.insert(INSERT, "--- Port has been opend ---\n")
            receiveThread = threading.Thread(target=receiveDataThread, args=(serialPort, receiveDataText))
            receiveThread.start()
        except Exception as e:
          print(e)
    # Close port
    elif operateButton["text"] == "Close Port":
      if not serialPort.is_open:
        showMessage(title="Message", message="Port is closed")
      else:
        try:
          print("Close", serialPort.port)
          serialPort.close()
          if not serialPort.is_open:
            operateButtonText.set("Open Port")
            receiveDataText.insert(INSERT, "--- Port has been closed ---\n")
        except Exception as e:
          print(e)

  operateButton.bind("<Button-1>", lambda event: operateButtonListener())

  # Send Button
  sendButton = Button(root, text="Send", width=9, height=1)
  sendButton.grid(column=1, row=9, columnspan=2)

  # Send text
  def sendButtonListener():
    text: str = sendText.get(0.0, END)
    if not serialPort.is_open:
      print("Port is closed")
    else:
      try:
        if dataFormatCombo.get() == "ASCII":
          serialPort.write(text.encode("ascii"))
        if dataFormatCombo.get() == "UTF-8":
          serialPort.write(text.encode("utf-8"))
        if dataFormatCombo.get() == "Hex":
          # Remove 0x(0X) at the beginning of text
          if text.startswith("0x"):
            text.replace("0x", "", 1)
          if text.startswith("0X"):
            text.replace("0X", "", 1)
          # Add a 0 at the beginning of text which have odd characters
          if (len(text) % 2) == 1:
            text = "0" + text
          serialPort.write(bytes.fromhex(text))
        sendText.delete(0.0, END)
      except Exception as e:
        print(e)

  sendButton.bind("<Button-1>", lambda event: sendButtonListener())

  # Set size and center window
  screenWidth: int = root.winfo_screenwidth()
  screenHeight: int = root.winfo_screenheight()
  size = "%dx%d+%d+%d" % (windowWidth, windowHeight, (screenWidth - windowWidth) / 2, (screenHeight - windowHeight) / 2)
  root.geometry(size)
  root.resizable(width=False, height=False)

  root.mainloop()

  # Close port after close window
  if serialPort.is_open:
    serialPort.close()
