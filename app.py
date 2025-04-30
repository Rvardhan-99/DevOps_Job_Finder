import streamlit as st
import pandas as pd
import requests
import re

# -------------------------------
# Greenhouse API job fetcher
# -------------------------------
def get_greenhouse_jobs(company_slug):
    url = f"https://boards-api.greenhouse.io/v1/boards/{company_slug}/jobs"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        jobs = []

        for job in data.get('jobs', []):
            title = job.get('title', '')
            location = job.get('location', {}).get('name', '')
            if is_devops_related(title):
                jobs.append({
                    'Company': company_slug,
                    'Platform': 'Greenhouse',
                    'Job Title': title,
                    'Location': location,
                    'Job URL': job.get('absolute_url')
                })
        return jobs
    except Exception as e:
        return []

# -------------------------------
# Lever API job fetcher
# -------------------------------
def get_lever_jobs(company_slug):
    url = f"https://api.lever.co/v0/postings/{company_slug}?mode=json"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        jobs = []

        for job in data:
            title = job.get('text', '')
            location = job.get('categories', {}).get('location', '')
            if is_devops_related(title):
                jobs.append({
                    'Company': company_slug,
                    'Platform': 'Lever',
                    'Job Title': title,
                    'Location': location,
                    'Job URL': job.get('hostedUrl')
                })
        return jobs
    except Exception as e:
        return []

# -------------------------------
# Job title relevance check
# -------------------------------
def is_devops_related(title):
    if re.search(r'devops|cloud|sre|infrastructure|platform', title, re.I):
        if re.search(r'entry|junior|0[-–]5\s*years|early career|graduate', title, re.I):
            return True
    return False

# -------------------------------
# Streamlit App
# -------------------------------
def main():
    st.title("🔍 DevOps Job Finder from Company Careers Pages")
    st.write("Upload a CSV with a `Company` column. It uses Lever and Greenhouse APIs for job scraping.")

    uploaded_file = st.file_uploader("📄 Upload your CSV", type=["csv"])

    # Known mappings of companies to ATS platform slugs
    greenhouse_map = {
        'Databricks': 'databricks',
        'Stripe': 'stripe',
        'Notion': 'notion',
        'Roblox': 'roblox'
    }

    lever_map = {
        'Dropbox': 'dropbox',
        'Lever': 'lever',
        'Rippling': 'rippling'
    }

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        if 'Company' not in df.columns:
            st.error("CSV must contain a 'Company' column.")
            return

        all_jobs = []
        progress = st.progress(0)
        total = len(df)

        for i, company in enumerate(df['Company']):
            st.text(f"Processing {company}...")

            if company in greenhouse_map:
                jobs = get_greenhouse_jobs(greenhouse_map[company])
            elif company in lever_map:
                jobs = get_lever_jobs(lever_map[company])
            else:
                jobs = []

            all_jobs.extend(jobs)
            progress.progress((i + 1) / total)

        if all_jobs:
            jobs_df = pd.DataFrame(all_jobs)
            st.success(f"✅ Found {len(jobs_df)} relevant jobs!")
            st.dataframe(jobs_df)
            csv = jobs_df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download CSV", csv, "filtered_jobs.csv", "text/csv")
        else:
            st.warning("No relevant DevOps jobs found.")

if __name__ == "__main__":
    main()
