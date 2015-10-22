## Broker settings.
BROKER_URL = 'amqp://mava:orkarint@130.238.29.120:5672/app2'

# List of modules to import when celery starts.
CELERY_IMPORTS = ('app2.proj')

## Using the database to store task state and results.
CELERY_RESULT_BACKEND = 'amqp://'

CELERY_ACKS_LATE = True