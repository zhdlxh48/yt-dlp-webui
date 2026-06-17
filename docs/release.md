# Release

1. Update `pyproject.toml` version.
2. Commit changes.
3. Tag with the same version, for example `v0.1.0`.
4. Push `main` and the tag.
5. GitHub Actions builds `yt-dlp-webui-windows-x64-v0.1.0.zip`.

The workflow uses `GITHUB_TOKEN` and `contents: write`; no personal access token is required.

