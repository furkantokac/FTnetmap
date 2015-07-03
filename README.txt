FTnetmap Version 0.5

BUGS:
No reported.

UNDER DEVELOPMENT:
-Will show more details about host.

CURRENT FEATURES:
-Search alive hosts between 2 IPs.
-Cross-Platform.
-Export IPs to file.
-Fast.

COMING FEATURES:
-Will show more details about host.
-Will use socket for new, advanced features.

MANUEL:
Usage: python FTnetmap.py -e fileName.txt -i firstIP-lastIP
This command scan alive IP's between firstIP and lastIP and export IPs to fileName.txt

-i --interval - IP interval that will be checked.
-d --detailed - See all details during process (May be unordered).
-h --help     - Help
-e --export   - Write alive hosts to file.

Examples:
python FTnetmap.py -i 192.168.1.0-192.168.2.0
python FTnetmap.py -d -i 192.168.1.0-192.168.1.255
python FTnetmap.py -e fileName.txt -i 192.168.1.0-192.168.1.255
