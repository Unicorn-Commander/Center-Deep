# Quick Start Guide

Get Center Deep running in under 5 minutes!

## 🚀 Fastest Setup

```bash
# One command to rule them all
git clone https://github.com/Unicorn-Commander/Center-Deep.git && \
cd Center-Deep && \
./install.sh
```

That's it! The installer handles everything.

## 🌊 First Search

1. **Open your browser**: http://localhost:8888
2. **Complete setup wizard** (2 minutes)
3. **Start searching!** No login required

## ⚙️ Essential Configuration

### 1. Change Admin Password

During setup wizard, or later in admin panel:
- Navigate to: http://localhost:8888/admin
- Click "Settings" → "Change Password"

### 2. Select Your Search Engines

In admin panel → "Search Engines":
- ✅ **Brave** - Privacy-focused, great results
- ✅ **DuckDuckGo** - No tracking
- ✅ **Google** - Most comprehensive
- ✅ **Startpage** - Google results, private
- ✅ **Qwant** - European privacy engine

### 3. Choose Your Theme

Three beautiful themes included:
- 🌙 **Dark Theme** - Easy on the eyes
- ☀️ **Light Theme** - Clean and bright
- 🦄 **Magic Unicorn** - Colorful gradients

## 🎯 Key Features

### Search Operators

- **Exact phrase**: `"your exact phrase"`
- **Exclude terms**: `python -snake`
- **Site search**: `site:reddit.com`
- **File type**: `filetype:pdf`

### Keyboard Shortcuts

- `/` - Focus search box
- `Ctrl+K` - Quick search
- `Esc` - Clear search
- `Tab` - Navigate results

### Search Categories

Click category tabs for specialized searches:
- 🌐 **General** - Web results
- 🖼️ **Images** - Image search
- 📰 **News** - Latest news
- 🎬 **Videos** - Video content
- 📚 **Files** - Documents and files
- 🗺️ **Maps** - Location search
- 🎓 **Science** - Academic papers

## 🔒 Privacy Features

Center Deep protects your privacy by default:

- ✅ **No tracking** - Zero analytics or telemetry
- ✅ **No cookies** - Session-only, no persistence
- ✅ **No logs** - Searches not recorded
- ✅ **Proxy support** - Hide your IP
- ✅ **Image proxy** - Images served through Center Deep

## 🤖 AI Integration (Optional)

Connect with OpenWebUI for AI-powered search:

1. **Install OpenWebUI** (if not already)
2. **Enable Tool Servers** in admin panel
3. **Add to OpenWebUI**:
   ```
   URL: http://localhost:13050/
   Name: Center Deep Search
   ```

## 📊 Admin Dashboard

Access at: http://localhost:8888/admin

Quick tasks:
- **Monitor stats** - Search volume, response times
- **Manage users** - Add/remove users
- **Configure engines** - Enable/disable sources
- **View logs** - System health
- **Update settings** - Customize instance

## 🚨 Common Tasks

### Restart Services

```bash
docker compose restart
```

### View Logs

```bash
docker compose logs -f center-deep
```

### Update Center Deep

```bash
git pull
docker compose down
docker compose up -d --build
```

### Backup Configuration

```bash
cp .env .env.backup
cp -r instance instance.backup
```

## 💡 Pro Tips

1. **Bookmark the search page** for quick access
2. **Set as default search** in your browser
3. **Use bangs** like `!g` for Google, `!ddg` for DuckDuckGo
4. **Enable infinite scroll** in preferences
5. **Customize results per page** (10-100)

## 🆘 Need Help?

- Check [Troubleshooting Guide](troubleshooting.md)
- Visit [FAQ](faq.md)
- Open an [issue on GitHub](https://github.com/Unicorn-Commander/Center-Deep/issues)

---

**Ready for more?** Check out:
- [Advanced Configuration](configuration.md)
- [Production Deployment](production.md)
- [API Documentation](api.md)