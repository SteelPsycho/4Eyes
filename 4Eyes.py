import scapy.all as scapy
import nmap
import socket
import os
import subprocess
import re


from scapy.layers.l2 import ARP
import pprint


def scan(ip):
    arpReq = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")

    arpReqBroad = broadcast / arpReq
    answeredList = scapy.srp(arpReqBroad, timeout=1, verbose=False)[0]

    results = []

    for i in answeredList:
        clientDict = {"ip": i[1].psrc, "mac": i[1].hwsrc}
        results.append(clientDict)
    return results


def display(results):

    count = 1
    for i in results:
        print("Entry: "+{count})
        print("IP: " + i["ip"] + "\t||\t MAC: " + i["mac"])
        count += count


def hostScan(ip):
    print("Host Scanning Started")
    nm = nmap.PortScanner()
    try:
        nm.scan(hosts=ip, arguments='-n -sP -PE -PA21,23,80,3389')
        hosts_list = [(x, nm[x]['status']['state'], socket.gethostbyaddr(x)[0]) for x in nm.all_hosts()]
        for host, status, name in hosts_list:
            print("{}\t{}\t{}".format(host, status, name))
    except:
        print("ERROR - Glasses Fogged Up")


def nmapPortRun(start, end):
    target = '127.0.0.1'
    nm = nmap.PortScanner()
    if end - start > 10:
        print()
        if input("Large range scanning, continue? y/n: ") == "y":
            for i in range(start, end + 1):
                res = nm.scan(target, str(i))
                res = res['scan'][target]['tcp'][i]['state']
                print(f'port: {i}\tstate: {res}')
    else:
        for i in range(start, end + 1):
            res = nm.scan(target, str(i))
            res = res['scan'][target]['tcp'][i]['state']
            print(f'port: {i}\tstate: {res}')


def arp(inIP):
    command = "arp -a -N " + inIP
    interfaces = input("all interfaces (y/n)?")
    if interfaces == "y":
        command = "arp -a"
    else:
        command = "arp -a -N " + inIP
    result = subprocess.check_output(command, shell=True, text=True)
    ip_pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
    IPs = re.findall(ip_pattern, result)
    print(IPs)
    names = input("Do you want Names (y/n)? ")
    if names == "y":
        for ip in IPs:
            print(os_scan_light(ip))
    else:
        print(result)


def os_scan_light(ip):
    #THis is only used by the arp process to get hostnames
    nm = nmap.PortScanner()
    results = nm.scan(ip, arguments='-O')
    if not results:
        name = "N/A"
    elif 'scan' not in results or ip not in results['scan'] or 'hostnames' not in results['scan'][ip] or not \
            results['scan'][ip]['hostnames']:
        name = "N/A"
    else:
        name = results['scan'][ip]['hostnames'][0]['name'] if results['scan'][ip]['hostnames'][0]['name'] else "N/A"

    result_tuple = (ip, name)
    return result_tuple


def os_scan(ip):
    print("OS Scanning\n")
    nm = nmap.PortScanner()
    results = nm.scan(ip, arguments='-O', timeout=10)

    print(results)
    print(results.keys())
    print("Enter a single key, several separated by a space, or Exit")
    key = "test"
    justkeys = 0
    while (True):
        currentDir = []

        key = input("-0_0: ")
        if '-jk' in key:
            key.replace('-jk', '')
            justkeys = 1
        else:
            justkeys = 0
        if (key == 'keylist'):
            print(results.keys())
        elif key == ('exit'):
            break
        elif ' ' in key:
            for i in key.split(' '):
                currentDir.append(i)
        else:
            currentDir.append(key)
            getPath(results, currentDir, justkeys)

    #if 'osclass' in nm[ip]:
    #    for osclass in nm[ip]['osclass']:
    #        print('OsClass.type : {0}'.format(osclass['type']))
    #        print('OsClass.vendor : {0}'.format(osclass['vendor']))
    #        print('OsClass.osfamily : {0}'.format(osclass['osfamily']))
    #        print('OsClass.osgen : {0}'.format(osclass['osgen']))
    #        print('OsClass.accuracy : {0}'.format(osclass['accuracy']))
    #        print('')


def getPath(dict, path, justkeys):
    current = dict
    for i in path:
        if i in current:
            current = current[i]
        else:
            print("Path Wrong")
    if justkeys == 1:
        print(dict.keys())
    else:
        pprint.pprint(current)


def tcpsyn(port):
    nm = nmap.PortScanner()
    nm.scan(port, arguments='-sS')
    #print(".scan")
    for host in nm.all_hosts():
        for proto in nm[host].all_protocols():
            lport = nm[host][proto].keys()
            for port in lport:
                if nm[host][proto][port]['state'] == 'open':
                    print('Port: %s/%s' % (port, proto))


def main():
    # Create a socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Connect to some address to get the local IP address associated with it
    s.connect(("8.8.8.8", 80))
    # Get the local IP address
    local_ip = s.getsockname()[0]
    # Close the socket

    # Close the socket
    s.close()

    print(f"Currently connected to IP: {local_ip}")
    print("Type help for list of commands OR enter command to begin")

    cmdList = {"netscan", "exit", "nmapport", "tcpsyn", "hostscan", "<cmd> help", "osscan", "arp"}
    stillWorking = {"netscan", "nmapport", "tcpsyn", "hostscan", "osscan", "arp"}
    helpMsgs = {"osscan": "Scan target IP for OS",
                "hostscan": "works with localhost but not network (on wustl wifi), Scans for hosts connected to network",
                "exit": "exit the program", "netscan": "lists IP addresses on network I think",
                "tcpsyn": "list open ports and protocols on destination IP addresses"}
    while True:
        inputCmd = input("-O_O: ")
        if len(inputCmd.split()) > 1:
            if "help" in inputCmd.split():
                if inputCmd.split()[0] in helpMsgs:
                    print(helpMsgs[inputCmd.split()[0]])
                else:
                    print("no help for this command")

        if inputCmd == "exit":
            exit(0)
        if inputCmd == "help":
            print("Commands:")
            for i in cmdList:
                if i in stillWorking:
                    print('\t' + i + " - Unstable" + '\n')
                else:
                    print('\t' + i + '\n')
        if inputCmd == "netscan":
            ip = input("IP: ")
            try:
                display(scan(ip))
            except:
                print("ERROR - Glasses Fogged Up")
        if inputCmd == "nmapport":
            try:
                nmapStart = int(input("Nmap start port: "))
                nmapEnd = int(input("Nmap end port: "))
                nmapPortRun(nmapStart, nmapEnd)
            except:
                print("ERROR - Glasses Fogged Up")
        if inputCmd == "tcpsyn":
            try:
                inputU = input("TCP SYN Dest IP: ")
                tcpsyn(inputU)
            except:
                print("ERROR - Glasses Fogged Up")
        if inputCmd == "hostscan":
            try:
                ip = input("IP: ")
                hostScan(ip)
            except:
                print("ERROR - Glasses Fogged Up")
        if inputCmd == "arp":
            try:
                arp(local_ip)
            except Exception as e:
                print("ERROR - Glasses Fogged Up:", str(e))
        if inputCmd == "osscan":
            try:
                os_ip = input("IP to scan: ")
                os_scan(os_ip)
            except:
                print("ERROR - Glasses Fogged Up")


main()
