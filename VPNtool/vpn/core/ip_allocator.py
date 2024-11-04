import ipaddress
import heapq
import json
import os


class IPAllocator:
    def __init__(self, start_ip, end_ip, ip_pool_file, existing_allocations=None):
        self.start_ip = ipaddress.ip_address(start_ip)
        self.end_ip = ipaddress.ip_address(end_ip)
        self.issued_ips = set()
        self.released_ips = []
        self.ip_pool_file = ip_pool_file

        if os.path.exists(self.ip_pool_file):
            self.load_ip_pool()
        else:
            self.generate_ip_pool()
            self.save_ip_pool()

        # Add existing allocations to the issued IPs set
        if existing_allocations:
            for user, ips in existing_allocations.items():
                for ip_info in ips:
                    ip = ipaddress.ip_address(ip_info["ipAddress"])
                    self.issued_ips.add(ip)
                    # Ensure that released IPs do not include existing allocations
                    if ip in self.released_ips:
                        self.released_ips.remove(ip)

    def generate_ip_pool(self):
        self.ip_pool = []
        current_ip = self.start_ip
        while current_ip <= self.end_ip:
            self.ip_pool.append(current_ip)
            current_ip += 1
        self.ip_pool_iter = iter(self.ip_pool)

    def save_ip_pool(self):
        with open(self.ip_pool_file, "w") as file:
            json.dump([str(ip) for ip in self.ip_pool], file)

    def load_ip_pool(self):
        with open(self.ip_pool_file, "r") as file:
            self.ip_pool = [ipaddress.ip_address(ip) for ip in json.load(file)]
        self.ip_pool_iter = iter(self.ip_pool)

    def allocate_ip(self):
        if self.released_ips:
            # Allocate an IP address from the released pool if available
            ip = heapq.heappop(self.released_ips)
            self.issued_ips.add(ip)
            return str(ip)

        try:
            # Find the next available IP address from the main pool
            while True:
                ip = next(self.ip_pool_iter)
                if ip not in self.issued_ips:
                    self.issued_ips.add(ip)
                    return str(ip)
        except StopIteration:
            raise Exception(
                "No available IP addresses in the specified range.")

    def release_ip(self, ip):
        ip_obj = ipaddress.ip_address(ip)
        if ip_obj in self.issued_ips:
            self.issued_ips.remove(ip_obj)
            if self.start_ip <= ip_obj <= self.end_ip:
                heapq.heappush(self.released_ips, ip_obj)
        else:
            raise ValueError("IP address not found in issued list.")

    def list_issued_ips(self):
        return [str(ip) for ip in self.issued_ips]


def load_existing_allocations(json_file_path):
    try:
        with open(json_file_path, "r") as file:
            print(f"[*] Loaded existing clients configuration 📋")
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"[*] No existing clients configuration 📋")
        return {}
