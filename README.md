<div align="center">

<img src="static/images/center-deep-logo.png" alt="Center Deep Logo" width="200">

# 🌊 Center Deep

### The Privacy-First Search Engine That Replaced SearXNG

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE_MIT)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)](docker-compose.yml)
[![OpenWebUI Compatible](https://img.shields.io/badge/OpenWebUI-Compatible-green)](https://github.com/open-webui/open-webui)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python)](https://python.org)

**Center Deep** is the evolution of metasearch - a privacy-focused search engine that goes beyond what SearXNG offered. Built from the ground up with modern architecture, AI integration, and a beautiful UI that actually makes you want to search.

[**Live Demo**](#) | [**Documentation**](docs/) | [**Pro Version**](#pro-features) | [**Discord**](#)

</div>

---

## ✨ Why Center Deep?

We loved SearXNG, but it was time for something better. Center Deep isn't just another fork - it's a complete reimagining of what a privacy-first search engine should be in 2025.

### 🚀 **What Makes Us Different**

| Feature | SearXNG | Center Deep |
|---------|---------|-------------|
| **UI/UX** | Functional but dated | Modern, responsive, beautiful |
| **AI Integration** | None | Native LLM support with tool servers |
| **Admin Panel** | Basic config files | Full web-based admin dashboard |
| **Docker Setup** | Complex multi-file | Single command deployment |
| **OpenWebUI** | Not supported | Native integration |
| **Redis Caching** | Basic | Search-optimized configuration |
| **User Management** | None | Full authentication system |

## 🎯 Key Features

### 🔒 **Privacy First**
- **Zero tracking** - We don't store your searches
- **No cookies** required for searching  
- **No ads**, no BS, just results
- **IP rotation** support via proxy configuration
- **Encrypted connections** throughout

### 🤖 **AI-Powered Tools**
- **4 Specialized Tool Servers** for OpenWebUI:
  - 🔍 **Search Tool** - Web, GitHub, Reddit, Stack Overflow
  - 🔬 **Deep Search** - Multi-source aggregation with analysis
  - 📊 **Report Generator** - Professional reports with citations
  - 🎓 **Academic Research** - Scholarly papers with proper citations

### 🎨 **Beautiful Interface**
- **Dark/Light themes** with smooth transitions
- **Responsive design** that works everywhere
- **Floating assistant** (our mascot, the unicorn diver!)
- **Clean search results** with source attribution
- **Image & video search** with preview galleries

### ⚙️ **Admin Dashboard**
- **Web-based configuration** - No more config files!
- **LLM provider management** with model auto-discovery
- **User management** with role-based access
- **Real-time statistics** and monitoring
- **Tool server control** - Start/stop services from the UI

## 📦 Installation

### 🐳 Quick Start with Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/Center-Deep.git
cd Center-Deep

# Start everything with one command
docker compose -f docker-compose.center-deep.yml up -d

# Access at http://localhost:8888
```

**That's it!** 🎉 Center Deep is now running with:
- Main search engine on port `8888`
- Redis cache on port `6385`
- Tool servers ready on ports `13050-13053`

### 🔧 Manual Installation

<details>
<summary>Click for manual setup instructions</summary>

```bash
# Install Python 3.11+
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your settings

# Initialize database
python init_admin.py

# Run the application
python app.py
```

</details>

## 🚀 Quick Configuration

### 1️⃣ **Login to Admin Panel**

Navigate to `http://localhost:8888/admin`

```
Username: ucadmin
Password: MagicUnicorn!8-)
```

> ⚠️ **Change the default password immediately!**

### 2️⃣ **Configure Search Engines**

In the admin panel, go to **Search Engine** and select your preferred sources:
- Google, Bing, DuckDuckGo
- Brave, Qwant, StartPage
- And many more!

### 3️⃣ **Add LLM Providers** (Optional)

For AI-powered features:
1. Go to **LLM Config**
2. Click **+ Add LLM Provider**
3. Enter your API credentials
4. Click **🔍 Fetch Available Models**
5. Select your model and save

## 🛠️ Tool Servers for OpenWebUI

### Enabling Tool Servers

```bash
# Start all tool servers
docker compose --profile tools -f docker-compose.center-deep.yml up -d
```

### Integrating with OpenWebUI

Add these URLs to your OpenWebUI tool configuration:

| Tool | URL | Purpose |
|------|-----|---------|
| **Search** | `http://localhost:13050` | General web search |
| **Deep Search** | `http://localhost:13051` | In-depth research |
| **Report Gen** | `http://localhost:13052` | Professional reports |
| **Academic** | `http://localhost:13053` | Academic papers |

## 🎨 Customization

### Environment Variables

```env
# Redis Configuration
USE_EXTERNAL_REDIS=false  # Use your own Redis?
EXTERNAL_REDIS_HOST=localhost
EXTERNAL_REDIS_PORT=6379

# Admin Credentials
ADMIN_USERNAME=ucadmin
ADMIN_PASSWORD=YourSecurePassword

# LLM Configuration (Optional)
SEARCH_LLM_API_BASE=https://api.openai.com/v1
SEARCH_LLM_API_KEY=your-api-key
SEARCH_LLM_MODEL=gpt-3.5-turbo
```

### Docker Compose Options

```bash
# Use existing Redis
USE_EXTERNAL_REDIS=true docker compose up -d

# Start with tool servers
docker compose --profile tools up -d

# Development mode
docker compose -f docker-compose.dev.yml up
```

## 📊 Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│    User     │────▶│  Center Deep │────▶│   Search    │
└─────────────┘     │              │     │   Engines   │
                    │   Port 8888  │     └─────────────┘
                    │              │
┌─────────────┐     │              │     ┌─────────────┐
│  OpenWebUI  │────▶│              │────▶│    Redis    │
└─────────────┘     └──────────────┘     │    Cache    │
                            │             └─────────────┘
                            │
                    ┌───────▼────────┐
                    │  Tool Servers  │
                    │  13050-13053   │
                    └────────────────┘
```

## 🚀 Pro Features

### Coming Soon in Center Deep Pro

- **🤖 AI Agents & Data Scrapers**
  - RSS feed monitoring
  - GitHub repository tracking
  - Reddit community scanning
  - Custom URL watchers

- **📊 Advanced Analytics**
  - Search pattern analysis
  - User behavior insights
  - Performance metrics
  - Custom dashboards

- **🔗 Full REST API**
  - Complete API access
  - Webhook support
  - Rate limiting controls
  - API key management

- **🎨 Custom Themes**
  - Theme builder
  - CSS customization
  - Logo replacement
  - White-label options

## 📸 Screenshots

<div align="center">
<table>
<tr>
<td><img src="screenshots/main-page.png" alt="Main Search Page" width="400" /></td>
<td><img src="screenshots/search-results.png" alt="Search Results" width="400" /></td>
</tr>
<tr>
<td colspan="2"><img src="screenshots/settings-full.png" alt="Admin Dashboard" width="800" /></td>
</tr>
</table>
</div>

## 🤝 Contributing

We love contributions! Whether it's:
- 🐛 Bug reports
- 💡 Feature requests
- 🔧 Pull requests
- 📖 Documentation improvements

Check out our [Contributing Guide](CONTRIBUTING.md) to get started.

## 📚 Documentation

- [**Installation Guide**](docs/installation.md)
- [**Configuration Guide**](docs/configuration.md)
- [**API Documentation**](docs/api.md)
- [**Tool Server Guide**](docs/tool-servers.md)
- [**Troubleshooting**](docs/troubleshooting.md)

## 🛡️ Security

Center Deep takes security seriously:
- Regular security updates
- Dependency scanning
- Input sanitization
- Rate limiting
- Secure password hashing

Found a vulnerability? Please email security@center-deep.com

## 📄 License

Center Deep is MIT licensed. See [LICENSE](LICENSE_MIT) for details.

## 🙏 Acknowledgments

- The original SearXNG team for inspiration
- Our amazing community of contributors
- The unicorn diver for being an awesome mascot 🦄🤿

## 💬 Community & Support

- **GitHub Issues**: [Report bugs](https://github.com/yourusername/Center-Deep/issues)
- **Discussions**: [Ask questions](https://github.com/yourusername/Center-Deep/discussions)

## 🌟 Star History

Give us a star if you find Center Deep useful! ⭐

---

<div align="center">

**Built with ❤️ by the Center Deep Team**

[Documentation](docs/) • [Report Bug](issues) • [Request Feature](issues)

</div>