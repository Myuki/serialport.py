#!/usr/bin/env python3

import serial
import sys
import threading
import time

from serial.tools import list_ports
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from typing import Any


# Get serial port name
def getComList():
  portComList: list = []
  try:
    portList: list = list(list_ports.comports())
    for port in portList:
      portComList.append(port[0])
  except Exception as e:
    print(e)
  return portComList


# Receive data from serial port in independent thread
def receiveDataThread(serialPort: serial.Serial, receiveDataText: ScrolledText):
  print("Receive thread start")
  while True:
    if serialPort.is_open:
      try:
        readData = serialPort.readall()
        if len(readData) > 0:
          receiveDataFormat: str = receiveDataFormatCombo.get()
          if receiveDataFormat == "UTF-8":
            receiveDataText.insert(END, bytes(readData).decode("utf-8"))
          if receiveDataFormat == "ASCII":
            receiveDataText.insert(END, bytes(readData).decode("ascii"))
          if receiveDataFormat == "Hex":
            receiveDataText.insert(END, bytes(readData).hex())
      except Exception as e:
        print(e)
    else:
      print("Port is closed, receiving thread exit")
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

  settingsLabel: Label = Label(
      root, text="Settings").grid(
          column=1, row=0, columnspan=2)

  # Send Data Format
  receiveDataFormatLabel: Label = Label(
      root, text="Format").grid(
          column=1, row=1)
  receiveDataFormatCombo = ttk.Combobox(root, state="readonly", width=8)
  receiveDataFormatCombo.grid(column=2, row=1)
  receiveDataFormatCombo["values"] = ("UTF-8", "ASCII", "Hex")
  receiveDataFormatCombo.current(0)
  receiveDataFormatCombo.bind("<<ComboboxSelected>>",
                              lambda event: changeSendDataFormat())

  def changeSendDataFormat():
    receiveDataFormat: str = receiveDataFormatCombo.get()
    if receiveDataFormat == "UTF-8":
      sendDataFormatCombo.current(0)
    if receiveDataFormat == "ASCII":
      sendDataFormatCombo.current(1)
    if receiveDataFormat == "Hex":
      sendDataFormatCombo.current(2)

  # Port COM
  comLabel: Label = Label(root, text="Port").grid(column=1, row=2)
  comCombo = ttk.Combobox(root, state="readonly", width=8)
  comCombo.grid(column=2, row=2)
  # Get and check port com list
  portComList = getComList()
  if len(portComList) > 0:
    comCombo["values"] = portComList
    comCombo.current(0)
  else:
    showMessage("Message", "No port detected")

  # Speed
  speedLabel: Label = Label(root, text="Speed").grid(column=1, row=3)
  speedCombo = ttk.Combobox(root, state="readonly", width=8)
  speedCombo.grid(column=2, row=3)
  speedCombo["values"] = ("9600", "19200", "38400", "115200")
  speedCombo.current(0)

  # Data Bits
  dateBitsLabel: Label = Label(root, text="Data Bits").grid(column=1, row=4)
  dataBitsCombo = ttk.Combobox(root, state="readonly", width=8)
  dataBitsCombo.grid(column=2, row=4)
  dataBitsCombo["values"] = ("8", "7", "6", "5")
  dataBitsCombo.current(0)

  # Stop Bits
  stopBitsLabel: Label = Label(root, text="Stop Bits").grid(column=1, row=5)
  stopBitsCombo = ttk.Combobox(root, state="readonly", width=8)
  stopBitsCombo.grid(column=2, row=5)
  stopBitsCombo["values"] = ("1", "1.5", "2")
  stopBitsCombo.current(0)

  # Parity Bits
  parityLabel: Label = Label(root, text="Parity Bits").grid(column=1, row=6)
  parityCombo = ttk.Combobox(root, state="readonly", width=8)
  parityCombo.grid(column=2, row=6)
  parityCombo["values"] = ("N", "O", "E")
  parityCombo.current(0)

  # Send Text Input
  sendLabel: Label = Label(root, text="Send Input").grid(column=0, row=7)
  sendText = Text(root, width=45, height=5)
  sendText.grid(row=8, column=0, rowspan=3)

  # Send Data Format
  sendDataFormatLabel: Label = Label(root, text="Format").grid(column=1, row=8)
  sendDataFormatCombo = ttk.Combobox(root, state="readonly", width=8)
  sendDataFormatCombo.grid(column=2, row=8)
  sendDataFormatCombo["values"] = ("UTF-8", "ASCII", "Hex")
  sendDataFormatCombo.current(0)

  # Open Button
  operateButtonText = StringVar()
  operateButtonText.set("Open Port")
  openButton = Button(root, textvariable=operateButtonText, width=9)
  openButton.grid(column=1, row=9, columnspan=2)
  openButton.bind("<Button-1>", lambda event: openPort())

  def openPort():
    # Check and set port
    serialPort.port = comCombo.get()
    if serialPort.port == "":
      showMessage("Error", "No port selected")
      return
    serialPort.baudrate = int(speedCombo.get())
    serialPort.bytesize = int(dataBitsCombo.get())
    serialPort.stopbits = float(stopBitsCombo.get())
    serialPort.parity = parityCombo.get()
    # Open port
    if openButton["text"] == "Open Port":
      if serialPort.is_open:
        showMessage("Error", "Port is opened")
      else:
        print("Open port", serialPort.port)
        try:
          serialPort.open()
          receiveDataText.insert(INSERT, "\n--- Port has been opened ---\n")
          receiveThread = threading.Thread(
              target=receiveDataThread, args=(serialPort, receiveDataText))
          receiveThread.start()
        except Exception as e:
          print(e)
    # Close port
    elif openButton["text"] == "Close Port":
      if not serialPort.is_open:
        showMessage("Message", "Port is closed")
      else:
        print("Close port", serialPort.port)
        try:
          serialPort.close()
          receiveDataText.insert(INSERT, "\n--- Port has been closed ---\n")
        except Exception as e:
          print(e)
    if serialPort.is_open:
      operateButtonText.set("Close Port")
    else:
      operateButtonText.set("Open Port")

  # Send Button
  sendButton = Button(root, text="Send", width=9, height=1)
  sendButton.grid(column=1, row=10, columnspan=2)
  sendButton.bind("<Button-1>", lambda event: sendData())

  def sendData():
    if not serialPort.is_open:
      showMessage("Error", "Port is closed")
    else:
      # Remove \n in the end
      text: str = sendText.get(0.0, END)[:-1]
      sendDataFormat: str = sendDataFormatCombo.get()
      try:
        if sendDataFormat == "UTF-8":
          serialPort.write(text.encode("utf-8"))
        if sendDataFormat == "ASCII":
          serialPort.write(text.encode("ascii"))
        if sendDataFormat == "Hex":
          # Remove 0x(0X) at the beginning of text
          if text.startswith("0x") or text.startswith("0X"):
            text = text[2:]
          # Add a 0 at the beginning of text which have odd characters
          if (len(text) % 2) == 1:
            text = "0" + text
          serialPort.write(bytes.fromhex(text))
        sendText.delete(0.0, END)
        receiveDataText.see(END)
      except Exception as e:
        print(e)

  # Set size and center window
  screenWidth: int = root.winfo_screenwidth()
  screenHeight: int = root.winfo_screenheight()
  size = "%dx%d+%d+%d" % (windowWidth, windowHeight,
                          (screenWidth - windowWidth) / 2,
                          (screenHeight - windowHeight) / 2)
  root.geometry(size)
  root.resizable(width=False, height=False)

  root.mainloop()

  # Close port after close window
  if serialPort.is_open:
    serialPort.close()
