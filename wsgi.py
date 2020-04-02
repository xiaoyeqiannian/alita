# coding: utf-8

import os
import inc

config_file = os.environ.get("ALITA_CONFIG", "config/prod/prod.py")
application = inc.create_app(config_file)

