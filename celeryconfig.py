## Broker settings.
import os
floating_ip = os.environ['FLOATING_IP']
broker_user = os.environ['BROKER_USER']
broker_pass = os.environ['BROKER_PASS']

BROKER_URL = 'amqp://'+ broker_user +':'+broker_pass+'@'+floating_ip+':5672/app2'

# List of modules to import when celery starts.
CELERY_IMPORTS = ('proj', )

## Using the database to store task state and results.
CELERY_RESULT_BACKEND = 'amqp://'

#CELERY_ACKS_LATE = True