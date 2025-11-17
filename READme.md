# Job & Internship Finder

A simple and beginner-friendly web application that helps users search for live job and internship openings and view current trends using charts.
It uses Python (Flask) for backend, BeautifulSoup for web scraping, and Matplotlib for data visualization — all without any database.

# Technology Used:

Front End: HTML, CSS
Back End: Python (Flask), BeautifulSoup, Matplotlib
Libraries: Requests, lxml
Database: No database used (data stored in memory)

# Requirements
1.Install Python 3, Visual Studio Code, and any browser

2.Install dependencies:
pip install -r requirements.txt

Or manually:
pip install flask requests beautifulsoup4 lxml matplotlib

3.Folder structure:

<pre> ``` project/ │ ├── backend.py ├── requirements.txt │ ├── templates/ │ └── index.html │ └── static/ ├── by_city.png ├── by_type.png └── by_trend.png ``` </pre>

4.Run the project:
python backend.py

5.Open in browser:
http://127.0.0.1:5000/

# Features
Job & Internship Search
•	Search by role / position
•	Search by location / city
•	Filter Job, Internship, or both
•	Optional strict filter: Only matching titles
•	Select any combination of these sources:
    •	Indeed
    •	LinkedIn (best effort scraping)
    •	RemoteOK (remote jobs)

# Real-time Trend Charts

Automatically generated using Matplotlib:

• Openings by City
Shows the distribution of job openings across cities.

• Openings by Type
Shows counts of Job vs Internship.

• Openings (Last 14 Days)
Visualizes day-wise search trends.

# ✔ Beginner-Friendly & No Database
All scraping results are stored in memory.
No MySQL / PostgreSQL / MongoDB needed — just run and use.

# How It Works
1.User selects filters and job sources
2.backend.py scrapes:
•	Indeed public HTML
•	LinkedIn public job listings
•	RemoteOK remote jobs
3.Extracted data is cleaned using BeautifulSoup
4.Flask renders results dynamically
5.Charts are saved as images inside /static/
6.The frontend loads these charts on the right-side panel

# Hosting
You can host this on:
•	PythonAnywhere
•	Render / Railway
•	AWS EC2
•	Simply upload your project and run the Flask server.

# About Me
![banner](banner.jpg)

Mahesh Kshirsagar<br>
maheshkshirsagar510@gmail.com<br>
Maharashtra, India







