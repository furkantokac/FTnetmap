# Example   : python FTnetmap.py -r 192.168.0.0-192.168.2.0
# if you run like python FTnetmap.py, defaultly assing ip 192.168.0.0-192.168.2.0

import subprocess, sys, argparse, threading, time, platform, socket

PLATFORM = platform.system()

verbose         = False
fileName        = ""
aliveHosts      = dict()
aliveHostsIds   = list()
threadNumber    = 0

def usage():
    print "-___________FTnetmap Tool Guide___________-"
    print "Usage: python FTnetmap.py -e fileName.txt -r firstIP-lastIP"
    print "This command scan IPs between firstIP & lastIP, export IPs to fileName.txt"
    print ""
    print "-r --range   - IP range that will be checked."
    print "-e --export  - Write alive hosts to file."
    print "-v --verbose - Deactive verbose mode."
    print "-h --help    - Help."
    print ""
    print "Examples:"
    print "python FTnetmap.py -r 192.168.1.0-192.168.2.0"
    print "python FTnetmap.py -v -r 192.168.1.0-192.168.1.255"
    print "python FTnetmap.py -e fileName.txt -r 192.168.1.0-192.168.1.255"
    print ""
    sys.exit(0)

def parse_arguments():
    
    parser = argparse.ArgumentParser(description="FTnetmap", add_help=False)
    parser.add_argument("-r", "--range",   dest="ip",       default="192.168.0.0-192.168.2.0", type=str)
    parser.add_argument("-e", "--export",  dest="fileName", default="", type=str)
    parser.add_argument("-v", "--verbose", dest="verbose",  default=True, action="store_false")
    parser.add_argument("-h", "--help",    dest="help",     default=False, action="store_true")
    
    return parser.parse_args()

def main():
    global verbose
    global aliveHostsIds
    global fileName
    ip = ""
    print ""
    
    parser = parse_arguments()
    if parser.help: usage()
    ip       = parser.ip
    verbose  = parser.verbose
    fileName = parser.fileName
    
    if "-" in ip and len(ip.split(".")) == 7:
        ipRangeHandler(ip)
    else:
        print "[!] ERROR: Please write IPs in correct format."
        usage()
    
    #Sleep till all threads finish
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
    global fileName
    
    print "\nAlive Hosts"
    if fileName is not "":
        fileName = open(fileName, "w")
        for i in aliveHostsIds:
            print "[+]", aliveHosts[i]
            fileName.write(aliveHosts[i]+"\n")
        fileName.close()
    else:
        for i in aliveHostsIds:
            print "[+]", aliveHosts[i]
    print len(aliveHostsIds), "hosts are alive.\n"

def ipRangeHandler(ip):
    global threadNumber
    
    ipfirst = (ip.split("-")[0]).split(".") # store ip like ("192", "168", "1", "0")
    iplast  = (ip.split("-")[1]).split(".") # store ip like ("192", "168", "2", "0")
    
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

    ipfirstint = convertIpInt(map(str, ipfirst))
    iplastint  = convertIpInt(map(str, iplast))
        
    if ipfirstint>=iplastint:
        print "[!] ERROR: First IP cannot be bigger or equal to last IP."
        usage()
        
    # String to integer
    ipfirst = map(int, ipfirst)
    iplast = map(int, iplast)
    
    # Scan info
    print "[+] IP range     : " + ip.split("-")[0]
    print "                   " + ip.split("-")[1]
    print "[+] Verbose mode : " + ("ON" if verbose else "OFF")
    print "[+] Export mode  : " + (fileName if fileName!="" else "OFF")
    print "[.] Scanning...\n"
    
    hostId = 0
    # Start main process
    ipfirstint = convertIpInt(map(str, ipfirst))
    iplastint  = convertIpInt(map(str, iplast))
    while iplastint > ipfirstint:
        currentIP = str(ipfirst[0]) + "." + str(ipfirst[1]) + "." + str(ipfirst[2]) + "." + str(ipfirst[3])
        threadNumber+=1
        while threadNumber > 255: # Maximum 255 thread can work at the same time
            time.sleep(1)
        ipThread = threading.Thread(target=pingIp, args=(currentIP,hostId,))
        ipThread.start()
        hostId+=1
        
        ipfirstint = convertIpInt(map(str, ipfirst))
        iplastint  = convertIpInt(map(str, iplast))
        
        # This part makes accurate increment in ip
        ipfirst[3] += 1
        if ipfirstint > iplastint:
            ipfirst = iplast
            break
        if ipfirst[3] > 255:
            ipfirst[3] = 0
            ipfirst[2] += 1
            if ipfirst[2] > 255:
                ipfirst[2] = 0
                ipfirst[1] += 1
                if ipfirst[1] > 255:
                    ipfirst[1] = 0
                    ipfirst[0] += 1

def convertIpInt(ip):
    return int(ip[0]+((3-len(ip[1]))*'0'+ip[1])+((3-len(ip[2]))*'0'+ip[2])+((3-len(ip[3]))*'0'+ip[3]))

# if ping successful, return 1 else return 0
def pingIp(ip, hostId):
    global aliveHosts
    global aliveHostsIds
    global threadNumber
    
    if PLATFORM == 'Linux':
        output = runCommand("ping -c 1 -w 1 "+ip)
    elif PLATFORM == 'Windows':
        output = runCommand("ping -n 1 -w 1000 "+ip)
    
    if  output == False or "Unreachable" in output or "timed out" in output:
        threadNumber-=1
        return 0
    else:
        if verbose:
            print "%s %8s" % (ip, "ALIVE")
            
        aliveHosts[hostId] = ip # This keeps IP's in dictionary
        aliveHostsIds.append(hostId) # This keeps just ID's which we assigned. This necessary to sort IP number for output
        threadNumber-=1 # One of the threads finished.
        return 1

def runCommand(command):
    command = command.rstrip()
    
    # Run the command and get output
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except:
        output = False
    
    return output

if __name__ == '__main__':
    main()
    raw_input("Please enter to exit...")
