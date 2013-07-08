BROKER_URL = "amqp://guest:guest@openmalaria-qa.crc.nd.edu:5672"
CELERY_RESULT_BACKEND = 'amqp'
CELERY_IMPORTS = ("tasks",)
CELERY_DEFAULT_QUEUE = 'openmalaria'