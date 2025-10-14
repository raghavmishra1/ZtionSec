# ZtionSec - Comprehensive Security Analysis Tool

ZtionSec is a powerful web-based security analysis tool built with Django that provides comprehensive security testing for websites and email breach checking capabilities.

## Features

### 🔒 Website Security Analysis
- **SSL Certificate Validation**: Check SSL validity, issuer, expiry dates, and security grades
- **HTTP Security Headers**: Analyze HSTS, CSP, X-Frame-Options, X-XSS-Protection, and X-Content-Type-Options
- **CMS Detection**: Identify content management systems and their versions
- **Performance Monitoring**: Track response times and HTTP status codes
- **Security Scoring**: Get an overall security score (0-100) with letter grades (A+ to F)

### 📧 Data Breach Checking
- **Email Breach Detection**: Check if email addresses have been compromised in known data breaches
- **HaveIBeenPwned Integration**: Uses the HaveIBeenPwned API for comprehensive breach data
- **Breach History**: Track all email checks with detailed breach information

### 📊 Reporting & Analytics
- **PDF Report Generation**: Create comprehensive security reports in PDF format
- **Scan History**: View all previous security scans with filtering and search
- **Security Dashboard**: Visual representation of security metrics and trends
- **Breach Analytics**: Track email breach checks and risk levels

### 🎨 Modern UI/UX
- **Bootstrap 5**: Responsive, modern interface
- **Font Awesome Icons**: Professional iconography
- **Mobile-Friendly**: Works seamlessly on all devices
- **Real-time Results**: Instant security analysis feedback

## Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Setup Instructions

1. **Clone or navigate to the project directory**
   ```bash
   cd /home/offensive/Desktop/Ztionsec
   ```

2. **Install required packages**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run database migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Create a superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

5. **Start the development server**
   ```bash
   python manage.py runserver
   ```

6. **Access the application**
   - Open your browser and go to `http://127.0.0.1:8000`
   - Admin panel: `http://127.0.0.1:8000/admin`

## Usage

### Website Security Scanning

1. **Enter Website URL**: Input the full URL of the website you want to analyze
2. **Start Scan**: Click "Start Security Scan" to begin the analysis
3. **View Results**: Get detailed security analysis including:
   - SSL certificate status and grade
   - Security headers analysis
   - CMS detection results
   - Performance metrics
   - Overall security score and grade
4. **Download Report**: Generate and download a comprehensive PDF report

### Email Breach Checking

1. **Enter Email Address**: Input the email address you want to check
2. **Check for Breaches**: Click "Check for Breaches" to search breach databases
3. **View Results**: See if the email has been compromised and in which breaches
4. **Follow Recommendations**: Get security recommendations based on results

## API Endpoints

### Website Scanning API
```bash
POST /api/scan/
Content-Type: application/json

{
    "url": "https://example.com"
}
```

**Response:**
```json
{
    "ssl_valid": true,
    "ssl_grade": "A",
    "ssl_issuer": "Let's Encrypt",
    "has_hsts": true,
    "has_csp": false,
    "security_score": 85,
    "grade": "A",
    "response_time": 245.67,
    "status_code": 200
}
```

## Security Features Analyzed

### SSL/TLS Analysis
- Certificate validity and chain verification
- Issuer information and trust validation
- Expiry date monitoring and alerts
- Security grade assessment (A+ to F)

### HTTP Security Headers
- **HSTS**: HTTP Strict Transport Security
- **CSP**: Content Security Policy
- **X-Frame-Options**: Clickjacking protection
- **X-XSS-Protection**: Cross-site scripting protection
- **X-Content-Type-Options**: MIME type sniffing protection

### Performance Metrics
- Response time measurement
- HTTP status code analysis
- Server information detection
- Load time optimization suggestions

### CMS Detection
- WordPress detection and version identification
- Drupal, Joomla, Magento detection
- Technology stack identification
- Version-specific vulnerability alerts

## Configuration

### HaveIBeenPwned API Setup
To enable breach checking functionality:

1. Get an API key from [HaveIBeenPwned](https://haveibeenpwned.com/API/Key)
2. Update the API key in `scanner/utils.py`:
   ```python
   headers = {
       'hibp-api-key': 'YOUR_ACTUAL_API_KEY_HERE'
   }
   ```

### Security Settings
Update Django settings for production:
- Set `DEBUG = False`
- Configure `ALLOWED_HOSTS`
- Use environment variables for sensitive data
- Enable HTTPS and security middleware

## File Structure

```
Ztionsec/
├── Ztionsec/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── scanner/
│   ├── migrations/
│   ├── templates/scanner/
│   ├── __init__.py
│   ├── admin.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── utils.py
│   └── pdf_generator.py
├── templates/
├── static/
├── manage.py
├── requirements.txt
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Security Considerations

- Always use HTTPS in production
- Keep dependencies updated
- Validate all user inputs
- Implement rate limiting for API endpoints
- Use environment variables for sensitive configuration
- Regular security audits and updates

## License

This project is built for educational and professional security assessment purposes. Use responsibly and in accordance with applicable laws and regulations.

## Support

For issues, questions, or contributions:
- Create an issue in the repository
- Follow security best practices
- Test thoroughly before deployment

## Changelog

### Version 1.0.0
- Initial release with full security scanning capabilities
- Website SSL and header analysis
- Email breach checking integration
- PDF report generation
- Modern Bootstrap UI
- Admin panel integration
- API endpoints for automation

---

**Built with ❤️ for security professionals and developers**
