# Center Deep - Advanced Metasearch Engine

Center Deep is a powerful metasearch engine that aggregates results from multiple search engines, providing users with comprehensive and privacy-focused search capabilities.

## Features

- **Multi-Engine Search**: Aggregates results from Google, Bing, DuckDuckGo, Qwant, and more
- **Category Filtering**: Specialized search for Images, Videos, News, Maps, and Music
- **Privacy-Focused**: Optional local data tracking with client-side storage
- **Admin Dashboard**: Comprehensive admin panel for managing:
  - BrightData rotating proxy configuration
  - Prometheus and Grafana monitoring integration
  - User management and authentication
  - Real-time search statistics
- **Modern UI**: Dark theme with responsive design
- **Advanced Filtering**: Time range, language, and safe search options

## Installation

1. Clone the repository:
```bash
git clone https://github.com/MagicUnicornInc/Center-Deep.git
cd Center-Deep
```

2. Install dependencies:
```bash
pip install flask flask-sqlalchemy flask-login redis requests
```

3. Ensure SearXNG is running on port 8888 (or configure the port in admin settings)

4. Run the application:
```bash
python app.py
```

5. Access the application at `http://localhost:8890`

## Default Credentials

- Username: `ucadmin`
- Password: `MagicUnicorn!8-)`

**Important**: Change the default password after first login for security.

## Configuration

### Admin Dashboard

Access the admin dashboard at `/admin` after logging in to configure:

- **Proxy Settings**: Configure BrightData rotating proxies
- **Monitoring**: Set up Prometheus and Grafana endpoints
- **SearXNG**: Configure the SearXNG instance URL and parameters
- **User Management**: Add/remove users and manage access

### Search Preferences

Users can customize their search experience through the preferences page:

- Safe search settings
- Results per page
- Enabled search engines
- Theme and language preferences
- Local data tracking options

## Architecture

- **Backend**: Flask with SQLAlchemy for database management
- **Search Engine**: SearXNG metasearch engine integration
- **Database**: SQLite for user data and search logs
- **Caching**: Optional Redis integration for statistics
- **Authentication**: Flask-Login for user session management

## Development

The project structure:
```
Center-Deep/
├── app.py              # Main Flask application
├── templates/          # HTML templates
├── static/            
│   ├── css/           # Stylesheets
│   └── images/        # Logo and image assets
└── instance/          # Database files (created on first run)
```

## Security

- All user passwords are hashed using Werkzeug's security utilities
- Session management with secure cookies
- Optional proxy support for anonymized searching
- No tracking by default - users opt-in for local data storage

## Credits

Developed by Magic Unicorn Unconventional Technology & Stuff Inc.

## License

This project is proprietary software. All rights reserved.