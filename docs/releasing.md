# Releasing

This repository is intended to keep `main` in a releasable state.

## Release Model

- Pull requests land in `main` only after CI is green
- Tags starting with `v` trigger the automated release workflow
- The release workflow:
  - runs tests
  - builds Python distributions
  - creates or updates the GitHub release
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
   - GHCR Docker image

## Collaboration Notes

- Avoid using `main` as an experimental branch
- Prefer small pull requests with tests and doc updates
- Treat README and docs as release-critical, not optional
- Keep installation examples aligned with the actual supported release channel
