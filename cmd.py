from flask_script import Manager
from flask_script.commands import Clean, ShowUrls
import inc
from util.commands import InitApp


def main():
    # create application
    manager = Manager(inc.create_app)
    # add config, default by dev/dev.py
    manager.add_option('-c', '--config', dest='config', required=False, default='../config/alita/prod.py')
    # show the application's url routes
    manager.add_command("urls", ShowUrls())
    # clean .pyc .pyo
    manager.add_command("clean", Clean())
    manager.add_command("init", InitApp())

    try:
        manager.run()
    except KeyboardInterrupt:
        print('KeyboardInterrupt cause quit')


if __name__ == "__main__":
    main()
