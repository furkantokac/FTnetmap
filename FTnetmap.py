# Example   : python FTnetmap.py -i 192.168.0.0-192.168.2.0
# if you run like python FTnetmap.py, defaultly assing ip 192.168.0.0-192.168.2.0

import subprocess, sys, getopt, threading, time, platform

PLATFORM = platform.system()

detailed = False
aliveHosts = dict()
aliveHostsIds = list()
threadNumber = 0
fileName = ""

def usage():
    print "-___________FTnetmap Tool Guide___________-"
    print "Usage: python FTnetmap.py -e fileName.txt -i firstIP-lastIP"
    print "This command scan alive IP's between firstIP and lastIP and export IPs to fileName.txt"
    print ""
    print "-i --interval - IP interval that will be checked."
    print "-d --detailed - See all details during process (May be unordered)."
    print "-h --help     - Help"
    print "-e --export   - Write alive hosts to file."
    print ""
    print "Examples:"
    print "python FTnetmap.py -i 192.168.1.0-192.168.2.0"
    print "python FTnetmap.py -d -i 192.168.1.0-192.168.1.255"
    print "python FTnetmap.py -e fileName.txt -i 192.168.1.0-192.168.1.255"
    print ""
    sys.exit(0)
    
def main():
    global detailed
    global aliveHostsIds
    global fileName
    ip = ""
    print ""
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "i:dhe:", ["interval", "detail", "help", "export"])
    except getopt.GetoptError as err:
        print str(err)
        usage()
    
    for o,a in opts:
        if o in ("-i", "--interval"):
            ip = a
        elif o in ("-d", "--detail"):
            detailed = True
        elif o in ("-h", "--help"):
            usage()
        elif o in ("-e", "--export"):
            fileName = a
        else:
            assert False, "Unhandled Option"

    if ip is "":
        ip = "192.168.0.0-192.168.2.0"
        detailed = True
    
    if "-" in ip and len(ip.split(".")) == 7:
        ipRangeHandler(ip)
    else:
        print "ERROR: Please write IPs in correct format."
        usage()
    
    repeatCounter=0
    temp=0
    time.sleep(1)
    while threadNumber>0 and repeatCounter<5:
        if threadNumber is not temp:
            temp = threadNumber
        else:
            repeatCounter+=1
        time.sleep(1)
    
    aliveHostsIds.sort()
    printHosts()
    
def printHosts():
    global aliveHostsIds
    global aliveHosts
    global fileName
    
    print "\nAlive Hosts"
    for i in aliveHostsIds:
        print aliveHosts[i]
    print len(aliveHostsIds), "hosts are alive.\n"

    if fileName is not "":
        fileName = open(fileName, "w")
        for i in aliveHostsIds:
            fileName.write(aliveHosts[i]+"\n")
        fileName.close()

def ipRangeHandler(ip):
    global threadNumber
    
    ipfirst = (ip.split("-")[0]).split(".") # storage ip like ("192", "168", "1", "0")
    iplast  = (ip.split("-")[1]).split(".") # storage ip like ("192", "168", "2", "0")
    
    # Format checking. If format is ok, it will continue.
    for i in xrange(3):
        if iplast[i]=="":
            iplast[i]="0"
        elif int(iplast[i])>255:
            iplast[i]="255"
        elif int(iplast[i])<0:
            iplast[i]="0"
        if ipfirst[i]=="":
            ipfirst[i]="0"
        elif int(ipfirst[i])>255:
            ipfirst[i]="255"
        elif int(ipfirst[i])<0:
            ipfirst[i]="0"
    
    # String to integer
    ipfirst = map(int, ipfirst)
    iplast = map(int, iplast)
    
    # IPs changing in which line. Flag will keep line number.
    flag = 0
    for i in xrange(4):
        if iplast[i] != ipfirst[i]:
            if iplast[i] < ipfirst[i]:
                print "ERROR: First IP cannot be bigger than second IP."
                usage()
            flag = i
            break
    
    hostId = 0
    # Start main process
    while ipfirst is not iplast:
        currentIP = str(ipfirst[0]) + "." + str(ipfirst[1]) + "." + str(ipfirst[2]) + "." + str(ipfirst[3])
        threadNumber+=1
        while threadNumber > 100: # Maximum 100 thread can work at the same time
            time.sleep(1)
        ipThread = threading.Thread(target=pingIp, args=(currentIP,hostId,))
        ipThread.start()
        hostId+=1
        
        # This part makes accurate increment in ip ( Code will be improved )
        ipfirst[3] += 1
        if 3 == flag:
            if ipfirst[3] > iplast[3]:
                ipfirst[3] = iplast[3]
                break
        elif ipfirst[3] > 255:
            ipfirst[3] = 0
            ipfirst[2] += 1
            if 2 == flag:
                if ipfirst[2] > iplast[2]:
                    flag+=1
                    ipfirst[2] = iplast[2]
                    ipfirst[3] = 1
            elif ipfirst[2] > 255:
                ipfirst[2] = 0
                ipfirst[1] += 1
                if 1 == flag:
                    if ipfirst[1] > iplast[1]:
                        flag+=1
                        ipfirst[1] = iplast[1]
                        ipfirst[2] = 1
                elif ipfirst[1] > 255:
                    ipfirst[1] = 0
                    ipfirst[0] += 1
                    if ipfirst[0] > iplast[0]:
                        flag+=1
                        ipfirst[0] = iplast[0]
                        ipfirst[1] = 1

# if ping successful, return 1 else return 0
def pingIp(ip, hostId):
    global aliveHosts
    global aliveHostsIds
    global threadNumber
    
    if PLATFORM == 'Linux':
        output = runCommand("ping -c 1 -w 1 "+ip)
    elif PLATFORM == 'Windows':
        output = runCommand("ping -n 1 -w 1000 "+ip)
    
    if "Failed" in output or "Unreachable" in output or "timed out" in output:
        threadNumber-=1
        return 0
    else:
        if detailed==True:
            print "%s %8s" % (ip, "ALIVE") 
        
        aliveHosts[hostId] = ip # This keeps IP's in dictionary
        aliveHostsIds.append(hostId) # This keeps just ID's which we assigned. This necessary to sort IP number for output
        threadNumber-=1 # One of the threads finished.
        return 1
    
def runCommand(command):
    command = command.rstrip()
    
    # Run the command and get output back
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except:
        output= "Failed to execute command.\n"
    
    return output

main()
raw_input("Please enter to exit...")
