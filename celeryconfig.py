## Broker settings.
BROKER_URL = 'amqp://guest:guest@localhost:5672//'

# List of modules to import when celery starts.
CELERY_IMPORTS = ('myapp.tasks', )

## Using the database to store task state and results.
CELERY_RESULT_BACKEND = 'amqp://'

CELERY_ACKS_LATE = True