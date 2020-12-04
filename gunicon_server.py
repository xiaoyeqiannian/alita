import os
import inc

config_file = os.environ.get("ALITA_CONFIG", "../config/config.py")
application = inc.create_app(config_file)

