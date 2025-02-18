```markdown
# MovieTrend Integration for Telex

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![Django](https://img.shields.io/badge/django-3.2%2B-green)

A Django-based integration that fetches weekly trending movies from TMDb and displays them in a Telex channel.

## Overview

MovieTrend fetches trending movies from TMDb, formats the data with titles, ratings, overviews, and poster images, and sends it to Telex for display in a designated channel. Perfect for keeping communities updated on popular films.

## Features

- **Weekly Updates**: Automatically fetches trending movies weekly.
- **Rich Media Support**: Includes movie titles, ratings, overviews, and poster images.
- **Telex Integration**: Seamlessly sends formatted data to Telex channels.
- **Customizable**: Configure the number of movies to display via integration settings.

## Requirements

- Python 3.8+
- `requests` library
- Django 3.2+
- [TMDb API Key](https://www.themoviedb.org/settings/api) (free account required)

## Project Structure

```plaintext
movie_trend/
    ├── movieTrendApp/
        ├── tests/                # Test cases for the integration
        ├── static/
            ├── logo/
                ├── logo.png      # Telex integration logo
        ├── integrations.json    # Telex integration configuration
    ├── manage.py                 # Django management script
    ├── requirements.txt          # Project dependencies
```

## Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/telex_integrations/movie_trend.git
   cd movie_trend
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up TMDb API Key**:
   - Add your API key to `settings.py`:
     ```python
     TMDB_API_KEY = 'your_api_key_here'  # Replace with your key
     ```
   - *For production, use environment variables instead of hardcoding.*

4. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

## Usage

### Integration with Telex
1. Provide Telex with the integration JSON URL:
   ```
   http://<your-server-domain>/integration.json
   ```
   Replace `<your-server-domain>` with your server's domain/IP and port (e.g., `localhost:8000`).

2. Telex will periodically fetch trending movies via the `/tick/` endpoint:
   ```
   http://<your-server-domain>/tick/
   ```

### Configuration
- Adjust the number of movies fetched in the Telex integration settings.
- Modify polling frequency via Telex's admin dashboard.

## Testing

Run the test suite with:
```bash
python manage.py test
```

## Deployment

1. **Production Server Setup**:
   - Use **Gunicorn** as the application server and **Nginx** as the reverse proxy.
   - Example Gunicorn command:
     ```bash
     gunicorn --workers 3 your_project_name.wsgi:application
     ```

2. **Environment Variables**:
   - Set `TMDB_API_KEY` in your production environment for security.

3. **Ensure Accessibility**:
   - Verify the `/tick/` endpoint is publicly accessible to Telex servers.

## Screenshots

*(Include screenshots of the integration in a Telex channel here)*
> Example:
>

---

## Contributing
Pull requests are welcome! For major changes, open an issue first to discuss proposed changes.

## License
[MIT](https://choosealicense.com/licenses/mit/) (Add a `LICENSE` file to specify)
```

---

