# Deployment checklist

- [x] Python source syntax compiles in the build environment.
- [x] RDKit chemistry tests pass (5 tests).
- [x] PDF report test passes: generated PDF opens, expected sections and signature areas exist, and 2D precedes 3D.
- [x] Example PDF rendered to page images for layout inspection; structure section heading/image ordering corrected.
- [x] No real API credentials included; `.env.example` contains empty placeholders.
- [x] Dockerfile and Render configuration included.
- [ ] Install runtime dependencies on the target deployment platform.
- [ ] Launch Streamlit and verify UI in a browser.
- [ ] Verify outbound PubChem and 3Dmol.js CDN connectivity on the target host.
- [ ] Configure optional AI provider secrets if desired.
- [ ] Deploy to a hosting provider and verify its public URL.

**Limitations:** GitHub could not be reached from the build environment, and Streamlit could not be installed because package-index network access was unavailable. The app has not been browser-smoke-tested or deployed live. The source repository was not retrieved, so this is a new implementation from the supplied specification rather than a verified refactor of the existing repository.
