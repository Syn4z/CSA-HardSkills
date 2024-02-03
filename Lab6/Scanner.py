import scapy.all as scapy
import argparse
import ipaddress
from socket import *
import time
from tabulate import tabulate
import threading


def parse_and_validate_cmd():
    parser = argparse.ArgumentParser(description='Scan a network for open ports.')
    parser.add_argument('-t', '--target', required=True, help='The target IP address(es).')

    args = parser.parse_args()

    try:
        target = ipaddress.ip_address(args.target)
        print(f"Valid IP address: {target}")
        return target
    except ValueError:
        try:
            targets = ipaddress.ip_network(args.target, strict=False)
            print("Valid IP address range.")
            return targets
        except ValueError:
            print("Invalid IP address or range")


def send_arp_request(target):
    arp_request = scapy.ARP(pdst=str(target))

    ether_frame = scapy.Ether(dst="ff:ff:ff:ff:ff:ff") / arp_request

    responses, unanswered = scapy.srp(ether_frame, timeout=2, verbose=False)
    return responses


def scan_single(target, results):

    responses = send_arp_request(target)

    results.extend(responses)


def scan_multithread(targets, num_threads):
    results = []
    threads = []

    if isinstance(targets, ipaddress.IPv4Address):
        thread = threading.Thread(target=scan_single, args=(targets, results))
        thread.start()
        threads.append(thread)

    elif isinstance(targets, ipaddress.IPv4Network):
        subnet = targets.subnets(num_threads)

        for subnet_ip in subnet:
            for ip in subnet_ip.hosts():
                thread = threading.Thread(target=scan_single, args=(ip, results))
                thread.start()
                threads.append(thread)

    else:
        print("Invalid IP address or range")

    for thread in threads:
        thread.join()

    return results


def print_results(results):
    table = []
    for sent_packet, received_packet in results:
        table.append([received_packet.psrc, received_packet.hwsrc])
    headers = ["IP", "MAC"]
    print(tabulate(table, headers, tablefmt="grid"))


if __name__ == '__main__':
    startTime = time.time()
    targets = parse_and_validate_cmd()
    result = scan_multithread(targets, num_threads=4)
    print_results(result)
    endTime = time.time()
    print(f"Execution time: {round((endTime - startTime), 4)} seconds.")
