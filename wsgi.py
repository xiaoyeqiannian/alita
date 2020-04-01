# coding: utf-8

import os
import inc
# 后台启动
config_file = os.environ.get("ALITA_CONFIG", "config/prod/prod.py")
application = inc.create_app(config_file)

