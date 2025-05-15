
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
import urllib3
from concurrent.futures import ThreadPoolExecutor, as_completed


urllib3.disable_warnings()


COMMON_DIRS = [
    ".",  # root
    "admin", "login", "test", "backup", "dev", "dashboard", "panel", ".git",
    "config", "old", "uploads", "files", "data", "db", "database", "private",
    "temp", "tmp", "log", "logs", "status", ".env", "config.php", "webadmin",
    "siteadmin", "cpanel", "includes", "webdav", "staging", "monitor",
    "debug", "shell", "api", "v1", "v2"
]


def is_directory_listing(html):
    soup = BeautifulSoup(html, 'html.parser')  
    text = soup.get_text(separator=' ', strip=True)  
   
    return "Index of" in text or "Directory listing for" in text or "directory" in text or "../" in text


def check_directory(ip, proto, directory):
    url = urljoin(f"{proto}{ip}/", directory + "/") 
    try:
        response = requests.get(url, timeout=10, verify=False, allow_redirects=True)
        if response.status_code == 200:
            if is_directory_listing(response.text):
                return (ip, url, "Yes")  
            else:
                return (ip, url, "No")  
        elif response.status_code in [301, 302]:
            return (ip, url, f"Yönlendiriliyor ({response.status_code})")  # Redirect
    except requests.RequestException:
        return None  


def scan_ip(ip):
    results = []
    protocols = ['http://', 'https://']  
    with ThreadPoolExecutor(max_workers=20) as executor:  # Parallel working
    
        futures = [
            executor.submit(check_directory, ip, proto, directory)
            for proto in protocols
            for directory in COMMON_DIRS
        ]
       
        for future in as_completed(futures):
            result = future.result()
            if result:
                results.append({
                    "IP": result[0],
                    "URL": result[1],
                    "Directory Listing": result[2]
                })
    return results


def main():
    
    excel_path = "your_csv_path"
    output_csv = "your results saved to the this path"

   
    try:
        df = pd.read_excel(excel_path)
    except Exception as e:
        print(f"[X] CSV file couldnt read: {e}")
        return

    all_results = []

  
    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Scanning IP's"):
        ip = str(row.get("Alias")).strip()
      
        if ip and ip.lower() != "Couldn't resolved":
            ip_results = scan_ip(ip)
            all_results.extend(ip_results)


    result_df = pd.DataFrame(all_results)
    result_df.to_csv(output_csv, index=False, encoding="utf-8-sig")
    print(f"[✓] Results saved {output_csv}")


if __name__ == "__main__":
    main()