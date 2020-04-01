#coding: utf-8

import logging
import util.commands
from flask_script import Manager
#from flask_assets import ManageAssets
from flask_script.commands import Clean, ShowUrls

import inc

logger = logging.getLogger(__name__)

def main():
    #  创建应用程序
    manager = Manager(inc.create_app)
    # 添加配置文件默认dev/dev.py
    manager.add_option('-c', '--config', dest='config', required=False, default='config/dev/dev.py')
    # 显示项目的所有URL匹配路由。
    manager.add_command("urls", ShowUrls())
    # 清除文件 .pyc .pyo
    manager.add_command("clean", Clean())
    # 资源管理
    #manager.add_command("assets", ManageAssets())
    # 控制台程序调用 执行特定的程序 可设定执行几次==
    manager.add_command("interval", util.commands.IntervalRun())
    # doc test
    manager.add_command("test", util.commands.RunDocTest())
    # 执行一次的命令
    manager.add_command("run", util.commands.RunModule())

    try:
        manager.run()
    except KeyboardInterrupt:
        logger.info('KeyboardInterrupt cause quit')

if __name__ == "__main__":
    main()
