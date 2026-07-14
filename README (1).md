# Load Monitor Dashboard

A self-contained dashboard for substation/feeder load (LOAD01) and province
peak load. The page (`index.html`) is static — it loads its data from the
`data/` folder at runtime, so **updating the dashboard never requires
touching or regenerating the HTML file.**

## Folder structure

```
index.html                 <- the dashboard (never needs to change for data updates)
convert_excel.py           <- run this to turn your Excel file into the JSON below
data/
  sum_data.json            <- from the "SUM" sheet
  province_data.json       <- from the "PROVINCE" sheet
```

## Deploying to GitHub Pages

1. Create a new GitHub repository (or use an existing one).
2. Upload `index.html`, `convert_excel.py`, and the whole `data/` folder to
   the repo (keep the folder structure above).
3. In the repo: **Settings → Pages → Source → Deploy from branch** → pick
   `main` (or `master`) and `/ (root)` → Save.
4. GitHub gives you a URL like
   `https://<your-username>.github.io/<repo-name>/` — that's your live
   dashboard.

## Updating the data (every time you get a new Excel export)

You do **not** need to come back and ask for the HTML to be rebuilt. Just:

1. Install the one-time requirement (only needed once on your machine):
   ```
   pip install pandas openpyxl
   ```
2. Run the converter on your new Excel file:
   ```
   python3 convert_excel.py YourNewFile.xlsx
   ```
   This overwrites `data/sum_data.json` and `data/province_data.json`.
3. Commit and push just the `data/` folder to GitHub:
   ```
   git add data/
   git commit -m "Update load data"
   git push
   ```
4. GitHub Pages redeploys automatically within a minute or two — refresh the
   live URL and the dashboard shows the new numbers. `index.html` is
   untouched.

## Expected Excel format

**Sheet "SUM"**: columns `SUBSTATION`, `Voltage Level`, `TYPE FEEDER`
(ignored), `Feeder`, then one column per month (Buddhist-era date headers)
with that month's load value per feeder.

**Sheet "PROVINCE"**: 12 columns in order — `MONTH`, `SUM PROVINCE`, `PNB`,
`NSN`, `LRI`, `CNT`, `SBR`, `UTI`, `SUM REG1`, `SUM REG4`, `DATE/TIME` (the
peak timestamp, as text).

If your column layout changes, open `convert_excel.py` and adjust the column
names near the top of `convert_sum_sheet()` / `convert_province_sheet()`
accordingly.

## Local testing (optional)

Opening `index.html` by double-clicking it will **not** work — browsers
block `fetch()` of local files for security reasons. To preview locally,
serve the folder with a tiny local web server first:

```
python3 -m http.server 8000
```

then open `http://localhost:8000/index.html` in your browser.
