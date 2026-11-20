from machine import Pin, PWM, Timer
from time import sleep
import network
import socket
import ubinascii
led = Pin("LED", Pin.OUT)

#DutyVals = [0,6502, 13005, 19507, 26010, 32512, 39015, 45517, 52020, 60000]
DutyVals = [0,4000, 11000, 18000, 25000, 32000, 39000, 46000, 53000, 60000]

def connect():
    wlan = network.WLAN(network.STA_IF)
    mac = ubinascii.hexlify(wlan.config('mac'),':').decode()
    print(mac)
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
    print(f'My IP: {ip}')
    return ip

def open_socket(ip):
    # Open a socket
    address = (ip, 12345)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
#    print('Connection is: ' + str(connection))
    return connection

def processRequest(request):
    try:
        pieces = request.split(",")
    except IndexError:
        pass
    if len(pieces) == 3:
        try:
            lightSet = int(pieces[0])
            whiteduty = DutyVals[int(pieces[1])]
            yellowduty = DutyVals[int(pieces[2])]
            if lightSet == 0:
                pwmWhite10.duty_u16(whiteduty)
                pwmYellow18.duty_u16(yellowduty)
            elif lightSet == 1:
                pwmWhite11.duty_u16(whiteduty)
                pwmYellow19.duty_u16(yellowduty)
            elif lightSet == 2:
                pwmWhite12.duty_u16(whiteduty)
                pwmYellow20.duty_u16(yellowduty)
            elif lightSet == 9:
                # Turn off all strips
                pwmWhite10.duty_u16(whiteduty)
                pwmYellow18.duty_u16(yellowduty)
                pwmWhite11.duty_u16(whiteduty)
                pwmYellow19.duty_u16(yellowduty)
                pwmWhite12.duty_u16(whiteduty)
                pwmYellow20.duty_u16(yellowduty)
            else:
                return False
            return True
        except:
#            print("Subscripting issue")
            pass
        return False
    else:
#        print("Wrong length")
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
            if processRequest(request):
                client.send("ACK\n")
            else:
                client.send("NACK\n")
            client.close()
        except:
#            print('Client closed connection.  Will renew accept.')
            pass


timer = Timer()

def blink(timer):
    led.toggle()


try:
    pwmWhite10 = PWM(Pin(10))
    pwmYellow18 = PWM(Pin(18))
    pwmWhite10.freq(1000)
    pwmYellow18.freq(1000)
    pwmWhite10.duty_u16(0)
    pwmYellow18.duty_u16(0)
    
    pwmWhite11 = PWM(Pin(11))
    pwmYellow19 = PWM(Pin(19))
    pwmWhite11.freq(1000)
    pwmYellow19.freq(1000)
    pwmWhite11.duty_u16(0)
    pwmYellow19.duty_u16(0)    
    
    pwmWhite12 = PWM(Pin(12))
    pwmYellow20 = PWM(Pin(20))
    pwmWhite12.freq(1000)
    pwmYellow20.freq(1000)
    pwmWhite12.duty_u16(0)
    pwmYellow20.duty_u16(0)    
    
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

