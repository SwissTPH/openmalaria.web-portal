openmalaria_data_dir = "/omdata"
om_exe = "/omdata/build/openMalaria"

DATABASES = {
    'default': {
        'NAME': 'OpenMalaria',
        'USER': 'openmalaria',
        'PASSWORD': 'openmalaria',
        'HOST': 'openmalaria-qa.crc.nd.edu',
        'PORT': '',
        }
}

BROKER_URL = "amqp://guest:guest@openmalaria-qa.crc.nd.edu:5672"