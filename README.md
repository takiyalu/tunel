# Project Name

## Overview

This project is designed ap personal project designed to manage and monitor financial assets using Django, Celery, and RabbitMQ.
It provides functionalities for fetching and processing asset data, managing tasks, and monitoring through Flower.
Also, it has been mostly designed to be run locally, in case of production environments a few adjustments would be required.

## Features

- Monitor financial assets and update their prices.
- Send alert emails when asset prices cross specified thresholds.
- Use Celery for task management and periodic updates.
- Monitor Celery tasks using Flower.
- This project uses MySQL as it's main database.

## Installation

### Prerequisites

- **Python**: Ensure you have Python 3.10 installed.
- **Virtual Environment**: Use a virtual environment to manage dependencies.

### Setup

1. **Clone the Repository**

   ```bash
   git clone https://github.com/takiyalu/tunel
   cd tunnel
   ```

2. **Create and Activate a Virtual Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### RabbitMQ and Erlang

1. **Download and Install Erlang**

   - **Website**: [Erlang](https://www.erlang.org/downloads)

2. **Download and Install RabbitMQ**

   - **Website**: [RabbitMQ](https://www.rabbitmq.com/download.html)

   Follow the installation guides on these websites. Ensure RabbitMQ is running.
   Make sure that the RabbitMQ and Erlang have matching versions: https://www.rabbitmq.com/docs/which-erlang

### Celery Setup

1. **Install Celery**

   Add Celery to your `requirements.txt` or install it directly:

   ```bash
   pip install celery
   ```

2. **Configure Celery**

   Add the following to your Django settings (e.g., `settings.py`):

   ```python
   CELERY_BROKER_URL = 'pyamqp://guest@localhost//'
   CELERY_RESULT_BACKEND = 'rpc://'
   ```

   Create a `celery.py` file in your project root:

   ```python
   from __future__ import absolute_import, unicode_literals
   import os
   from celery import Celery

   os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tunnel.settings')
   app = Celery('tunnel')
   app.config_from_object('django.conf:settings', namespace='CELERY')
   app.autodiscover_tasks()
   ```

   Ensure that you update `__init__.py` in your project directory:

   ```python
   from __future__ import absolute_import, unicode_literals
   # This will make sure the app is always imported when Django starts so that shared_task will use this app.
   from .celery import app as celery_app

   __all__ = ('celery_app',)
   ```

3. **Start Celery Worker**

   ```bash
   celery celery -A myapp.celeryapp worker --loglevel=info -P eventlet
   ```

### Celery Beat Setup

1. **Install Celery Beat**

   Celery Beat is included in the Celery package. No separate installation is needed.

2. **Configure Celery Beat**

   Add to your Django settings:

   ```python
   CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
   ```

   Ensure you have `django_celery_beat` installed:

   ```bash
   pip install django-celery-beat
   ```

3. **Start Celery Beat**

   ```bash
   celery -A tunnel beat --loglevel=info
   ```

### Flower (Optional)

1. **Install Flower**

   ```bash
   pip install flower
   ```

2. **Start Flower**

   ```bash
   celery -A tunnel flower
   ```

   Visit [http://localhost:5555](http://localhost:5555) to monitor your Celery tasks.

## Running the Application

1. **Migrate Database**

   ```bash
   python manage.py migrate
   ```

2. **Run the Development Server**

   ```bash
   python manage.py runserver
   ```

## Usage

- Access the web interface to monitor and manage financial assets.
- Configure the task schedules and alerts via the Django admin interface.

## Troubleshooting

- If you encounter issues with Celery workers not starting, ensure RabbitMQ is running and accessible.
- Check Celery logs for detailed error messages.

## Contributing

- Please follow the code of conduct and contribution guidelines provided in the repository.

## License

- This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
