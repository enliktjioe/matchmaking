import requests
from bs4 import BeautifulSoup
import csv
import time
import re

def scrape_uni_bremen_employees():
    main_url = "https://www.uni-bremen.de/en/university/campus/list-of-employees"
    
    print("🔍 Fetching main directory page...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    session = requests.Session()
    response = session.get(main_url, headers=headers)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract letter links with cHash
    letter_links = {}
    letter_elements = soup.find_all('a', href=re.compile(r'/persons/[A-Z]'))
    
    print("📋 Extracting letter links WITH cHash:")
    for link in letter_elements:
        href = link.get('href')
        if href:
            match = re.search(r'/persons/([A-Z])(?:\?cHash=([a-f0-9]+))?', href, re.I)
            if match:
                letter = match.group(1).upper()
                if letter not in letter_links:
                    full_url = f"https://www.uni-bremen.de{href}"
                    letter_links[letter] = full_url
                    print(f"  {letter}: {full_url}")
    
    # ✅ FORCE ADD LETTER A FIRST (if missing)
    letter_a_url = "https://www.uni-bremen.de/en/university/campus/list-of-employees/persons/A?cHash=318dfe23ad092804f7737d38350b7d16"
    if 'A' not in letter_links:
        letter_links['A'] = letter_a_url
        print(f"  ➕ FORCED A: {letter_a_url}")
    
    print(f"\n📊 Total letters: {len(letter_links)}")
    
    # ✅ PRIORITIZE A FIRST, then alphabetical order
    processing_order = ['A'] + [letter for letter in sorted(letter_links.keys()) if letter != 'A']
    
    print(f"🔄 Processing order: {', '.join(processing_order[:5])}...")
    
    # Scrape in custom order (A first!)
    all_employees = []
    
    for letter in processing_order:
        url = letter_links[letter]
        print(f"\n📄 Scraping {letter}... ({url})")
        
        try:
            response = session.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            table = soup.find('table', class_='hbuxmlcon-table')
            if not table:
                table = soup.find('table')
                if not table:
                    print(f"  ❌ No table found")
                    continue
            
            rows = table.find_all('tr')
            print(f"  📊 Total rows: {len(rows)}")
            
            count = 0
            for row in rows[1:]:
                cols = row.find_all(['td', 'th'])
                if len(cols) >= 2:
                    name_link = cols[0].find('a')
                    name = name_link.get_text(strip=True) if name_link else cols[0].get_text(strip=True)
                    
                    institution = cols[1].get_text(strip=True).replace('\n', ' ').strip()
                    phone = cols[2].get_text(strip=True).strip() if len(cols) > 2 else ""
                    
                    if (name and len(name) > 2 and 
                        name[0].isalpha() and 
                        not any(h in name.lower() for h in ['name', 'header', 'namenname'])):
                        
                        all_employees.append([name, institution, phone])
                        count += 1
            
            print(f"  ✅ Saved {count} employees")
            time.sleep(1.5)
            
        except Exception as e:
            print(f"  ❌ Error {letter}: {str(e)[:80]}")
            continue
    
    # Save CSV
    filename = "uni_bremen_employees_full.csv"
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Name", "Institution", "Phone"])
        writer.writerows(all_employees)
    
    a_count = sum(1 for emp in all_employees if emp[0].upper().startswith('A'))
    print(f"\n🎉 SUCCESS!")
    print(f"📈 Total: {len(all_employees)} employees")
    print(f"✅ Letter A: {a_count} (processed FIRST)")
    
    return filename

if __name__ == "__main__":
    scrape_uni_bremen_employees()
