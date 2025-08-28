# Installation Guide

## Prerequisites

- **Operating System**: Linux, macOS, or Windows (with WSL2)
- **Docker**: Version 20.10 or higher (installer will handle this)
- **RAM**: Minimum 2GB, recommended 4GB+
- **Storage**: Minimum 2GB free space

## 🚀 One-Click Installation

The easiest way to install Center Deep:

```bash
# Clone and auto-install
git clone https://github.com/Unicorn-Commander/Center-Deep.git
cd Center-Deep
./install.sh
```

The installer automatically:
- ✅ Detects your operating system
- ✅ Installs Docker if needed
- ✅ Sets up Docker Compose
- ✅ Configures all services
- ✅ Creates secure keys
- ✅ Starts Center Deep
- ✅ Opens the setup wizard

## 🐳 Docker Installation (Manual)

If you prefer manual control:

```bash
# Clone the repository
git clone https://github.com/Unicorn-Commander/Center-Deep.git
cd Center-Deep

# Copy environment template
cp .env.example .env

# Edit configuration (optional)
nano .env

# Start services
docker compose -f docker-compose.center-deep.yml up -d

# Verify installation
docker compose ps
```

## 🖥️ Native Installation (Advanced)

For running without Docker:

```bash
# Install Python 3.11+
python3 --version  # Verify version

# Clone repository
git clone https://github.com/Unicorn-Commander/Center-Deep.git
cd Center-Deep

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python init_admin.py

# Run application
python app.py
```

## 📝 Post-Installation Setup

1. **Access the Setup Wizard**
   - Navigate to: `http://localhost:8888/setup`
   - The wizard will guide you through:
     - Creating admin account
     - Selecting search engines
     - Configuring privacy settings
     - Choosing theme

2. **Default Credentials** (if skipping wizard)
   - Username: `ucadmin`
   - Password: `MagicUnicorn!8-)`
   - **⚠️ Change these immediately!**

3. **Admin Panel Access**
   - URL: `http://localhost:8888/admin`
   - Use credentials from setup wizard

## 🔧 Configuration Options

### Redis Configuration

**Option 1: Use Included Redis** (Default)
```yaml
# Runs on port 6385 to avoid conflicts
USE_EXTERNAL_REDIS=false
```

**Option 2: Use External Redis**
```yaml
USE_EXTERNAL_REDIS=true
EXTERNAL_REDIS_HOST=localhost
EXTERNAL_REDIS_PORT=6379
```

### Port Configuration

Default ports:
- **8888**: Main application
- **6385**: Redis (internal)
- **13050-13053**: Tool servers (optional)

To change ports, edit `docker-compose.center-deep.yml`:
```yaml
ports:
  - "YOUR_PORT:8080"
```

## 🚀 Quick Verification

Run this command to verify your installation:

```bash
curl -I http://localhost:8888
```

Expected response:
```
HTTP/1.1 200 OK
Server: Center-Deep
```

## 🆘 Troubleshooting

### Docker Issues

```bash
# Check Docker status
docker --version
systemctl status docker

# View logs
docker compose logs -f center-deep

# Restart services
docker compose restart
```

### Port Conflicts

If port 8888 is in use:
```bash
# Find process using port
lsof -i :8888

# Change port in docker-compose.yml
ports:
  - "8889:8080"
```

### Permission Issues

```bash
# Fix permissions
sudo chown -R $USER:$USER .
chmod +x install.sh
```

## 📚 Next Steps

- [Configure your instance](configuration.md)
- [Learn about search features](search-features.md)
- [Set up for production](production.md)
- [Integrate with OpenWebUI](toolservers.md)