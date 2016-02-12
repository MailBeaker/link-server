from logging import config
from flask import Flask

from sdk import beaker

import settings

# Setup logging
config.dictConfig(settings.LOGGING)


# Creating the Flask app object
app = Flask(__name__)
app.debug = settings.DEBUG

beaker_client = beaker.Client()

import views
