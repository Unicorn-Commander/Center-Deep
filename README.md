<div align="center">

<img src="static/images/center-deep-logo.png" alt="Center Deep Logo" width="300">

# 🌊 Center Deep

## **The One-Click Privacy Search Engine**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE_MIT)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)](docker-compose.yml)
[![OpenWebUI Compatible](https://img.shields.io/badge/OpenWebUI-Compatible-green)](https://github.com/open-webui/open-webui)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python)](https://python.org)
[![Stars](https://img.shields.io/github/stars/Unicorn-Commander/Center-Deep?style=social)](https://github.com/Unicorn-Commander/Center-Deep)

### 🦄 **Built by [Magic Unicorn Unconventional Technology & Stuff Inc](https://magicunicorn.tech)**

**Center Deep** is a fork of the excellent SearXNG project, reimagined with a focus on simplicity and ease of deployment. We saw many users struggling with SearXNG's setup process, so we created a one-click solution that just works out of the box while adding modern features like AI integration and a beautiful admin panel.

[**🚀 Get Started**](#-quick-start) • [**📸 Screenshots**](#-screenshots) • [**🆚 Compare Editions**](#-center-deep-vs-center-deep-pro) • [**💬 Community**](#-community--support)

</div>

---

## 🎯 **Why Center Deep?**

**Center Deep** is a powerful, privacy-focused metasearch engine that aggregates results from multiple search providers while never tracking you. Built as a modern, user-friendly alternative to complex search solutions, it offers:

- 🔒 **Complete Privacy**: No tracking, no logs, no ads
- 🚀 **One-Click Setup**: Install and run in under 60 seconds
- 🎨 **Beautiful Interface**: Modern, responsive design with dark mode
- 🔧 **Web Admin Panel**: Configure everything through an intuitive UI
- 🤖 **AI-Ready**: Optional integration with OpenWebUI and AI tools
- ⚡ **Fast & Reliable**: Redis caching for blazing-fast results

<table>
<tr>
<td width="50%">

### 🛡️ **Privacy First**
- Zero tracking or user profiling
- No cookies or fingerprinting
- All searches are anonymous
- Self-hosted on your infrastructure

</td>
<td width="50%">

### ✨ **Key Features**
- Aggregates 90+ search engines
- Beautiful setup wizard
- Professional blue theme
- Smart result ranking
- Image proxy for privacy
- Mobile-responsive design

</td>
</tr>
</table>

---

## ⚡ **Quick Start**

### 🎯 **The Truly One-Click Install**

```bash
# Clone and auto-install (handles Docker installation too!)
git clone https://github.com/Unicorn-Commander/Center-Deep.git && cd Center-Deep
./install.sh

# That's literally it. The installer handles everything.
```

**Our installer automatically:**
- ✅ Detects your OS (Linux, macOS, Windows/WSL2)
- ✅ Checks if Docker is installed (installs it if needed!)
- ✅ Sets up Docker Compose
- ✅ Configures Redis with optimized settings
- ✅ Creates secure keys automatically
- ✅ Starts all services
- ✅ Verifies everything is running

### 🐳 **Manual Docker Start** (if you prefer)

```bash
docker compose -f docker-compose.center-deep.yml up -d
# Access at http://localhost:8888
```

> 🔑 **First Run**: Visit `http://localhost:8888/setup` to configure your instance with our beautiful setup wizard!

---

## 🌟 **What's New in Latest Release**

### **v2.0 - Professional Edition**
- ✅ **Removed Background Images**: Cleaner dark theme without distracting gradients
- ✅ **Professional Setup Wizard**: Beautiful blue-themed configuration interface
- ✅ **Improved Search Quality**: Google and Brave prioritized, DuckDuckGo moved to optional
- ✅ **Fixed UI Issues**: Resolved toggle switch overlapping in settings
- ✅ **Docker Optimizations**: Updated to latest Docker Compose spec
- ✅ **Standalone Mode**: No external dependencies required

## 🔧 **Configuration**

### **Included Search Engines**
Center Deep aggregates results from multiple sources, with smart prioritization:

**Premium Engines** (Enabled by default):
- 🔍 **Google** - Highest priority for best results
- 🦁 **Brave** - Privacy-focused with quality results
- 🔷 **Bing** - Microsoft's search engine

**Additional Engines** (Optional):
- DuckDuckGo, Yahoo, Qwant, Startpage, and 80+ more

### **Redis Caching** (Recommended)
Center Deep includes Redis for performance optimization:
```bash
# Runs automatically on port 6385 (non-standard to avoid conflicts)
docker compose -f docker-compose.center-deep.yml up -d
```

### **Option 2: Use Your Existing Redis**
```bash
# Set environment variables before starting
export USE_EXTERNAL_REDIS=true
export EXTERNAL_REDIS_HOST=localhost
export EXTERNAL_REDIS_PORT=6379
export EXTERNAL_REDIS_DB=2  # Optional: specific database number

docker compose -f docker-compose.center-deep.yml up -d
```

### **Option 3: Configure in .env File**
```env
# Edit .env file
USE_EXTERNAL_REDIS=true
EXTERNAL_REDIS_HOST=your-redis-server
EXTERNAL_REDIS_PORT=6379
EXTERNAL_REDIS_PASSWORD=your-password  # If authentication is required
```

> 💡 **Note**: We use port 6385 by default to avoid conflicts with existing Redis installations

---

## 📸 **Screenshots**

<div align="center">

### **🏠 Clean, Modern Search Interface**
<img src="screenshots/main-page.png" alt="Main Search Page" width="800" style="border-radius: 10px; box-shadow: 0 20px 60px rgba(0,0,0,0.3);">

### **🔍 Beautiful Search Results**
<img src="screenshots/search-results.png" alt="Search Results" width="800" style="border-radius: 10px; box-shadow: 0 20px 60px rgba(0,0,0,0.3);">

### **⚙️ Web-Based Admin Dashboard**
<img src="screenshots/settings-full.png" alt="Admin Dashboard" width="800" style="border-radius: 10px; box-shadow: 0 20px 60px rgba(0,0,0,0.3);">

</div>

---

## 🎯 **Core Features**

<div align="center">

| 🔒 **Privacy First** | 🤖 **AI Integration** | 🎨 **Beautiful UI** | ⚙️ **Easy Admin** |
|:---:|:---:|:---:|:---:|
| Zero tracking | OpenWebUI ready | Professional themes | Setup wizard |
| No cookies needed | Tool servers | Dark mode | Web-based config |
| No ads ever | AI-powered search | Clean results | User management |
| Anonymous searching | Native integration | Mobile responsive | Auto-configuration |

</div>

---

## 🛠️ **Tool Servers for OpenWebUI**

### **AI-Powered Search Enhancement**

<table>
<tr>
<td width="25%">

### 🔍 **Search Tool**
Port: `13050`

Web, GitHub, Reddit, Stack Overflow integration

</td>
<td width="25%">

### 🔬 **Deep Search**
Port: `13051`

Multi-layer analysis with link following

</td>
<td width="25%">

### 📊 **Report Gen**
Port: `13052`

Professional reports with citations

</td>
<td width="25%">

### 🎓 **Academic**
Port: `13053`

Scholarly papers with proper formatting

</td>
</tr>
</table>

### **Simple Integration**

```bash
# Only if you want AI tool servers:
docker compose --profile tools up -d

# Add to OpenWebUI:
http://localhost:13050  # Search Tool
http://localhost:13051  # Deep Search  
http://localhost:13052  # Report Generator
http://localhost:13053  # Academic Research
```

---

## 🆚 **Center Deep vs Center Deep Pro**

<div align="center">

### **Choose Your Edition**

| Feature | 🆓 **Center Deep** <br>(Open Source) | 💼 **Center Deep Pro** <br>(Enterprise) |
|:--------|:----------------------------------:|:----------------------------------------:|
| **🔍 Core Search** | ✅ 70+ search engines | ✅ 70+ engines + priority results |
| **🤖 AI Tool Servers** | ✅ 4 basic tools | ✅ Unlimited custom tools |
| **👥 Users** | ✅ Unlimited local users | ✅ SSO/LDAP/OAuth2 |
| **📊 Analytics** | ✅ Basic statistics | ✅ Advanced dashboards + exports |
| **🌐 Proxy Support** | ✅ Basic proxy config | ✅ Rotating proxy pools |
| **📦 Data Export** | ✅ JSON/CSV | ✅ Advanced formats + automation |
| **🔗 API Access** | ✅ Basic API | ✅ Full REST API + webhooks |
| **🎨 Customization** | ✅ Themes | ✅ White-label + custom branding |
| **📞 Support** | Community | 24/7 Enterprise support |
| **💰 Price** | **FREE Forever** | **[Contact Sales](mailto:sales@unicorncommander.com)** |

</div>

> 🚀 **Need enterprise features?** [Get Center Deep Pro](mailto:sales@unicorncommander.com)

---

## 🏗️ **Architecture**

<div align="center">

```mermaid
graph LR
    A[👤 User] --> B[Center Deep<br/>:8888]
    B --> C[Search Aggregation<br/>90+ engines]
    B --> D[Redis Cache<br/>:6385]
    B --> E[Privacy Proxy]
    
    style B fill:#2563eb,stroke:#1e40af,stroke-width:3px,color:#fff
    style D fill:#ef4444,stroke:#dc2626,stroke-width:2px,color:#fff
    style E fill:#10b981,stroke:#059669,stroke-width:2px,color:#fff
```

</div>

---

## 💪 **Advanced Configuration**

<details>
<summary><b>🔧 Environment Variables</b></summary>

```env
# Redis Configuration
USE_EXTERNAL_REDIS=false        # Use your own Redis instance
EXTERNAL_REDIS_HOST=localhost   # Redis server address
EXTERNAL_REDIS_PORT=6379        # Redis port
EXTERNAL_REDIS_PASSWORD=         # Redis password (if required)
EXTERNAL_REDIS_DB=0             # Redis database number

# Admin Setup
ADMIN_USERNAME=ucadmin
ADMIN_PASSWORD=YourSecurePassword

# Search Engine Settings
SEARCH_TIMEOUT=10               # Search timeout in seconds
MAX_RESULTS=20                  # Maximum results per page
SAFE_SEARCH=moderate            # off, moderate, strict

# LLM Integration (Optional)
SEARCH_LLM_API_BASE=https://api.openai.com/v1
SEARCH_LLM_API_KEY=your-api-key
SEARCH_LLM_MODEL=gpt-4
```

</details>

<details>
<summary><b>🐳 Docker Compose Variants</b></summary>

```bash
# Standard deployment (includes Redis on port 6385)
docker compose -f docker-compose.center-deep.yml up -d

# Use existing Redis
USE_EXTERNAL_REDIS=true docker compose -f docker-compose.center-deep.yml up -d

# Development mode with hot reload
docker compose -f docker-compose.dev.yml up

# Production with SSL/TLS
docker compose -f docker-compose.prod.yml up -d

# With monitoring stack (Prometheus + Grafana)
docker compose --profile monitoring up -d
```

</details>

<details>
<summary><b>🔨 Manual Installation</b></summary>

```bash
# Create virtual environment
python3 -m venv venv && source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
nano .env

# Initialize database
python init_admin.py

# Run application
python app.py
```

</details>

---

## 🚀 **Roadmap**

### **Open Source (Forever Free)**
- ✅ Core search functionality from SearXNG
- ✅ Web-based admin dashboard
- ✅ AI tool servers
- ✅ User management
- ✅ Docker one-click deployment
- 🔄 Browser extensions
- 🔄 Mobile apps
- 🔄 Custom search operators

### **Pro Edition (Enterprise)**
- 🎯 AI Agents & Scrapers
- 🎯 Advanced analytics
- 🎯 Full REST API
- 🎯 White-label options
- 🎯 Priority support
- 🎯 Custom integrations
- 🎯 Compliance tools
- 🎯 Audit logging

---

## 🤝 **Contributing**

We welcome contributions! Whether you're fixing bugs, adding features, or improving documentation, we'd love your help.

```bash
# Fork and clone
gh repo fork Unicorn-Commander/Center-Deep

# Create feature branch
git checkout -b feature/awesome-feature

# Make your changes
# ...

# Push and create PR
git push origin feature/awesome-feature
gh pr create
```

See our [Contributing Guide](CONTRIBUTING.md) for details.

---

## 🛡️ **Security**

- 🔐 **Password hashing** with Werkzeug
- 🔒 **Session management** with Flask-Login
- 🛡️ **CSRF protection** on all forms
- 🚫 **Input sanitization** everywhere
- 📦 **Isolated containers** for services
- 🔄 **Regular security updates**

Found a vulnerability? Email `security@unicorncommander.com`

---

## 📚 **Documentation**

<div align="center">

| 📖 [Installation](docs/installation.md) | 🔧 [Configuration](docs/configuration.md) | 🔌 [API Docs](docs/api.md) | 🤖 [Tool Servers](docs/tool-servers.md) | ❓ [FAQ](docs/faq.md) |
|:---:|:---:|:---:|:---:|:---:|

</div>

---

## 💬 **Community & Support**

<div align="center">

### **Join Our Community**

[![GitHub Issues](https://img.shields.io/badge/GitHub-Issues-181717?logo=github)](https://github.com/Unicorn-Commander/Center-Deep/issues)
[![Discussions](https://img.shields.io/badge/GitHub-Discussions-181717?logo=github)](https://github.com/Unicorn-Commander/Center-Deep/discussions)

</div>

---

## 🙏 **Acknowledgments**

- 🔍 **[SearXNG Team](https://github.com/searxng/searxng)** - For creating the amazing foundation we built upon
- 👥 **The Community** - For feedback, contributions, and making this project better
- 🦄 **[Unicorn Commander](https://unicorncommander.com)** - For making this project possible
- ⚓ **The Commodore** - Our mascot guiding us through the deep web

---

<div align="center">

## ⭐ **Star us if Center Deep makes your search easier!**

---

### **🦄 A [Magic Unicorn](https://magicunicorn.tech) Production**

**[Unicorn Commander](https://unicorncommander.com)** - Enterprise Division

Built with ❤️ and 🦄 to make privacy-first search accessible to everyone

[**Website**](https://center-deep.com) • [**Pro Version**](mailto:sales@unicorncommander.com) • [**Issues**](https://github.com/Unicorn-Commander/Center-Deep/issues)

</div>