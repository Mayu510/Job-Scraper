# backend.py
from flask import Flask, request, render_template
import requests
from bs4 import BeautifulSoup
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from urllib.parse import quote_plus
from datetime import datetime, timedelta

app = Flask(__name__)
STATIC_DIR = 'static'
os.makedirs(STATIC_DIR, exist_ok=True)

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

# ----------------- simple scrapers -----------------
def clean_text(el):
    if not el:
        return ''
    return ' '.join(el.split()).strip()

def scrape_indeed(role, place, max_results=25):
    """Simple Indeed scraper (public HTML). Best-effort."""
    results = []
    q = quote_plus(role or '')
    l = quote_plus(place or '')
    url = f'https://www.indeed.com/jobs?q={q}&l={l}'
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, 'lxml')
        cards = soup.select('.result, .job_seen_beacon, .jobsearch-SerpJobCard') or soup.select('a[href*="/rc/clk"]')
        for c in cards[:max_results]:
            # title
            t = ''
            t_el = c.select_one('h2.jobTitle') or c.select_one('a.jobtitle') or c.select_one('a')
            if t_el:
                t = clean_text(t_el.get_text(separator=' ', strip=True))
            # company
            comp = c.select_one('.companyName') or c.select_one('.company')
            company = clean_text(comp.get_text(strip=True)) if comp else ''
            # location
            loc_el = c.select_one('.companyLocation') or c.select_one('.location')
            location = clean_text(loc_el.get_text(strip=True)) if loc_el else ''
            # link
            a = c.select_one('a[href]')
            link = ''
            if a and a.get('href'):
                href = a.get('href').strip()
                if href.startswith('http'):
                    link = href
                elif href.startswith('/'):
                    link = 'https://www.indeed.com' + href
            results.append({
                'source': 'Indeed',
                'title': t or 'N/A',
                'company': company or 'N/A',
                'location': location or 'N/A',
                'job_type': 'Job',
                'url': link,
                'scraped_at': datetime.utcnow()
            })
    except Exception as e:
        print('Indeed error:', e)
    return results

def scrape_linkedin(role, place, max_results=25):
    """
    Very simple LinkedIn public page fetch.
    LinkedIn often serves JS and blocks scraping — this is best-effort.
    """
    results = []
    q = quote_plus(role or '')
    l = quote_plus(place or '')
    url = f'https://www.linkedin.com/jobs/search/?keywords={q}&location={l}'
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, 'lxml')
        cards = soup.select('.result-card') or soup.select('.jobs-search__results-list li') or soup.select('a[href*="/jobs/view/"]')
        for c in cards[:max_results]:
            t = ''
            t_el = c.select_one('h3') or c.select_one('h2') or c.select_one('a')
            if t_el:
                t = clean_text(t_el.get_text(separator=' ', strip=True))
            comp = c.select_one('.result-card__subtitle') or c.select_one('.base-search-card__subtitle') or c.select_one('.job-result-card__subtitle')
            company = clean_text(comp.get_text(strip=True)) if comp else ''
            loc_el = c.select_one('.job-result-card__location') or c.select_one('.job-result-card__location') or c.select_one('.result-card__meta')
            location = clean_text(loc_el.get_text(strip=True)) if loc_el else ''
            a = c.select_one('a[href]')
            link = ''
            if a and a.get('href'):
                link = a.get('href').strip()
            results.append({
                'source': 'LinkedIn',
                'title': t or 'N/A',
                'company': company or 'N/A',
                'location': location or 'N/A',
                'job_type': 'Job',
                'url': link,
                'scraped_at': datetime.utcnow()
            })
    except Exception as e:
        print('LinkedIn error (likely blocked/JS):', e)
    return results

def scrape_remoteok(role, place, max_results=25):
    """RemoteOK is friendly to simple scrapers for many roles."""
    results = []
    url = f'https://remoteok.com/remote-{quote_plus(role or "")}-jobs' if role else 'https://remoteok.com/remote-jobs'
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, 'lxml')
        cards = soup.select('tr.job') or soup.select('.job') or soup.select('article')
        for c in cards[:max_results]:
            title_el = c.select_one('h2') or c.select_one('a') or c.select_one('.company_and_position h2')
            title = clean_text(title_el.get_text(separator=' ', strip=True)) if title_el else 'N/A'
            company_el = c.select_one('.company') or c.select_one('.companyLink') or c.select_one('.company h3')
            company = clean_text(company_el.get_text(strip=True)) if company_el else 'N/A'
            location = 'Remote / WFH'
            a = c.select_one('a[href]')
            link = ''
            if a and a.get('href'):
                href = a.get('href').strip()
                if href.startswith('http'):
                    link = href
                elif href.startswith('/'):
                    link = 'https://remoteok.com' + href
            results.append({
                'source': 'RemoteOK',
                'title': title,
                'company': company,
                'location': location,
                'job_type': 'Job',
                'url': link,
                'scraped_at': datetime.utcnow()
            })
    except Exception as e:
        print('RemoteOK error:', e)
    return results

