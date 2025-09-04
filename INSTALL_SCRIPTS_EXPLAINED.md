# Center Deep Installation Scripts - Explained

## 📋 **Two Install Scripts:**

### 1. **`install.sh`** (Main Installer - You're Using This)
- **Purpose**: Production installation script
- **Docker Compose**: Uses `docker-compose.yml` (simplified, standalone)
- **Containers**: 
  - Center Deep (main app)
  - Redis (optional cache)
- **Features**: Latest standalone version without SearXNG dependency

### 2. **`install_opensource.sh`** (Legacy/Alternative)
- **Purpose**: Open source version with more manual setup
- **Docker Compose**: Creates `docker-compose.complete.yml` on the fly
- **Containers**:
  - Center Deep
  - SearXNG (separate container)
  - Redis
- **Note**: This is the OLD architecture before we made Center Deep standalone

## 🚨 **Why Setup CSS Isn't Showing:**

### **Problem**: Docker is using a CACHED image!

When you run `install.sh`, Docker might use a previously built image that doesn't have the new CSS files (`setup-magic.css`).

### **Solution**: Force rebuild without cache

```bash
# Stop current containers
docker-compose down

# Rebuild without using cache
docker-compose build --no-cache center-deep

# Start with new image
docker-compose up -d
```

Or in one command:
```bash
docker-compose down && docker-compose build --no-cache && docker-compose up -d
```

## 🎯 **Which Script to Use:**

**Use `install.sh`** - This is the correct one for the new standalone Center Deep:
- ✅ Uses our new integrated search engine
- ✅ No SearXNG container needed
- ✅ Simpler deployment
- ✅ Your custom UI and features

**Don't use `install_opensource.sh`** unless you specifically want the old architecture with separate SearXNG.

## 🔧 **To Fix Your Current Setup:**

Since the container is rebuilding now (I started it), once it's done:

1. **Clear your browser cache** (Cmd+Shift+R on Mac)
2. **Visit**: http://localhost:8888/setup
3. **You should see**: 
   - Dark purple Magic Unicorn theme
   - White input backgrounds with black text
   - Tooltips on hover
   - Fixed slider positions

## 📁 **What Changed:**

The new CSS file `/static/css/setup-magic.css` needs to be in the Docker image. The rebuild ensures it gets included.

## ⚠️ **Important Notes:**

1. **Always rebuild when changing static files** - Docker doesn't auto-update
2. **Use `--no-cache` flag** when CSS/JS changes are made
3. **The installer works** - it's just using cached images

## 🚀 **For Future Updates:**

When pushing to GitHub, users running the one-liner will get the latest version because they're building fresh. The issue only happens when you have cached images locally.