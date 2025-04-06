import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

# Setup Selenium Chrome options
options = webdriver.ChromeOptions()
# options.add_argument('--headless')  # Disable headless for debugging
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)  # 10 second timeout

BASE_URL = "https://www.shl.com/solutions/products/product-catalog"
OUTPUT_FILE = "individual_test_solutions.json"

def get_soup_from_url(url):
    driver.get(url)
    try:
        # Wait for the section heading to appear
        wait.until(
            EC.presence_of_element_located((By.XPATH, "//h4[contains(text(), 'Individual Test Solutions')]"))
        )
        return BeautifulSoup(driver.page_source, 'html.parser')
    except TimeoutException:
        print(f"❌ Timeout waiting for heading on {url}")
        return BeautifulSoup(driver.page_source, 'html.parser')
    
def get_soup_for_individual_test_solution(url):
    driver.get(url)
    try:
        # Wait for the section heading to appear
        wait.until(
            EC.presence_of_element_located((By.XPATH, "//h4[contains(text(), 'Description')]"))
        )
        return BeautifulSoup(driver.page_source, 'html.parser')
    except TimeoutException:
        print(f"❌ Timeout waiting for heading on {url}")
        return BeautifulSoup(driver.page_source, 'html.parser')

def extract_individual_test_solutions(soup, page_url):
    data = []

    try:
        # Initial page load
        driver.get(page_url)
        
        # Wait for table to be present
        table = wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
        tbody = wait.until(EC.presence_of_element_located((By.TAG_NAME, "tbody")))
        
        # Get rows after waiting for them
        rows = tbody.find_elements(By.TAG_NAME, "tr")
        total_rows = len(rows)
        print(f"\n📑 Found {total_rows} rows on page {page_url}")
        
        # Store basic row data first to avoid stale elements
        row_data = []
        for row in rows:
            try:
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) < 4:
                    continue
                
                title_tag = cols[0].find_element(By.TAG_NAME, "a")
                row_data.append({
                    'title': title_tag.text.strip() if title_tag else "",
                    'link': title_tag.get_attribute('href') if title_tag else "",
                    'remote_testing': len(cols[1].find_elements(By.CSS_SELECTOR, "span.catalogue__circle.-yes")) > 0,
                    'adaptive_irt': len(cols[2].find_elements(By.CSS_SELECTOR, "span.catalogue__circle.-yes")) > 0,
                    'test_types': [span.text.strip() for span in cols[3].find_elements(By.CSS_SELECTOR, "span.product-catalogue__key")]
                })
            except (StaleElementReferenceException, NoSuchElementException) as e:
                print(f"❌ Error collecting basic row data: {str(e)}")
                continue
        
        # Now process each row's detailed data
        for row_index, basic_data in enumerate(row_data, 1):
            try:
                print(f"\n👉 Processing row {row_index} of {len(row_data)}")
                print(f"📌 Title: {basic_data['title']}")
                
                # Initialize detail_info dictionary for each row
                detail_info = {
                    'description': '',
                    'job_levels': '',
                    'languages': '',
                    'assessment_length': ''
                }

                if basic_data['link']:
                    print(f"🔗 Visiting detail page: {basic_data['link']}")
                    # Navigate to the detail page
                    driver.get(basic_data['link'])
                    try:
                        # Wait for content to load
                        wait.until(EC.presence_of_element_located((By.TAG_NAME, "h4")))
                        
                        # Find all h4 elements
                        h4_elements = driver.find_elements(By.TAG_NAME, "h4")
                        
                        for h4 in h4_elements:
                            text = h4.text.strip()
                            if text in ['Description', 'Job levels', 'Languages', 'Assessment length']:
                                try:
                                    # Get the next sibling p tag
                                    p_element = h4.find_element(By.XPATH, "following-sibling::p[1]")
                                    value = p_element.text.strip()
                                    
                                    # Map the h4 text to our dictionary keys
                                    key = text.lower().replace(' ', '_')
                                    detail_info[key] = value
                                    print(f"✅ Found {text}: {value[:50]}...")
                                except NoSuchElementException:
                                    print(f"⚠️ No value found for {text}")
                                    continue
                    except TimeoutException:
                        print(f"❌ Timeout waiting for details on {basic_data['link']}")

                # Combine basic and detail data
                data.append({
                    **basic_data,
                    **detail_info
                })
                print(f"✅ Successfully processed row {row_index}")

            except Exception as e:
                print(f"❌ Error processing row {row_index}: {str(e)}")
                continue

        print(f"\n✅ Completed processing all {len(row_data)} rows on current page")
        return data

    except TimeoutException:
        print(f"❌ Timeout waiting for elements on {page_url}")
        return []


def get_all_pages(type_num):
    all_data = []
    start = 0

    while True:
        url = f"{BASE_URL}?type={type_num}&start={start}"
        print(f"🔎 Scraping {url}")
        soup = get_soup_from_url(url)

        page_data = extract_individual_test_solutions(soup, url)
        if not page_data:
            print(f"❌ No more data at start={start}, stopping loop.")
            break

        all_data.extend(page_data)
        start += 12
        time.sleep(1)

    return all_data

if __name__ == "__main__":
    full_results = []

    for t in [1, 2]:
        print(f"\n🟢 Starting scrape for type={t}")
        results = get_all_pages(t)
        print(f"✅ Found {len(results)} records for type={t}")
        full_results.extend(results)

    with open(OUTPUT_FILE, "w", encoding='utf-8') as f:
        json.dump(full_results, f, indent=4, ensure_ascii=False)

    print(f"\n💾 Data saved to '{OUTPUT_FILE}'")
    driver.quit()