# ----------------- chart helpers -----------------
def save_bar_chart(pairs, out_path, title='Chart'):
    """pairs: list of (label, count)"""
    labels = [p[0] for p in pairs] if pairs else []
    values = [int(p[1]) for p in pairs] if pairs else []
    if not labels:
        fig, ax = plt.subplots(figsize=(6,3))
        ax.text(0.5,0.5,'No data',ha='center',va='center',fontsize=14,color='gray')
        ax.axis('off')
        fig.savefig(out_path)
        plt.close(fig)
        return
    fig, ax = plt.subplots(figsize=(6,3.2))
    ax.bar(range(len(values)), values)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.set_ylabel('Count')
    ax.set_title(title)
    plt.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)

def save_trend_chart(dates, counts, out_path):
    fig, ax = plt.subplots(figsize=(6,3.2))
    ax.plot(range(len(counts)), counts, marker='o')
    ax.set_xticks(range(len(dates)))
    labels = [d if (i % 2 == 0) else '' for i,d in enumerate(dates)]
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.set_title('Openings (last 14 days)')
    ax.set_ylabel('Count')
    plt.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)

def make_charts(jobs):
    # By city
    city_counts = {}
    type_counts = {}
    now = datetime.utcnow()
    # trend: last 14 days (most scrapes will be today)
    start = now.date() - timedelta(days=13)
    date_list = [(start + timedelta(days=i)).isoformat() for i in range(14)]
    date_counts = {d:0 for d in date_list}

    for j in jobs:
        loc = j.get('location') or 'N/A'
        city_counts[loc] = city_counts.get(loc, 0) + 1
        jt = j.get('job_type') or 'Unknown'
        type_counts[jt] = type_counts.get(jt, 0) + 1
        dt = j.get('scraped_at')
        if isinstance(dt, datetime):
            day = dt.date().isoformat()
            if day in date_counts:
                date_counts[day] += 1

    city_pairs = sorted(city_counts.items(), key=lambda x: x[1], reverse=True)[:8]
    type_pairs = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:8]
    date_pairs = [date_counts[d] for d in date_list]

    save_bar_chart(city_pairs, os.path.join(STATIC_DIR, 'by_city.png'), title='Openings by City')
    save_bar_chart(type_pairs, os.path.join(STATIC_DIR, 'by_type.png'), title='Openings by Type')
    save_trend_chart(date_list, date_pairs, os.path.join(STATIC_DIR, 'by_trend.png'))

# ----------------- Flask routes -----------------
@app.route('/', methods=['GET'])
def index():
    # show empty page (no results) initially
    return render_template('index.html', jobs=[], role='', place='', filter_exact=False,
                           want_job=True, want_intern=True,
                           src_indeed=False, src_linkedin=False, src_remoteok=False)

@app.route('/search', methods=['POST'])
def search():
    role = request.form.get('role','').strip()
    place = request.form.get('place','').strip()
    try:
        max_results = int(request.form.get('max_results') or 25)
    except:
        max_results = 25

    filter_exact = bool(request.form.get('filter_exact'))
    want_job = bool(request.form.get('type_job'))
    want_intern = bool(request.form.get('type_intern'))
    if not want_job and not want_intern:
        want_job = want_intern = True

    # which sources
    src_indeed = bool(request.form.get('src_indeed'))
    src_linkedin = bool(request.form.get('src_linkedin'))
    src_remoteok = bool(request.form.get('src_remoteok'))

    # collect results in memory
    jobs = []

    if src_indeed:
        jobs += scrape_indeed(role, place, max_results=max_results)
    if src_linkedin:
        jobs += scrape_linkedin(role, place, max_results=max_results)
    if src_remoteok:
        jobs += scrape_remoteok(role, place, max_results=max_results)

    # optional filter (only matching titles/companies)
    if filter_exact and role:
        tokens = [t.lower() for t in role.split() if len(t) > 2]
        def matches_exact(j):
            text = (j.get('title','') + ' ' + j.get('company','')).lower()
            return all(tok in text for tok in tokens)
        jobs = [j for j in jobs if matches_exact(j)]

    # filter job/intern type (scrapers here mark everything as 'Job' by default)
    if not want_job or not want_intern:
        filtered = []
        for j in jobs:
            jt = j.get('job_type','').lower()
            if jt == 'job' and want_job:
                filtered.append(j)
            if jt == 'internship' and want_intern:
                filtered.append(j)
        jobs = filtered

    # generate charts from current job list
    make_charts(jobs)

    # render result page with current inputs and jobs
    return render_template('index.html',
                           jobs=jobs,
                           role=role,
                           place=place,
                           filter_exact=filter_exact,
                           want_job=want_job,
                           want_intern=want_intern,
                           src_indeed=src_indeed,
                           src_linkedin=src_linkedin,
                           src_remoteok=src_remoteok)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
