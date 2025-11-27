# Publishing AeroNavX to PyPI

This guide explains how to publish AeroNavX to PyPI using GitHub Actions and Trusted Publishers.

## Prerequisites

1. A PyPI account at https://pypi.org/
2. GitHub repository with the workflow file

## Step 1: Configure PyPI Trusted Publisher

1. Go to https://pypi.org/manage/account/publishing/
2. Scroll to "Add a new pending publisher"
3. Select **GitHub** tab
4. Fill in the form:

   ```
   PyPI Project Name: aeronavx
   Owner: teyfikoz
   Repository name: AeroNavX
   Workflow name: publish.yml
   Environment name: pypi
   ```

5. Click **Add**

## Step 2: Create GitHub Environment

1. Go to your GitHub repository: https://github.com/teyfikoz/AeroNavX
2. Click **Settings** → **Environments**
3. Click **New environment**
4. Name it: `pypi`
5. (Optional) Add protection rules:
   - Required reviewers
   - Wait timer
   - Deployment branches (only `main`)

## Step 3: Create a Release

The workflow triggers automatically when you create a GitHub release:

```bash
# Tag the current commit
git tag -a v0.1.0 -m "Release version 0.1.0"

# Push the tag to GitHub
git push origin v0.1.0
```

Then on GitHub:
1. Go to **Releases** → **Create a new release**
2. Choose the tag you just created (v0.1.0)
3. Write release notes
4. Click **Publish release**

The GitHub Action will automatically:
- Build the package
- Upload to PyPI using Trusted Publishing

## Step 4: Verify Publication

After the workflow completes, check:
- https://pypi.org/project/aeronavx/
- Install and test: `pip install aeronavx`

## Manual Publication (Alternative)

If you prefer manual publishing:

```bash
# Install build tools
pip install build twine

# Build the package
python -m build

# Upload to PyPI
twine upload dist/*
```

You'll need a PyPI API token for this method.

## Version Bumping

Update version in `pyproject.toml`:

```toml
[project]
version = "0.1.1"  # Increment this
```

Then create a new release with the new version tag.

## Troubleshooting

**Error: "Project does not exist"**
- Make sure you added the Trusted Publisher on PyPI first
- The first release will create the project automatically

**Error: "Environment not found"**
- Create the `pypi` environment in GitHub repository settings

**Error: "Permission denied"**
- Ensure the workflow has `id-token: write` permission
- Check that the workflow file name matches what you entered in PyPI

## Security Notes

- Never commit PyPI tokens to the repository
- Use GitHub Environments for additional protection
- Enable branch protection on `main`
- Require pull request reviews before merging
