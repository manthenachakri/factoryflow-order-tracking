# FactoryFlow — Order & Dispatch Tracker

A Streamlit + SQLite prototype for the Wantace Solutions Sprint assignment, based on the fictional Vardhan Steelware client pack.

## Features
- Order register with search, status filters, create and update actions
- Dashboard showing active orders, stuck/partial orders and payment holds
- Status timeline / dispatch updates
- External polishing register with weight reconciliation flags
- Morning reports for at-risk orders, dispatch backlog and payment holds
- CSV exports
- Seeded demo records based on the supplied assignment pack, with ambiguous source rows flagged for verification

## Run locally
1. Install Python 3.10+.
2. Open a terminal in this folder.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the app:
   ```bash
   streamlit run app.py
   ```
5. Open the local URL shown by Streamlit.

## Important prototype limitations
- No authentication / role-based access yet.
- No multi-user cloud deployment, automated backups, or audit-grade security.
- No WhatsApp, Amazon, Flipkart, Tally, or payment gateway integrations.
- Seeded records are derived from a fictional case study. Duplicate-like rows and missing fields are intentionally flagged for human validation; they should not be assumed to be reconciled business facts.
- Before using with a real factory, add authentication, backups, access controls, validation, deployment configuration, and a tested migration strategy.
