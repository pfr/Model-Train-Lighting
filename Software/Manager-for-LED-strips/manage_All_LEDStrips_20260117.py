import socket
import time

numSegments = 63   # This changes with different strips


# hosts are ["192.168.5.237", "192.168.5.238", "192.168.5.239", "192.168.5.240"]]
port = 12345
strips=[["Projection_large","240", "0", "RGBIC"], ["Projection_bay", "237", "1", "WhYe"],\
        ["Projection_doorway", "238", "0", "WhYe"], ["Yards_front","237", "0","WhYe"],\
        ["Yards_back","237", "2", "WhYe"], ["Bay_Wharf", "238", "1", "WhYe"],["Hopewell", "238", "2", "WhYe"]]

colors=[["red", "0,16,0"], ["green", "16,0,0"], ["blue", "0,0,16"], ["yellow", "16,16,0"],\
        ["salmon", "8, 16, 5"], ["cyan", "16,0,16"], ["cool white", "16,16,16"], ["warm white", "16,16,4"],
        ["black", "0,0,0"]]


remap= [[2,1,0,3],[1,2,3,0]]  ## For the RGBWh strip to remap colors to positions

leaveNow = False
while not leaveNow:
    iwhich = 99 
    while not iwhich in range(len(strips)):
        try:
            print("\n* * * * *")
            for i in range(len(strips)):
                print(str(i) + ':   ' + str(strips[i][0]))
            iwhich = int(input("\nSelect an LED strip to control: "))
        except:
#            iwhich = 99
            print("!!! Please enter numeric value! ")

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   
#    s.settimeout(25)
    proceed = True
    try:
        addr = ("192.168.5." + strips[iwhich][1])
        s.connect((addr, port))
        print(f"Connection successful to {addr}:{port}")
    except socket.error as e:
        print(f"Connection failed to {addr}:{port}: {e}")
        s.close()
        proceed = False
    if proceed:
        if strips[iwhich][3] == "WhYe":
            white = '99'
            while not (white.isnumeric() and int(white) in range(10)):
                white = input(" Provide intensity for white (0..9): ").lstrip().rstrip()
            yellow = '99'
            while not (yellow.isnumeric() and int(yellow) in range(10)):
                yellow = input(" Provide intensity for yellow (0..9): ").lstrip().rstrip()
            toSend = strips[iwhich][2] +"," + white + "," + yellow

        elif strips[iwhich][3] == "RGB" or strips[iwhich][3] == "RGBW":  
            red = ''
            while not (red.isnumeric() and int(red) in range(10)):
                red = input(" Provide intensity for red (0..9): ").lstrip().rstrip()
            green = ''
            while not (green.isnumeric() and int(green) in range(10)):
                green = input(" Provide intensity for green (0..9): ").lstrip().rstrip()
            blue = ''
            while not (blue.isnumeric() and int(blue) in range(10)):
                blue = input(" Provide intensity for blue (0..9): ").lstrip().rstrip()
            toSend = strips[iwhich][2] +"," + red +',' + green + "," + blue
            if strips[iwhich][3] == "RGBW":
                if red == "0" and green == "0" and blue == "0":           
                    white = ''
                    while not (white.isnumeric() and int(white) in range(10)):
                        white = input(" Provide intensity for white (0..9): ").lstrip().rstrip()
                else:
                    white = "0"
                toSend = toSend + "," + white
     
        elif strips[iwhich][3] == "RGBIC":
            choice = 99
            while not choice in range(len(colors)+1):
                try:
                    print("\n - - - - ")
                    for i in range(len(colors)):
                        print(str(i) + ':   ' + str(colors[i][0]))
                    print(str(len(colors)) + ':   custom')
                    choice = int(input("\nSelect a color or custom: "))
                except:
                    print("!!! Please enter numeric value! ")
            
            firstSegment = '900'
            while not (firstSegment.isnumeric() and int(firstSegment) in range(numSegments)):
                firstSegment = input(" Provide beginning segment ([0].." + str(numSegments-1) + "): ").lstrip().rstrip()
                if firstSegment == '':
                    firstSegment = '0'
            endSegment = '900'
            while not (endSegment.isnumeric() and int(firstSegment) <= int(endSegment) < numSegments):
                endSegment = input(" Provide ending segment (0..[" + str(numSegments-1) + "]): ").lstrip().rstrip()
                if endSegment == '':
                    endSegment = str(numSegments-1)
                
            toSend = firstSegment + ',' + endSegment + ','
            if choice == len(colors):   # User chose custom
                
                red = ''
                while not (red.isnumeric() and int(red) in range(256)):
                    red = input(" Provide intensity for red (0..255): ").lstrip().rstrip()
                green = ''
                while not (green.isnumeric() and int(green) in range(256)):
                    green = input(" Provide intensity for green (0..255): ").lstrip().rstrip()
                blue = ''
                while not (blue.isnumeric() and int(blue) in range(256)):
                    blue = input(" Provide intensity for blue (0..255): ").lstrip().rstrip()
                toSend = toSend + green + "," +red + "," +  blue
            else:
                toSend = toSend + colors[choice][1]

        else:
            toSend = ''
            print("Unrecognized strip type: ", strips[iwhich][3] + '\n')
            
        if toSend:
            print("sendng: " + toSend)
            s.sendall(bytes(toSend.encode("utf-8")))        
            response = s.recv(1024).decode("utf-8")
            print(f"Received {response!r}")
#    print("Im closing socket")
    s.close()




