# Chemical Equipment Parameter Visualizer

This project was built for the **FOSSEE Web Application Screening Task**.

It consists of:
- A **Django REST API** backend
- A **React web dashboard** frontend
- A **PyQt5 desktop client** frontend

The system allows users to upload chemical equipment CSV files, compute summary statistics, visualize type distribution, view upload history, and download a PDF report. Authentication with token-based login protects upload & report endpoints.

---

## Tech Stack

- **Backend**: Python, Django, Django REST Framework, django-cors-headers, reportlab, pandas
- **Web Frontend**: React, Chart.js (or Recharts, depending on what you used), plain CSS
- **Desktop Frontend**: Python, PyQt5, matplotlib
- **Database**: SQLite (development)

---

## Project Structure

```text
chemviz/
  backend/            # Django project + API app
  web-frontend/       # React single-page app
  desktop-frontend/   # PyQt5 desktop client
  README.md
