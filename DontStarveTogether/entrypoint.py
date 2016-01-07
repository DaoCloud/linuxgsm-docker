#!/usr/bin/env python
import os
import pwd
import grp
import getpass
import functools
import subprocess
import contextlib
import ConfigParser

GAME = 'DoNotStarveTogether'
USER = 'dstserver'
GROUP = 'dstserver'
VOLUME_PATH = '/save'
HOME = os.path.expanduser('~%s' % USER)
KLEI_DIRECTORY = os.path.join(HOME, '.klei')
SETTING_DIRECTORY = os.path.join(KLEI_DIRECTORY, GAME)

SETTING_FILE = os.path.join(SETTING_DIRECTORY, 'settings.ini')
TOKEN_FILE = os.path.join(SETTING_DIRECTORY, 'server_token.txt')
MANAGER_FILE = os.path.join(HOME, 'dstserver')
BIN_DIRECTORY = os.path.join(HOME, 'serverfiles', 'bin')
BIN_FILE = os.path.join(
    BIN_DIRECTORY, 'dontstarve_dedicated_server_nullrenderer'
)

SERVER_TOKEN = os.environ.get('SERVER_TOKEN')
SERVER_NAME = os.environ.get('SERVER_NAME', 'Do Not Starve Together')
SERVER_DESCRIPTION = os.environ.get(
    'SERVER_DESCRIPTION', 'Welcome to %s' % SERVER_NAME
)
SERVER_PASSWORD = os.environ.get(
    'SERVER_PASSWORD', os.urandom(4).encode('hex')
)


class NotRoot(Exception):
    pass


def _switch_to_user(user, group):
    uid, gid = pwd.getpwnam(user).pw_uid, grp.getgrnam(group).gr_gid
    os.setgid(gid)
    os.setuid(uid)
    return uid, gid


@contextlib.contextmanager
def process_as_user(user, group):
    pid = os.fork()
    if pid == 0:
        uid, gid = _switch_to_user(user, group)
        os.environ['HOME'] = HOME
        yield pid, uid, gid
    else:
        os.waitpid(pid, 0)


def prepare_volume():
    if os.path.exists(VOLUME_PATH):
        subprocess.call(['ln', '-s', VOLUME_PATH, KLEI_DIRECTORY])
        subprocess.call(['chown', '-hR', '%s:%s' % (USER, GROUP), VOLUME_PATH])
    else:
        print 'No Volume found.'


def prepare_game():
    subprocess.call([MANAGER_FILE, 'auto-install'])


def game_start():
    config = ConfigParser.ConfigParser()

    with open(SETTING_FILE, 'rb') as config_file:
        config.readfp(config_file)

    if SERVER_TOKEN:
        config.set('account', 'dedicated_lan_server', 'false')
        with open(TOKEN_FILE, 'wb') as token_file:
            token_file.write(SERVER_TOKEN)
    else:
        config.set('account', 'dedicated_lan_server', 'true')

    config.set('network', 'default_server_name', SERVER_NAME)
    config.set('network', 'default_server_description', SERVER_DESCRIPTION)
    config.set('network', 'server_password', SERVER_PASSWORD)

    with open(SETTING_FILE, 'wb') as config_file:
        config.write(config_file)

    print 'Your world\'s password is %s' % SERVER_PASSWORD
    subprocess.call([BIN_FILE], cwd=BIN_DIRECTORY)


def main():
    if getpass.getuser() != 'root':
        raise NotRoot('This script should be run as root.')

    prepare_volume()

    with process_as_user(USER, GROUP):
        prepare_game()
        game_start()

if __name__ == '__main__':
    main()
