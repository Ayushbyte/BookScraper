from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import requests
from bs4 import BeautifulSoup
import csv

def get_all_book_links(url, target_count=100):
    # Setup the Chrome driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(url)
    
    # Wait for initial page load
    time.sleep(2)
    prev_count = 0

    # Scroll until we have loaded at least target_count books or no more new books load
    while True:
        # Scroll to the bottom of the page
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Wait for new content to load
        time.sleep(2)
        # Find book links
        links = driver.find_elements(By.XPATH, '//a[contains(@href, "/read/")]')
        current_count = len(links)
        print(f"Found {current_count} book links...")
        if current_count >= target_count or current_count == prev_count:
            break
        prev_count = current_count

    # Extract the URLs (ensuring unique values)
    hrefs = list({link.get_attribute("href") for link in links})
    driver.quit()
    return hrefs

def scrape_book_details(book_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(book_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    book_details = {
        'Name': soup.find('h2', class_='section-title').text.strip() if soup.find('h2', class_='section-title') else 'N/A',
        'Author': soup.find('span', class_='auth_name').text.strip() if soup.find('span', class_='auth_name') else 'N/A',
        'Price': soup.find('span', class_='current_price bmrp').text.strip() if soup.find('span', class_='current_price bmrp') else 'N/A',
        'Summary': soup.find('div', class_='description').text.strip() if soup.find('div', class_='description') else 'N/A',
        'Genre': 'Cooking, Food & Wine'
    }
    return book_details

def save_to_csv(book_details_list, filename="book_details.csv"):
    headers = ["Name", "Author", "Price", "Genre", "Summary"]
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(book_details_list)
    print(f"Book details saved to {filename}")

if __name__ == "__main__":
    category_url = "https://notionpress.com/in/store/categories/cooking-food-wine/"
    print("Fetching book URLs...")
    book_urls = get_all_book_links(category_url, target_count=100)
    print(f"Fetched {len(book_urls)} book URLs.")

    book_details_list = []
    for url in book_urls:
        print(f"Scraping details for: {url}")
        try:
            details = scrape_book_details(url)
            print(f"Scraped details: {details}")
            book_details_list.append(details)
        except Exception as e:
            print(f"Error scraping {url}: {e}")

    print(f"Saving {len(book_details_list)} books to CSV...")
    save_to_csv(book_details_list)
