import scapy.all as scapy
import argparse
import ipaddress
import socket
import time
import threading
from tabulate import tabulate


def parse_and_validate_cmd():
    parser = argparse.ArgumentParser(description='Scan a network for open ports.')
    parser.add_argument('-t', '--target', required=True, help='The target IP address(es).')
    parser.add_argument('-p', '--port', help='The target port or port range.')

    args = parser.parse_args()

    try:
        target = ipaddress.ip_address(args.target)
        print(f"Valid IP address: {target}")
    except ValueError:
        try:
            targets = ipaddress.ip_network(args.target, strict=False)
            print("Valid IP address range.")
        except ValueError:
            print("Invalid IP address or range")
            return None

    try:
        port = int(args.port)
        print(f"Valid port: {port}")
        return target, port
    except ValueError:
        try:
            port_range = args.port.split('-')
            start_port = int(port_range[0])
            end_port = int(port_range[1])
            print(f"Valid port range: {start_port}-{end_port}")
            return target, range(start_port, end_port + 1)
        except (ValueError, IndexError):
            print("Invalid port or port range")
            return None


def scan_port(ip_address, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)

    try:
        # Make the connection to the ip & port
        result = sock.connect_ex((str(ip_address), port))

        # Output the connection results
        if result == 0:
            print(f"Port {port} is open on {ip_address}")
        else:
            print(f"Port {port} is closed on {ip_address}")

    except socket.error:
        print(f"Error for port {port} on {ip_address}")

    finally:
        sock.close()


def subports(ports, num_sublists):
    # Divide the ports into a specified number of subports
    sublist_size = (len(ports) + num_sublists - 1) // num_sublists
    return [ports[i:i + sublist_size] for i in range(0, len(ports), sublist_size)]


is_single = False


def scan(ip_address, ports, table, num_threads):
    threads = []
    global is_single

    # Scan for single port
    if isinstance(ports, int):
        is_single = True
        tcp_port_scan(ip_address, ports, table)

    # Scan for a range of ports
    elif isinstance(ports, range):
        port_list = list(ports)
        # Divide the port list into subports
        port_sublist = subports(port_list, num_threads)
        # Scan each subports of ports
        for port_sublist in port_sublist:
            for port in port_sublist:
                thread = threading.Thread(target=tcp_port_scan, args=(ip_address, port, table))
                thread.start()
                threads.append(thread)

        for thread in threads:
            thread.join()
    else:
        print("Invalid port or port range")


def tcp_port_scan(ip_address, port, table):
    try:
        # Craft SYN packet
        syn_packet = scapy.IP(dst=str(ip_address)) / scapy.TCP(dport=port, flags="S")

        # Send SYN packet and receive response
        syn_ack_response = scapy.sr1(syn_packet, timeout=2, verbose=False)

        # Check if SYN-ACK received
        if syn_ack_response and syn_ack_response.haslayer(scapy.TCP) and syn_ack_response.getlayer(
                scapy.TCP).flags == 0x12:
            # Craft ACK packet
            ack_packet = scapy.IP(dst=str(ip_address)) / scapy.TCP(dport=port, flags="A",
                                                                   ack=syn_ack_response[scapy.TCP].seq + 1)

            # Send ACK packet
            scapy.send(ack_packet, verbose=False)

            # Print open port information
            print(f"Port {port} is open on {ip_address}")

            # Uncomment to show detailed packet
            '''
            # Show SYN packet response details
            print("SYN packet response:")
            syn_ack_response.show()

            # Show ACK packet details
            print(f"ACK packet:")
            ack_packet.show()
            '''

            # Table with results
            table.append([ip_address, port, 'Open'])
            return table

        else:
            print(f"Port {port} is closed on {ip_address}")

            if is_single:
                # Table with results
                table.append([ip_address, port, 'Closed'])
                return table

            # Uncomment to show detailed packet
            '''
            # Show SYN packet response details
            print("SYN packet response:")
            syn_ack_response.show()
            '''

    except Exception as e:
        print(f"Error occurred while scanning port {port} on {ip_address}: {str(e)}")


if __name__ == '__main__':
    table = []
    targets, ports = parse_and_validate_cmd()

    if isinstance(ports, range):
        port_max = list(ports)
        headers = ["IP", f"Port/{port_max[-1]}", "Status"]
    else:
        port_max = ports
        headers = ["IP", f"Port/{port_max}", "Status"]

    startTime = time.time()
    if targets is not None and ports is not None:
        scan(targets, ports, table, 4)
    endTime = time.time()

    print(tabulate(table, headers, tablefmt="grid"))
    print(f"Execution time: {round((endTime - startTime), 4)} seconds.")
