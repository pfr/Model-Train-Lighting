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
#    mac = ubinascii.hexlify(wlan.config('mac'),':').decode()
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

def processRequest(request):
    try:
        pieces = request.split(",")
    except IndexError:
        pass
    if len(pieces) == 5:
        try:
            lightSet = int(pieces[0])
            redDuty = DutyVals[int(pieces[1])]
            greenDuty = DutyVals[int(pieces[2])]
            blueDuty = DutyVals[int(pieces[3])]
            whiteDuty = DutyVals[int(pieces[4])]
            if lightSet == 0:
                pwmRed10.duty_u16(redDuty)
                pwmGreen11.duty_u16(greenDuty)
                pwmBlue12.duty_u16(blueDuty)
                pwmWhite13.duty_u16(whiteDuty)
            elif lightSet == 1:
                pwmRed18.duty_u16(redDuty)
                pwmGreen19.duty_u16(greenDuty)
                pwmBlue20.duty_u16(blueDuty)
                pwmWhite21.duty_u16(whiteDuty)
            elif lightSet == 9:
                # Turn off all strips
                pwmRed10.duty_u16(0)
                pwmGreen11.duty_u16(0)
                pwmBlue12.duty_u16(0)
                pwmWhite13.duty_u16(0)
                pwmRed18.duty_u16(0)
                pwmGreen19.duty_u16(0)
                pwmBlue20.duty_u16(0)
                pwmWhite21.duty_u16(0)
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
    pwmRed10 = PWM(Pin(10))
    pwmRed10.freq(1000)
    pwmRed10.duty_u16(0)
    pwmGreen11 = PWM(Pin(11))
    pwmGreen11.freq(1000)
    pwmGreen11.duty_u16(0)    
    pwmBlue12 = PWM(Pin(12))
    pwmBlue12.freq(1000)
    pwmBlue12.duty_u16(0)
    pwmWhite13 = PWM(Pin(13))
    pwmWhite13.freq(1000)
    pwmWhite13.duty_u16(0)
    
    pwmRed18 = PWM(Pin(18))
    pwmRed18.freq(1000)
    pwmRed18.duty_u16(0)
    pwmGreen19 = PWM(Pin(19))
    pwmGreen19.freq(1000)
    pwmGreen19.duty_u16(0)    
    pwmBlue20 = PWM(Pin(20))
    pwmBlue20.freq(1000)
    pwmBlue20.duty_u16(0)    
    pwmWhite21 = PWM(Pin(21))
    pwmWhite21.freq(1000)
    pwmWhite21.duty_u16(0)
    
    
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

