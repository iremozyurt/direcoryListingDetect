
import dns.resolver
import dns.reversename
import pandas as pd
from tqdm import tqdm 
from ipaddress import ip_address  

def reverse_dns(ip):
    try:
        
        rev_name = dns.reversename.from_address(ip)

        
        resolver = dns.resolver.Resolver()
        resolver.timeout = 5
        resolver.lifetime = 5

        
        answer = resolver.resolve(rev_name, "PTR")

       
        return [str(rdata).rstrip('.') for rdata in answer]
    except Exception:
       
        return []


def ip_range(start_ip, end_ip):
    start = int(ip_address(start_ip))  
    end = int(ip_address(end_ip))      
   
    return [str(ip_address(ip)) for ip in range(start, end + 1)]


def scan_ip_range(start_ip, end_ip, output_csv):
    ip_list = ip_range(start_ip, end_ip) 
    results = []

   
    for ip in tqdm(ip_list, desc="PTR searching"):
        aliases = reverse_dns(ip)
        if aliases:
            
            for alias in aliases:
                results.append({"IP Adresss": ip, "Alias": alias})
        else:
           
            results.append({"IP Adress": ip, "Alias": "-"})

   
    pd.DataFrame(results).to_csv(output_csv, index=False, encoding="utf-8-sig")
    print(f"[✓] Result saved to CSV: {output_csv}")

if __name__ == "__main__":
   
    scan_ip_range("your_ip_start", "your_ip_end", "dns_result.csv")