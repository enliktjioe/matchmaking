import requests
from bs4 import BeautifulSoup
import csv
from io import StringIO
import time
import re

def scrape_uni_bremen_employees():
    base_url = "https://www.uni-bremen.de/en/university/campus/list-of-employees/persons/"
    all_employees = []
    
    for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
    # for letter in 'AB':
        try:
            print(f"Scraping {letter}...")
            url = f"{base_url}{letter}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find table rows (adjust selector based on actual HTML structure)
            rows = soup.find_all('tr')  # Common table row selector
            
            for row in rows[1:]:  # Skip header
                cols = row.find_all(['td', 'th'])
                if len(cols) >= 3:
                    name = cols[0].get_text(strip=True)
                    institution = cols[1].get_text(strip=True)
                    phone = cols[2].get_text(strip=True) if len(cols) > 2 else ""
                    
                    all_employees.append([name, institution, phone])
            
            time.sleep(1)  # Be respectful to server
            
        except Exception as e:
            print(f"Error scraping {letter}: {e}")
            continue
    
    # Generate CSV
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Name", "Institution", "Phone"])
    writer.writerows(all_employees)
    
    return output.getvalue()

# Run scraper
csv_content = scrape_uni_bremen_employees()
print(csv_content[:2000] + "..." if len(csv_content) > 2000 else csv_content)

filename = "uni_bremen_employees.csv"

with open(filename, "w", encoding="utf-8") as file:
    file.write(csv_content)

print(f"CSV file saved as {filename}")