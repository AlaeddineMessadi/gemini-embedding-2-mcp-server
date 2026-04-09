# Releasing

This repository is intended to keep `main` in a releasable state.

## Release Model

- Pull requests land in `main` only after CI is green
- Tags starting with `v` trigger the automated release workflow
- The release workflow:
  - runs tests
  - builds Python distributions
  - creates the GitHub release and uploads artifacts
  - publishes the Python package to PyPI via trusted publishing
  - publishes a Docker image to GHCR

## Standard Release Flow

1. Merge tested changes into `main`
2. Update version and changelog
3. Create and push a tag:

```bash
git tag v1.2.0
git push origin v1.2.0
```

4. Let GitHub Actions build:
   - release artifacts in `dist/`
   - release notes
   - PyPI package publish
   - GHCR Docker image

## Stable Install Channel

- Long term, stable installs should come from PyPI
- Until the first PyPI publish succeeds, keep user-facing install examples pinned to Git release tags
- After PyPI is live, switch the default `uvx` examples in the README and client snippets to `uvx gemini-embedding-2-mcp-server`

## One-Time PyPI Setup

1. Create the `gemini-embedding-2-mcp-server` project on PyPI
2. Configure a trusted publisher for this repository and release workflow
3. Add the repository variable `ENABLE_PYPI_PUBLISH=true`
4. Push the next `v*` tag to let GitHub Actions publish automatically

## Collaboration Notes

- Avoid using `main` as an experimental branch
- Prefer small pull requests with tests and doc updates
- Treat README and docs as release-critical, not optional
- Keep installation examples aligned with the actual supported release channel
