# Chef's Court of Justice Backend

A Django REST API backend for Chef's Court of Justice, a mock legal system where users can participate in simulated court cases with role-based access control.

## Features

- **JWT Authentication**: Secure token-based authentication
- **Role-Based Access Control**: Different permissions for defendants, plaintiffs, jurors, and judges
- **Case Management**: Create and view legal cases
- **Argument Submission**: Defendants and plaintiffs can submit arguments and evidence
- **Judge Powers**: Judges can approve, edit, and delete arguments
- **Jury Voting**: Jurors can vote on case verdicts with unique voting per case
- **RESTful API**: Complete REST API with proper HTTP status codes

### Setup

. **Create virtual environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

. **Install dependencies**
   ```bash
   pip install django djangorestframework djangorestframework-simplejwt
   ```

. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

. **Start development server**
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://127.0.0.1:8000/`


## User Roles

- **Defendant**: Can submit arguments for their cases
- **Plaintiff**: Can submit arguments for their cases
- **Juror**: Can vote on case verdicts (one vote per case)
- **Judge**: Can approve, edit, and delete arguments

## Database Models

### User
- Extends Django's AbstractUser
- Additional field: `role` (defendant, plaintiff, juror, judge)

### Case
- `title`: Case title
- `description`: Case description
- `defendant`: Foreign key to User
- `plaintiff`: Foreign key to User
- `created_at`: Timestamp
- `is_active`: Boolean

### Vote
- `case`: Foreign key to Case
- `juror`: Foreign key to User
- `verdict`: Choice (guilty, not_guilty)
- `voted_at`: Timestamp
- Unique constraint: One vote per juror per case


```

## Development

### Running Tests
```bash
python manage.py test
```

### Code Formatting
```bash
pip install black
black .
```

### Linting
```bash
pip install flake8
flake8 .
```

## Deployment

### Production Settings
- Change `DEBUG = False` in settings.py
- Use PostgreSQL database
- Set proper `SECRET_KEY`
- Configure allowed hosts
- Use production WSGI server (gunicorn)

### Environment Variables
```bash
export SECRET_KEY='your-secret-key'
export DEBUG=False
export DATABASE_URL='postgresql://user:password@localhost/dbname'
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

