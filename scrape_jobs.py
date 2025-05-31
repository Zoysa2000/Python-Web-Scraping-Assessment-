import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# URL to search for jobs on LinkedIn
BASE_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=AI+Engineer&location=USA&start={}"

# Function to fetch job listing HTML content
def fetch_job_listings(start):
    url = BASE_URL.format(start)
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()  # Raise an exception for bad responses (4xx, 5xx)
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching jobs at offset {start}: {e}")
        return None

# Function to fetch job detail
def fetch_job_detail(url):
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract job summaryfrom job page
        description = soup.find('div', class_='description__text')
        short_desc = description.get_text(strip=True)[:300] if description else "N/A"

        # Extract posted date
        posted = soup.find('span', class_='posted-time-ago__text')
        posted_date = posted.text.strip() if posted else "N/A"

        return short_desc, posted_date
    except Exception as e:
        print(f"Error fetching detail from {url}: {e}")
        return "N/A", "N/A"

# Function  parse each job card in the HTML and extract required fields
def parse_jobs(html):
    soup = BeautifulSoup(html, 'html.parser')
    job_cards = soup.find_all('li') 

    jobs = []
    for job in job_cards:
        try:
            # Extract basic info from job card
            title = job.find('h3').text.strip()
            company = job.find('h4').text.strip()
            location = job.find('span', class_='job-search-card__location').text.strip()
            link = job.find('a', href=True)['href']

    
            short_desc, posted_date = fetch_job_detail(link)

            # Sleep briefly to avoid being blocked by LinkedIn
            time.sleep(1)

            # Store job info in a dictionary
            jobs.append({
                "Job Title": title,
                "Company Name": company,
                "Location": location,
                "Posted Date": posted_date,
                "Job Summary": short_desc,
                "Job URL": link
            })

        except Exception as e:
            print(f"Error parsing job: {e}")
            continue
    return jobs

# Main function 
def main():
    all_jobs = []

    # Iterate through 3 pages
    for start in range(0, 75, 25):
        print(f"Fetching page starting from {start}...")
        html = fetch_job_listings(start)
        if html:
            jobs = parse_jobs(html)
            print(f" -> Extracted {len(jobs)} jobs.")
            all_jobs.extend(jobs) 

    # Save  CSV file
    if all_jobs:
        df = pd.DataFrame(all_jobs)
        df.to_csv("ai_jobs.csv", index=False, encoding='utf-8')
        print(f"\n Saved {len(all_jobs)} jobs to linkedin_ai_jobs_full.csv")
    else:
        print(" No jobs were scraped.")

if __name__ == "__main__":
    main()



