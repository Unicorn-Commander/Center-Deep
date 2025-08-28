# Frequently Asked Questions

## General Questions

### What is Center Deep?

Center Deep is a privacy-focused metasearch engine based on SearXNG. It aggregates results from 70+ search engines while protecting your privacy. Key features include a beautiful web-based setup wizard, admin dashboard, and AI tool integration.

### How is Center Deep different from SearXNG?

While SearXNG is excellent, Center Deep adds:
- ✨ One-click installation with automatic Docker setup
- 🎨 Beautiful web-based setup wizard (like WordPress)
- 👨‍💼 Admin dashboard for easy management
- 🤖 AI tool server integration for OpenWebUI
- 🎨 Modern, responsive themes
- 📦 Simplified deployment and configuration

### Is Center Deep really free?

Yes! Center Deep is 100% free and open source under the AGPL-3.0 license. You can use it personally or commercially without any fees.

### What's the difference between Center Deep and Center Deep Pro?

- **Center Deep** (this version): Free, open-source, community-supported
- **Center Deep Pro**: Enterprise features, priority support, advanced analytics (separate product)

## Installation

### Do I need Docker?

Docker is recommended but not required. Our installer can automatically install Docker for you, or you can run Center Deep natively with Python.

### What are the system requirements?

- **Minimum**: 2GB RAM, 2GB storage, any modern OS
- **Recommended**: 4GB RAM, 10GB storage, Linux/macOS
- **Docker**: Version 20.10+ (installer handles this)

### Can I run this on a Raspberry Pi?

Yes! Center Deep works on ARM devices including Raspberry Pi 4 and newer. Use the standard installation process.

### The installer fails, what should I do?

1. Check Docker is running: `docker --version`
2. Ensure ports are free: `lsof -i :8888`
3. Run with sudo if needed: `sudo ./install.sh`
4. Check [Troubleshooting Guide](troubleshooting.md)

## Configuration

### How do I change the admin password?

Two ways:
1. During initial setup wizard
2. Later via Admin Panel → Settings → Change Password

### Can I use my existing Redis instance?

Yes! Edit `.env`:
```bash
USE_EXTERNAL_REDIS=true
EXTERNAL_REDIS_HOST=your-redis-host
EXTERNAL_REDIS_PORT=6379
```

### How do I change the port?

Edit `docker-compose.center-deep.yml`:
```yaml
ports:
  - "YOUR_PORT:8080"  # Change YOUR_PORT
```

### Can I disable certain search engines?

Yes, in the Admin Panel → Search Engines, toggle engines on/off.

## Privacy & Security

### Does Center Deep track users?

No! Center Deep has:
- Zero tracking or analytics
- No cookies (except session-only)
- No search logs
- No user profiling
- IP addresses not stored

### Is HTTPS supported?

Yes! For production, use a reverse proxy like Nginx or Caddy with SSL certificates. See [Production Setup](production.md).

### Can I use a VPN or proxy?

Absolutely! Center Deep works with VPNs and supports configuring upstream proxies for enhanced privacy.

### Are searches encrypted?

- Local searches to Center Deep can use HTTPS
- Searches to upstream engines use their protocols
- Enable HTTPS in production for full encryption

## Usage

### What are search bangs?

Bangs let you search specific engines directly:
- `!g query` - Google
- `!ddg query` - DuckDuckGo  
- `!w query` - Wikipedia
- `!gh query` - GitHub

### How do I search a specific website?

Use the `site:` operator:
```
site:reddit.com your search
```

### Can I search for files?

Yes! Use:
```
filetype:pdf climate change
filetype:doc resume template
```

### What search operators are supported?

- `"exact phrase"` - Exact match
- `-exclude` - Exclude term
- `site:domain.com` - Site search
- `filetype:ext` - File type
- `intitle:term` - Title search

## Integration

### How do I connect to OpenWebUI?

1. Start Center Deep tool servers
2. In OpenWebUI, add tool:
   - URL: `http://localhost:13050/`
   - Name: Center Deep Search

### Can I use the API?

Yes! Basic API endpoints:
- `/api/search?q=query` - Search
- `/api/stats` - Statistics
- `/api/health` - Health check

### Does it work with browser extensions?

Yes, Center Deep is compatible with SearXNG browser extensions.

## Troubleshooting

### Search returns no results

1. Check internet connection
2. Verify search engines are enabled
3. Try different search terms
4. Check Docker logs: `docker compose logs`

### Admin panel won't load

1. Ensure you're logged in
2. Clear browser cache
3. Check URL: `http://localhost:8888/admin`
4. Verify admin account exists

### Docker containers keep restarting

1. Check logs: `docker compose logs center-deep`
2. Verify port availability
3. Check disk space: `df -h`
4. Ensure Redis is running

### Installation fails on Windows

1. Ensure WSL2 is installed
2. Use PowerShell as Administrator
3. Install Docker Desktop for Windows
4. Run: `wsl --install` first

## Advanced

### Can I contribute to the project?

Yes! We welcome contributions. See [CONTRIBUTING.md](../CONTRIBUTING.md).

### How do I report security issues?

Please see our [Security Policy](../SECURITY.md). Email security@magicunicorn.tech for vulnerabilities.

### Is commercial use allowed?

Yes! The AGPL-3.0 license allows commercial use. You must share source code modifications if you provide network access to users.

### Can I white-label Center Deep?

The open-source version requires attribution. For white-labeling, consider Center Deep Pro.

## Support

### Where can I get help?

1. Check this FAQ
2. Read [Documentation](README.md)
3. Search [GitHub Issues](https://github.com/Unicorn-Commander/Center-Deep/issues)
4. Create a new issue
5. Email: support@magicunicorn.tech

### Is there paid support?

Community support is free. For enterprise support, consider Center Deep Pro.

### How do I stay updated?

- Star the [GitHub repo](https://github.com/Unicorn-Commander/Center-Deep)
- Watch for releases
- Follow [@MagicUnicornTech](https://twitter.com/MagicUnicornTech)

---

**Still have questions?** Open an [issue on GitHub](https://github.com/Unicorn-Commander/Center-Deep/issues)!