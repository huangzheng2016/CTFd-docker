from CTFd.utils import set_config

from .db_utils import DBUtils

def setup_default_configs():
    config=[
        ['awd_setup', 'yes'],
        ['containers_key', 'ROOT_PASSWD'],
        ['docker_api_url', 'unix:///var/run/docker.sock'],
        ['per_round', '300'],
        ['port_minimum', '10201'],
        ['port_maximum', '10300'],
        ['random_port', '1'],
        ['direct_address', 'direct.test.com'],
    ]
    DBUtils.save_all_configs(config)