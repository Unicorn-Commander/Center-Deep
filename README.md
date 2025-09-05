<div align="center">

![Center Deep Homepage](docs/images/center-deep-homepage.png)
![Center Deep Results](docs/images/center-deep-results.png)

# 🌊 Center Deep

## **The One-Click Privacy Search Engine**

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)](docker-compose.yml)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python)](https://python.org)
[![Stars](https://img.shields.io/github/stars/Unicorn-Commander/Center-Deep?style=social)](https://github.com/Unicorn-Commander/Center-Deep)

### 🦄 **Built by [Magic Unicorn Unconventional Technology & Stuff Inc](https://magicunicorn.tech)**

**Center Deep** is a fork of the excellent SearXNG project, reimagined with a focus on simplicity and ease of deployment. We saw many users struggling with SearXNG's setup process, so we created a one-click solution that just works out of the box while adding a beautiful Magic Unicorn theme and optimized performance.

[**🚀 Get Started**](#-quick-start) • [**✨ Features**](#-why-center-deep) • [**🔧 Configuration**](#-configuration) • [**💬 Community**](#-community--support)

</div>

---

## 🎯 **Why Center Deep?**

**Center Deep** is a powerful, privacy-focused metasearch engine that aggregates results from multiple search providers while never tracking you. Built as a modern, user-friendly alternative to complex search solutions, it offers:

- 🔒 **Complete Privacy**: No tracking, no logs, no ads, no cookies
- 🚀 **One-Click Setup**: Install and run in under 60 seconds
- 🎨 **Beautiful Interface**: Magic Unicorn theme with purple gradients
- 🌊 **250+ Search Engines**: Aggregate results from across the web
- ⚡ **Redis Caching**: Blazing-fast performance out of the box
- 🐳 **Docker-Based**: Runs anywhere Docker runs

<table>
<tr>
<td width="50%">

### 🛡️ **Privacy First**
- Zero tracking or user profiling
- No cookies or fingerprinting
- All searches are anonymous
- Self-hosted on your infrastructure
- Proxied results for extra privacy

</td>
<td width="50%">

### ✨ **Key Features**
- Aggregates 250+ search engines
- Beautiful Magic Unicorn theme
- Dark mode by default
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
# Clone and auto-install
git clone https://github.com/Unicorn-Commander/Center-Deep.git && cd Center-Deep
./install.sh

# That's literally it. The installer handles everything.
```

**Our installer automatically:**
- ✅ Checks if Docker is installed
- ✅ Sets up Docker Compose
- ✅ Configures Redis with optimized settings
- ✅ Creates environment configuration
- ✅ Builds and starts all services
- ✅ Verifies everything is running

**Access Center Deep at:**
- **http://localhost:8888**
- **http://0.0.0.0:8888** (from other devices on your network)

## 🛠️ Manual Installation

If you prefer manual setup:

```bash
# Clone the repository
git clone https://github.com/YourUsername/Center-Deep.git
cd Center-Deep

# Create environment file
cp .env.example .env

# Start Center Deep
docker-compose up --build -d
```

## 📋 Management Commands

```bash
# Start Center Deep
docker-compose up -d

# Stop Center Deep
docker-compose down

# View logs
docker-compose logs -f center-deep

# Restart Center Deep
docker-compose restart

# Update Center Deep
git pull
docker-compose up --build -d
```

## ⚙️ Configuration

Edit the `.env` file to customize your installation:

```bash
# Generate a new secret key
openssl rand -hex 32
```

## 🌐 Access

- **Main Interface**: http://localhost:8888
- **External Access**: http://0.0.0.0:8888 (accessible from other devices on your network)

## 🔒 Privacy

Center Deep is designed with privacy as the top priority:
- Zero user tracking or profiling
- No search history storage
- All searches are encrypted and proxied
- Third-party engines never see your IP address
- Open source and transparent

## 🆚 **Center Deep vs Center Deep Pro**

<div align="center">

### **Choose Your Edition**

| Feature | 🆓 **Center Deep** <br>(Open Source) | 💼 **Center Deep Pro** <br>(Coming Soon) |
|:--------|:----------------------------------:|:----------------------------------------:|
| **🔍 Core Search** | ✅ 250+ search engines | ✅ 250+ engines + AI ranking |
| **🎨 Interface** | ✅ Magic Unicorn theme | ✅ Multiple themes + customization |
| **⚡ Performance** | ✅ Redis caching | ✅ Advanced caching + CDN |
| **👥 Users** | ✅ Unlimited local users | ✅ User accounts & preferences |
| **📊 Analytics** | ❌ None (privacy-first) | ✅ Private analytics dashboard |
| **🔗 API Access** | ❌ Not included | ✅ Full REST API |
| **🤖 AI Features** | ❌ Not included | ✅ AI-powered summaries & ranking |
| **🎯 Custom Search** | ❌ Not included | ✅ Custom search operators |
| **📞 Support** | Community | Priority support |
| **💰 Price** | **FREE Forever** | **[Join Waitlist](mailto:hello@magicunicorn.tech)** |

</div>

> 🚀 **Want early access to Center Deep Pro?** [Join the waitlist](mailto:hello@magicunicorn.tech)

---

## 🏗️ **Architecture**

<div align="center">

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│   Browser   │────▶│  Center Deep │────▶│ Search Engines  │
└─────────────┘     │   (SearXNG)  │     │  (250+ sites)   │
                    └──────┬───────┘     └─────────────────┘
                           │
                    ┌──────▼───────┐
                    │    Redis     │
                    │   (Cache)    │
                    └──────────────┘
```

</div>

---

## 🤝 **Contributing**

We welcome contributions! Whether you're fixing bugs, adding features, or improving documentation, we'd love your help.

```bash
# Fork and clone
git clone https://github.com/Unicorn-Commander/Center-Deep.git

# Create feature branch
git checkout -b feature/awesome-feature

# Make your changes and commit
git add .
git commit -m "Add awesome feature"

# Push and create PR
git push origin feature/awesome-feature
```

---

## 🛡️ **Security & Privacy**

- 🔐 **No user tracking** - We don't store any search queries
- 🔒 **No cookies** - Sessions are stateless
- 🛡️ **Proxied results** - Your IP never reaches search engines
- 🚫 **No JavaScript tracking** - Clean, tracking-free interface
- 📦 **Isolated containers** - Secure Docker deployment
- 🔄 **Regular updates** - Built on actively maintained SearXNG

Found a vulnerability? Email `security@magicunicorn.tech`

---

## 💬 **Community & Support**

<div align="center">

### **Join Our Community**

[![GitHub Issues](https://img.shields.io/badge/GitHub-Issues-181717?logo=github)](https://github.com/Unicorn-Commander/Center-Deep/issues)
[![Discussions](https://img.shields.io/badge/GitHub-Discussions-181717?logo=github)](https://github.com/Unicorn-Commander/Center-Deep/discussions)
[![Email](https://img.shields.io/badge/Email-hello@magicunicorn.tech-blue)](mailto:hello@magicunicorn.tech)

</div>

---

## 🙏 **Acknowledgments**

- 🔍 **[SearXNG Team](https://github.com/searxng/searxng)** - For creating the amazing foundation we built upon
- 👥 **The Community** - For feedback, contributions, and making this project better
- 🦄 **[Magic Unicorn](https://magicunicorn.tech)** - For making this project possible
- ⚡ **[Redis](https://redis.io)** - For the blazing-fast caching layer

---

<div align="center">

## ⭐ **Star us if Center Deep makes your search easier!**

---

### **🦄 A [Magic Unicorn](https://magicunicorn.tech) Production**

Built with ❤️ and 🦄 to make privacy-first search accessible to everyone

**🔒 Private & Secure | 🌊 250+ Search Engines | 🦄 Powered by Magic**

**Center Deep v1.0** - Your gateway to the deep web, without the creepy tracking

***You can't get deeper than Center Deep***

[**Website**](https://center-deep.com) • [**Pro Version**](mailto:hello@magicunicorn.tech) • [**Issues**](https://github.com/Unicorn-Commander/Center-Deep/issues)

</div>