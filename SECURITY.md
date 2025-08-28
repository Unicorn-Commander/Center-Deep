# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take security seriously at Center Deep. If you discover a security vulnerability, please follow these steps:

1. **DO NOT** create a public GitHub issue
2. Email security details to: security@magicunicorn.tech
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### What to expect:

- **Acknowledgment**: Within 48 hours
- **Initial Assessment**: Within 1 week
- **Fix Timeline**: Critical issues within 30 days
- **Credit**: Security researchers will be credited (unless anonymity requested)

## Security Features

### Privacy Protection
- **No tracking**: Zero user tracking or analytics
- **No logs**: Search queries are not logged by default
- **No cookies**: Session management without persistent tracking
- **IP anonymization**: User IPs are not stored

### Authentication & Authorization
- **Secure passwords**: Bcrypt hashing with salt
- **Session management**: Secure session tokens
- **Admin isolation**: Separate admin interface with authentication

### Network Security
- **HTTPS support**: Full TLS/SSL support for encrypted connections
- **Docker isolation**: Services run in isolated containers
- **Rate limiting**: Protection against abuse

### Data Security
- **Local storage**: All data stored locally, no cloud dependencies
- **Encrypted secrets**: Sensitive configuration encrypted at rest
- **Minimal permissions**: Services run with minimal required permissions

## Security Best Practices

### During Installation
1. **Change default credentials immediately** during setup
2. Use strong, unique passwords
3. Enable HTTPS in production
4. Keep your system and Docker updated

### During Operation
1. Regularly update Center Deep and dependencies
2. Monitor system logs for suspicious activity
3. Backup your configuration and data
4. Use firewall rules to restrict access

### Configuration Security
- Store `.env` files outside version control
- Use environment variables for sensitive data
- Rotate API keys and secrets regularly
- Limit network exposure of services

## Dependencies

Center Deep relies on:
- **SearXNG**: Base search engine (AGPL-3.0)
- **Flask**: Web framework
- **Redis**: Caching layer
- **Docker**: Container runtime

We regularly audit and update dependencies for security patches.

## Compliance

Center Deep is designed with privacy regulations in mind:
- **GDPR compliant**: No personal data collection
- **CCPA compliant**: No user tracking
- **Privacy by design**: Security and privacy built-in from the start

## Contact

For security concerns, contact:
- Email: security@magicunicorn.tech
- GitHub: Create a private security advisory

---

*Last updated: January 2025*