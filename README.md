# Center Deep - Professional SearXNG Fork

Center Deep is a professional, enterprise-ready fork of SearXNG metasearch engine, designed for businesses and licensed individual installations. This enhanced version includes advanced administration features, rotating proxy support, and comprehensive monitoring capabilities for professional deployments.

![Center Deep Main Page](screenshots/main-page.png)

## Professional Features

This is the licensed professional version of our SearXNG fork, available for UC-1-Pro enterprise deployments and licensed individual installations.

### Core Enhancements
- **Enterprise Admin Dashboard**: Complete control panel for system administrators
- **Rotating Proxy Support**: Built-in BrightData proxy integration for enhanced anonymity
- **Advanced Monitoring**: Prometheus and Grafana integration for real-time metrics
- **User Management**: Multi-user support with role-based access control
- **Professional UI**: Modern dark theme optimized for extended use
- **Real-time Analytics**: Live search statistics and usage monitoring

### Search Capabilities
- **Multi-Engine Aggregation**: Simultaneous search across Google, Bing, DuckDuckGo, Qwant, and more
- **Category-Specific Results**: Optimized layouts for Images, Videos, News, Maps, and Music
- **Advanced Filtering**: Time range, language, and safe search controls
- **Privacy Options**: Optional client-side data storage for enhanced privacy

## Screenshots

### Search Results
![Search Results](screenshots/search-results.png)

### Image Search
![Image Search](screenshots/images-page.png)

### Video Results
![Video Results](screenshots/video-results.png)

### Settings Page
![Settings](screenshots/settings.png)

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

## Licensing

Center Deep is a commercial fork of SearXNG, developed by Magic Unicorn Unconventional Technology & Stuff Inc.

- **Professional License**: Required for UC-1-Pro deployments and enterprise use
- **Individual License**: Available for personal professional installations
- **Base SearXNG**: Original SearXNG components maintain their open-source licensing

For licensing inquiries, contact Magic Unicorn Unconventional Technology & Stuff Inc.

## Credits

Developed and maintained by Magic Unicorn Unconventional Technology & Stuff Inc.

Based on the open-source SearXNG project with significant enhancements for professional use.