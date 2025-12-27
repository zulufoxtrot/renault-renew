# GitHub Actions Docker Build Setup

This repository includes a GitHub Actions workflow that automatically builds and publishes the Docker image to GitHub Container Registry (GHCR).

## 🔧 Setup Instructions

### 1. Enable GitHub Container Registry

The workflow is already configured in `.github/workflows/docker-build.yml`. It will automatically run when you push to the repository.

### 2. Make the Image Public (Optional)

After the first build, the image will be private by default. To make it public:

1. Go to your GitHub profile → Packages
2. Find the `renault-scraper` package
3. Click on it → Package settings
4. Scroll down to "Danger Zone"
5. Click "Change visibility" → Make public

### 3. Pull the Pre-built Image

Once the image is published, you can use it instead of building locally.

#### Option A: Use the dedicated compose file
```bash
# Edit docker-compose.ghcr.yml and replace YOUR_USERNAME/YOUR_REPO
# Example: ghcr.io/johndoe/renault-scraper:latest

docker-compose -f docker-compose.ghcr.yml up
```

#### Option B: Modify the main compose file
Edit `docker-compose.yml`:
```yaml
services:
  scraper:
    # Comment out the build section
    # build:
    #   context: .
    #   dockerfile: Dockerfile
    
    # Uncomment and update the image line
    image: ghcr.io/YOUR_USERNAME/YOUR_REPO:latest
```

Then run:
```bash
docker-compose up
```

## 🏷️ Image Tags

The workflow creates multiple tags:

- `latest` - Latest build from main/master branch
- `main` or `master` - Branch-specific tag
- `v1.0.0` - Semantic version tags (when you push git tags)
- `v1.0` - Minor version tag
- `v1` - Major version tag
- `main-sha-abc123` - Commit-specific tags

### Pulling Specific Versions

```bash
# Latest version
docker pull ghcr.io/YOUR_USERNAME/YOUR_REPO:latest

# Specific version
docker pull ghcr.io/YOUR_USERNAME/YOUR_REPO:v1.0.0

# Specific commit
docker pull ghcr.io/YOUR_USERNAME/YOUR_REPO:main-sha-abc123
```

## 🚀 Triggering Builds

The workflow runs automatically on:

- **Push to main/master** - Builds and pushes `latest` tag
- **Push tags (v*)** - Builds and pushes version tags
- **Pull requests** - Builds only (doesn't push)
- **Manual trigger** - Via GitHub Actions UI

### Creating a Release with Version Tag

```bash
# Tag your release
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# This will create:
# - ghcr.io/YOUR_USERNAME/YOUR_REPO:v1.0.0
# - ghcr.io/YOUR_USERNAME/YOUR_REPO:v1.0
# - ghcr.io/YOUR_USERNAME/YOUR_REPO:v1
# - ghcr.io/YOUR_USERNAME/YOUR_REPO:latest
```

## 🔐 Authentication

### For GitHub Actions
No setup needed! The workflow uses the built-in `GITHUB_TOKEN` which has permission to write to GHCR.

### For Local Docker Pull (Private Images)

If your image is private, authenticate first:

```bash
# Create a Personal Access Token (PAT) with 'read:packages' scope
# Go to: Settings → Developer settings → Personal access tokens → Tokens (classic)

# Login to GHCR
echo YOUR_PAT | docker login ghcr.io -u YOUR_USERNAME --password-stdin

# Now you can pull private images
docker-compose pull
```

## 🏗️ Build Configuration

The workflow builds for multiple platforms:
- `linux/amd64` - Standard x86_64 Linux (most servers, Docker Desktop)
- `linux/arm64` - ARM64 Linux (Raspberry Pi 4+, Apple Silicon)

### Multi-platform Support

The published image works on:
- ✅ Linux servers (x86_64)
- ✅ Mac with Intel chips
- ✅ Mac with Apple Silicon (M1/M2/M3)
- ✅ Raspberry Pi 4+ (ARM64)
- ✅ AWS Graviton instances

## 📦 Image Size Optimization

The workflow uses Docker layer caching (GitHub Actions cache) to speed up builds.

To view image details:
```bash
docker images ghcr.io/YOUR_USERNAME/YOUR_REPO
```

## 🔍 Viewing Build Logs

1. Go to your repository on GitHub
2. Click "Actions" tab
3. Click on a workflow run to see logs

## 🛠️ Customization

### Change Image Name

Edit `.github/workflows/docker-build.yml`:
```yaml
env:
  REGISTRY: ghcr.io
  IMAGE_NAME: your-org/custom-name  # Change this
```

### Add Docker Hub

Add Docker Hub credentials to repository secrets:
- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`

Then update the workflow to add Docker Hub login and build steps.

### Build on Schedule

Add to the workflow `on:` section:
```yaml
on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday at midnight
```

## 📊 Monitoring

View package statistics:
- Go to your GitHub profile
- Click "Packages"
- Click on your package to see downloads and versions

## 🧹 Cleanup Old Images

Old image versions accumulate in GHCR. To clean up:

1. Go to Package settings
2. Scroll to "Manage versions"
3. Select and delete old versions

Or use the GitHub API to automate cleanup.

## 🐛 Troubleshooting

### Build Failed - Permission Denied
Make sure the repository has Actions enabled:
- Settings → Actions → General → Allow all actions

### Can't Pull Image - Unauthorized
1. Check if image is public, or
2. Authenticate with `docker login ghcr.io`

### Wrong Image Name
The image name must match your GitHub username/org and repository name:
```
ghcr.io/GITHUB_USERNAME/REPOSITORY_NAME:latest
```

Example:
- GitHub repo: `github.com/johndoe/renault-scraper`
- Image name: `ghcr.io/johndoe/renault-scraper:latest`

## 📚 Additional Resources

- [GitHub Container Registry Docs](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Docker Build Push Action](https://github.com/docker/build-push-action)
- [Docker Metadata Action](https://github.com/docker/metadata-action)
