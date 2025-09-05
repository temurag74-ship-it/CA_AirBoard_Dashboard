
# Air Board Program Summary Dashboard (Streamlit)

An interactive Streamlit dashboard for exploring the Air Board Program Summary data.

## Features
- Sidebar filters:
  - Project Completed date range
  - Incentive Program
  - Equipment Type
  - Old Equipment Make
  - New Equipment Make
  - Incentive Amount range
- KPIs: project count, total incentive, average incentive
- Charts: total incentive by year, by equipment type, top new equipment makes (count), and incentive distribution by program
- Download filtered data as CSV or Excel

## Project Structure
```text
.
├── app.py
├── requirements.txt
├── README.md
└── data/
    └── Airboard Program Summary Data.xlsx
```

## Getting Started (Local)
1. Create and activate a virtual environment (optional).
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   streamlit run app.py
   ```
4. Open the URL Streamlit prints (usually http://localhost:8501).

## Deployment
- Push this repository to GitHub.
- In Streamlit Community Cloud (share.streamlit.io), create a new app pointing to `app.py` on your repo's main branch.

## Notes
- The app expects the data file at `data/Airboard Program Summary Data.xlsx` and reads the sheet named `Air Board Program Summary`.
- If your file name or sheet name changes, edit those in `app.py`.
