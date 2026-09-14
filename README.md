# JobPilot AI — GitHub Pages

This package contains:
- `docs/`: a polished static GitHub Pages landing page.
- `streamlit-app/`: your original Streamlit application.

## Deploy the static site
1. Upload the contents of `docs/` to your GitHub repository root, or keep it inside `docs/`.
2. Open **Settings → Pages**.
3. Select **Deploy from a branch**.
4. Choose your branch and `/docs` folder.
5. Save.

## Important
GitHub Pages (`github.io`) hosts static HTML/CSS/JS only. It cannot directly run the Python/Streamlit backend. Use the static page for the public website and deploy the Streamlit app separately on Streamlit Community Cloud, Render, Railway, or another Python host.
