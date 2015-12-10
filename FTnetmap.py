'''Example   : python FTnetmap.py -r 192.168.0.0-192.168.2.0
   if you run like python FTnetmap.py, defaultly assing ip 192.168.0.0-192.168.2.0
Functions
    usage()
    parse_arguments()
    main()
    start_scanning(ip)
    print_export_hosts()
    handle_ip_format(ip)
    ping_to_range(ipfirst, iplast)
    convert_ip_int(ip)
    ping_ip(ip, hostId)
    run_command(command)
'''

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
    
    start_scanning(ip)
    aliveHostsIds.sort()
    print_export_hosts()

def start_scanning(ip):
    
    ipfirst, iplast = handle_ip_format(ip)
    # Scan info
    print "[+] Verbose mode : " + ("ON" if verbose else "OFF")
    print "[+] Export mode  : " + (fileName if fileName!="" else "OFF")
    print "[+] IP range     : " + ip.split("-")[0]
    print "                   " + ip.split("-")[1]
    print "[.] Scanning..."
    ping_to_range(ipfirst,iplast)
    
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

def print_export_hosts():
    global fileName
    
    print "\n[+] Alive Hosts"
    if fileName!="":
        fileName = open(fileName, "w")
        for i in aliveHostsIds:
            print aliveHosts[i]
            fileName.write(aliveHosts[i]+"\n")
        fileName.close()
    else:
        for i in aliveHostsIds:
            print aliveHosts[i]
    print len(aliveHostsIds), "hosts are alive.\n"

def handle_ip_format(ip):
    if "-" not in ip or len(ip.split(".")) != 7:
        print "[!] ERROR: Please write IPs in correct format."
        usage()
    
    ipfirst = (ip.split("-")[0]).split(".") # store ip like ("192", "168", "1", "0")
    iplast  = (ip.split("-")[1]).split(".") # store ip like ("192", "168", "2", "0")
    
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

    ipfirstint = convert_ip_int(map(str, ipfirst))
    iplastint  = convert_ip_int(map(str, iplast))
        
    if ipfirstint>=iplastint:
        print "[!] ERROR: First IP cannot be bigger or equal to last IP."
        usage()
    
    return map(int, ipfirst), map(int, iplast)

def ping_to_range(ipfirst, iplast):
    global threadNumber
    
    hostId = 0
    # Start main process
    ipfirstint = convert_ip_int(map(str, ipfirst))
    iplastint  = convert_ip_int(map(str, iplast))
    while iplastint > ipfirstint:
        currentIP = str(ipfirst[0]) + "." + str(ipfirst[1]) + "." + str(ipfirst[2]) + "." + str(ipfirst[3])
        threadNumber+=1
        while threadNumber > 255: # Maximum 255 thread can work at the same time
            time.sleep(1)
        ipThread = threading.Thread(target=ping_ip, args=(currentIP,hostId,))
        ipThread.start()
        hostId+=1
        
        ipfirstint = convert_ip_int(map(str, ipfirst))
        iplastint  = convert_ip_int(map(str, iplast))
        
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

def convert_ip_int(ip):
    return int(ip[0]+((3-len(ip[1]))*'0'+ip[1])+((3-len(ip[2]))*'0'+ip[2])+((3-len(ip[3]))*'0'+ip[3]))

# if ping successful, return 1 else return 0
def ping_ip(ip, hostId):
    global aliveHosts
    global aliveHostsIds
    global threadNumber
    
    if PLATFORM == 'Linux':
        output = run_command("ping -c 1 -w 1.5 "+ip)
    elif PLATFORM == 'Windows':
        output = run_command("ping -n 1 -w 1500 "+ip)
    
    if  output == False or "Unreachable" in output or "timed out" in output:
        threadNumber-=1
        return 0
    else:
        if verbose:
            print "%s %8s" % (ip, "ALIVE")
        
        aliveHosts[hostId] = ip      # This keeps IPs in dictionary
        aliveHostsIds.append(hostId) # This keeps just IDs which we assigned. This necessary to sort IP number for output
        threadNumber-=1              # One of the threads finished.
        return 1

def run_command(command):
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
