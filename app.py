import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

def find_careers_page(company_name):
    query = f"{company_name} careers site"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(f"https://www.google.com/search?q={query.replace(' ', '+')}", headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    for a in soup.find_all('a', href=True):
        href = a['href']
        if 'careers' in href or 'jobs' in href:
            match = re.search(r'https?://[^\s"]+', href)
            if match:
                return match.group(0)
    return None

def scrape_jobs(careers_url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(careers_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        jobs = []

        for tag in soup.find_all(['li', 'div', 'p']):
            text = tag.get_text(separator=' ', strip=True)
            if re.search(r'devops|cloud|sre|infrastructure', text, re.I) and \
               re.search(r'0[-–]5\s*years|entry[- ]level|junior', text, re.I):
                jobs.append(text)
        return jobs
    except Exception as e:
        return []

def main():
    st.title("🔍 DevOps Job Finder (Experience < 5 Years)")
    st.write("Upload a CSV with a `Company` column to find DevOps-related jobs.")

    uploaded_file = st.file_uploader("Upload CSV file", type=['csv'])

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        if 'Company' not in df.columns:
            st.error("CSV must contain a 'Company' column.")
            return

        all_jobs = []
        progress = st.progress(0)
        total = len(df)
        
        for i, company in enumerate(df['Company']):
            st.text(f"Processing: {company}")
            careers_url = find_careers_page(company)
            if careers_url:
                jobs = scrape_jobs(careers_url)
                for job in jobs:
                    all_jobs.append({"Company": company, "Careers Page": careers_url, "Job Description": job})
            progress.progress((i + 1) / total)

        if all_jobs:
            jobs_df = pd.DataFrame(all_jobs)
            st.success(f"Found {len(jobs_df)} relevant jobs.")
            st.dataframe(jobs_df)
            csv = jobs_df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Results as CSV", csv, "filtered_jobs.csv", "text/csv")
        else:
            st.warning("No relevant jobs found.")

if __name__ == "__main__":
    main()
