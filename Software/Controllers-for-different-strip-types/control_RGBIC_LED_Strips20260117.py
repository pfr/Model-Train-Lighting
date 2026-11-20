from machine import Pin, Timer
import neopixel
from time import sleep
import network
import socket
import ubinascii
led = Pin("LED", Pin.OUT)

numberOfSegments = 63
strip = neopixel.NeoPixel(machine.Pin(27), numberOfSegments)

def connect():
    wlan = network.WLAN(network.STA_IF)
    mac = ubinascii.hexlify(wlan.config('mac'),':').decode()
#    print(mac)
    if not wlan.isconnected():
        wlan.active(True)
        sleep(2)
#        print(wlan.scan())
        wlan.config(pm = 0xa11140) # Disable power-saving for WiFi
        wlan.connect('YourSSID', 'YourPW')
        sleep(1)
        timeoutCount = 12
        while not wlan.isconnected() and timeoutCount >0:
#            print('.')
            timeoutCount -= 1
            sleep(1)
        if timeoutCount <= 0:
#            print('Giving up')
            machine.reset()
    ip = wlan.ifconfig()[0]
#    print(f'My IP: {ip}')
    return ip

def open_socket(ip):
    # Open a socket
    address = (ip, 12345)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
#    print('Connection is: ' + str(connection))
    return connection

def processRequest(request, theClient):
#    print("Process Request called")
    try:
        pieces = request.split(",")
    except:
        theClient.send("Input syntax error")
        return False
    if len(pieces) == 5:
        keepGoing = False
        try:
            keepGoing =  (0 <= int(pieces[0]) <= int(pieces[1]) < numberOfSegments and     # Check values/types
                0 <= int(pieces[2]) <= 255 and 0 <= int(pieces[3]) <= 255 and 0 <= int(pieces[4]) <= 255)
        except:
            theClient.send("Input type/range error")
            return False
        if keepGoing:
            # CONTROL LIGHT STRIP
            for i in range(int(pieces[0]), int(pieces[1])+1):  # Light segments # pieces[0] to pieces[1] inclusive
                strip[i] = (int(pieces[2]), int(pieces[3]), int(pieces[4]))
#            print("About to write to strip")
            strip.write()
            return True
        else:
            theClient.send("Input value range error(s)")
            return False
    else:
        theClient.send("Input length error")
        return False

def serve(connection):
    global led
    #Start a listener
    while True:
        sleep(1)
        try:
            client = connection.accept()[0]
            request = client.recv(1024)
            request = request.decode("utf-8").rstrip('\n\r')
            if processRequest(request, client):
                client.send(bytes("Command done".encode("utf-8")))
            else:
#                print("NACK")
                pass
            sleep(1)
        except:
#            print('Client closed connection.  Will renew accept.')
            pass
        client.close()

timer = Timer()

def blink(timer):
    led.toggle()


try:      
    ip = connect()
    connection = open_socket(ip)
    timer.init(freq=1.0, mode=Timer.PERIODIC, callback=blink)
    serve(connection)
except KeyboardInterrupt:
    try:
        connection.close()
    except:
        pass
    machine.reset()

