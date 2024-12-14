import requests
from bs4 import BeautifulSoup
import json
import time

BASE_URL = "https://www.powerball.com/previous-results?gc=lotto-america"

def get_initial_data():
    response = requests.get(BASE_URL)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Extract load more button info
    load_more_btn = soup.find('button', id='loadMore')
    if not load_more_btn:
        # If no load more button, all data might be on the first page
        return soup, None, None
    
    start_val = int(load_more_btn['data-val'])  # starting page
    max_val = int(load_more_btn['data-max'])    # max page
    
    return soup, start_val, max_val

def get_additional_results(val_to_load):
    # We'll fetch pg=2, pg=3, ..., up to pg=max_val
    # and store the HTML from each page.
    url = f"{BASE_URL}&pg={val_to_load}"
    print(f"Fetching page {val_to_load}...")
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Stopping at page {val_to_load}: HTTP {response.status_code}")
        exit(-2) 
    return BeautifulSoup(response.text, "html.parser")

def parse_results(html_soup, results):
    # Each drawing is in an <a class="card">
    cards = html_soup.find_all('a', class_='card')
    for card in cards:
        title = card.find('h5', class_='card-title')
        if not title:
            continue
        date_str = title.get_text(strip=True)
        
        # Extract the game balls
        ball_group = card.find('div', class_='game-ball-group')
        if not ball_group:
            continue
        balls = ball_group.find_all('div', class_='form-control')
        
        main_numbers = [int(b.get_text(strip=True)) for b in balls if 'star-ball' not in b.get('class', [])]
        star_number = None
        for b in balls:
            if 'star-ball' in b.get('class', []):
                star_number = int(b.get_text(strip=True))
                break
        
        multiplier_span = card.find('span', class_='multiplier')
        multiplier = multiplier_span.get_text(strip=True) if multiplier_span else None
        
        results[date_str] = {
            'main_numbers': main_numbers,
            'star_number': star_number,
            'multiplier': multiplier
        }
    
    return results

def main():
    # Step 1: Get initial page and find max number of loads 
    initial_soup, start_val, max_val = get_initial_data()
    
    if start_val is None or max_val is None:
        print("Something went wrong... no load number values")
        exit(-1)
    
    # Step 2: parse initial results 
    results = {}
    results = parse_results(initial_soup, results)
    time.sleep(2)

    #Step 3: get all values via additional gets up to max
    for i in range(start_val, max_val + 1):
        results = parse_results(get_additional_results(i), results)
        time.sleep(2) #lets not overload the server, thats naughty

    #Step 4: save results
    with open("lotto_america_winning_nums.json", "w") as f:
        json.dump(results, f)
    

if __name__ == "__main__":
    main()

