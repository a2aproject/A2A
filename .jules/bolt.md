## 2024-04-16 - A2A SDK Build Optimization
**Learning:** The build_sdk_docs.sh script was slow because it was running sequentially.
**Action:** Use '-j auto' with sphinx-build to enable parallel processing and speed up the build.
