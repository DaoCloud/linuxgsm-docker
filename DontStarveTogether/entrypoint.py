#!/usr/bin/env python
import os
import pwd
import grp
import logging
import getpass
import subprocess
import ConfigParser

GAME = 'DoNotStarveTogether'
USER = 'dstserver'
GROUP = 'dstserver'
VOLUME_PATH = '/save'
HOME = os.path.expanduser('~%s' % USER)
KLEI_DIRECTORY = os.path.join(HOME, '.klei')
SETTING_DIRECTORY = os.path.join(KLEI_DIRECTORY, GAME)

SETTING_FILE = os.path.join(SETTING_DIRECTORY, 'settings.ini')
CLUSTER_TOKEN_FILE = os.path.join(SETTING_DIRECTORY, 'Cluster_1', 'cluster_token.txt')
MANAGER_FILE = os.path.join(HOME, 'dstserver')
BIN_DIRECTORY = os.path.join(HOME, 'serverfiles', 'bin')
BIN_FILE = os.path.join(
    BIN_DIRECTORY, 'dontstarve_dedicated_server_nullrenderer'
)


class NotRoot(Exception):
    pass


class DontStarveTogetherConfig(object):

    CONFIGS = {
        'network': [
            'default_server_name',
            'default_server_description',
            # 'server_port',
            # 'server_password',
            'max_players',
            'pvp',
            'game_mode',
            'server_intention',
            'enable_autosaver',
            'enable_snapshots',
            'tick_rate',
            'connection_timeout',
            'server_save_slot',
            'enable_vote_kick',
            'pause_when_empty'
        ],
        'account': [
            # 'server_token'
            # 'dedicated_lan_server'
        ],
        'STEAM': [
            'DISABLECLOUD'
        ],
        'MISC': [
            'CONSOLE_ENABLED',
            'autocompiler_enabled'
        ]
    }

    def __init__(self, setting_file=None, cluster_token_file=None):
        super(DontStarveTogetherConfig, self).__init__()
        self.setting_file = setting_file
        self.cluster_token_file = cluster_token_file
        self.config = ConfigParser.ConfigParser()

        with open(self.setting_file, 'rb') as config_file:
            self.config.readfp(config_file)

    def get_password(self):
        return os.environ.get('SERVER_PASSWORD')

    def get_cluster_token(self):
        return os.environ.get('CLUSTER_TOKEN')

    def do_config(self):
        for section, options in self.CONFIGS.iteritems():
            for o in options:
                name = o.upper()
                if name in os.environ:
                    self.config.set(section, o, os.environ[name])

        password = self.get_password()
        if password:
            logging.info('Your world\'s password is %s.' % password)
            self.config.set('network', 'server_password', password)
        else:
            logging.error(
                'No password setted, everyone can access your world.'
            )
            self.config.remove_option('network', 'server_password')

        cluster_token = self.get_cluster_token()
        if cluster_token:
            with open(self.cluster_token_file, 'wb') as token_file:
                token_file.write(cluster_token)
            self.config.set('account', 'dedicated_lan_server', 'false')
        else:
            self.config.set('account', 'dedicated_lan_server', 'true')

        with open(self.setting_file, 'wb') as config_file:
            self.config.write(config_file)


def _switch_to_user(user, group):
    uid, gid = pwd.getpwnam(user).pw_uid, grp.getgrnam(group).gr_gid
    os.setgid(gid)
    os.setuid(uid)
    os.environ['HOME'] = os.path.expanduser('~%s' % user)
    return uid, gid


def prepare_volume():
    if os.path.exists(VOLUME_PATH):
        subprocess.call(['ln', '-s', VOLUME_PATH, '-T', KLEI_DIRECTORY])
        subprocess.call(['chown', '-hR', '%s:%s' % (USER, GROUP), VOLUME_PATH])
    else:
        logging.warning('No Volume found, maybe you will lose your all data.')


def prepare_game():
    subprocess.call([MANAGER_FILE, 'auto-install'])


def game_start():
    config = DontStarveTogetherConfig(setting_file=SETTING_FILE,
                                      cluster_token_file=CLUSTER_TOKEN_FILE)
    config.do_config()

    subprocess.call([BIN_FILE], cwd=BIN_DIRECTORY)


def main():
    if getpass.getuser() != 'root':
        raise NotRoot('This script should be run as root.')

    prepare_volume()

    pid = os.fork()
    if pid == 0:
        # child process
        _switch_to_user(USER, GROUP)

        prepare_game()
        game_start()
    else:
        os.waitpid(pid, 0)


if __name__ == '__main__':
    main()
