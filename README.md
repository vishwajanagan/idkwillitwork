# CHEMLABSVARSHINI
**Molecular Intelligence & Visualization Laboratory** — Explore. Visualize. Analyze. Compare.  
Designed & Developed by Varshini A

A Streamlit educational cheminformatics application using RDKit for molecular parsing, 2D depiction, calculated descriptors, 3D conformers, comparisons, and academic PDF reports.

## Important source note
The source repository `https://github.com/vishwajanagan/vlab` could not be cloned from the build environment because GitHub DNS/network access was unavailable. This ZIP is a new implementation based on the requested specification; it does **not** claim to contain or preserve the original repository's code. Review and merge against the original repository before describing this as a refactor of existing code.

## Features
- SMILES validation and canonicalization with RDKit
- 2D PNG/SVG depictions and MOL/SDF downloads
- 3D conformer generation with RDKit ETKDG/MMFF and interactive 3Dmol.js viewer
- Calculated molecular descriptors and Lipinski threshold screening
- Two-molecule comparison and CSV export
- PDF reports with separate 2D and 3D sections, IST timestamp, optional student details/photo/signature, and blank faculty approval section
- PubChem PUG REST lookup
- Optional OpenAI chemistry assistant with basic fallback
- Browser-updated IST clock and cosmic-violet theme
- Core chemistry tests

## Run locally
Python 3.10+ recommended (use a platform/runtime with compatible RDKit wheels).
```bash
python -m venv .venv
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

## Test
```bash
pytest -q
```

## Streamlit Community Cloud deployment
1. Push this project folder to a GitHub repository you control.
2. Create an app from that repository and set the main file path to `app.py`.
3. Optionally set `OPENAI_API_KEY` and `OPENAI_MODEL` in app secrets.
4. PubChem and the 3Dmol.js viewer need outbound network access.
5. Check RDKit wheel compatibility with the platform Python runtime. A conda-based environment may be needed on some platforms.

## Docker
```bash
docker build -t chemlabsvarshini .
docker run --rm -p 8501:8501 -e OPENAI_API_KEY=your_key chemlabsvarshini
```

## Scientific and deployment caveats
Descriptors are computed values, not experimental measurements. Conformers are computational, not experimental structures. Lipinski rules are screening heuristics, not proof of safety, biological activity, or clinical suitability. AI is live only when credentials are configured and the API call succeeds; otherwise fallback responses are used. PubChem and CDN viewer features need network access. No official SRM logo, endorsement, or approval is represented. The ZIP has not been deployed to a live host.

## Security
Never commit `.env`, API keys, Streamlit secrets, or private student data. Uploaded photos/signatures are passed in memory to PDF generation and are not intentionally written to disk by the app.
