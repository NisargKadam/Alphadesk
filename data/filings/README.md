# Filings drop zone

Put annual reports or 10-K PDFs in this folder, then index them:

```bash
cd backend
.venv/bin/python -m app.ingest ../data/filings
```

Re-running is safe — chunk IDs are content-derived, so unchanged documents
upsert onto themselves.

## Where to find real filings

- Any listed company's **investor relations** page (look for "Annual Report").
- **SEC EDGAR** (US listings): https://www.sec.gov/cgi-bin/browse-edgar — search a
  ticker, download the 10-K.
- **SGX** (Singapore): https://www.sgx.com/securities/company-announcements —
  filter by "Annual Reports".
- **NSE India**: https://www.nseindia.com/companies-listing/corporate-filings-annual-reports

## The sample document

`sampleco_annual_report_SYNTHETIC.txt` is a fictional annual report written
for this course (its first line says so), covering revenue segments, an
AI-risk discussion, and a dividend policy — so the retrieval demo works
before you add any real PDFs. Form-feed characters split it into "pages" the
same way a real PDF ingests page by page.
