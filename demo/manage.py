#!/usr/bin/env python
"""
This is a modified version of manage.py which serves 3 primary goals:

    1. Implement a --debug flag to allow Django to be run in debug mode
       without modifying the settings file

    2. Enable development-mode secrets management that is consistent with
       Ansible Vault based secrets for deployment. Vault secrets are kept
       in encrypted files in an external directory located at SECRETS_DIR
       or ~/.secrets. Secrets are rarely needed in development, but if they
       are, they can be placed into a vault.dev.yml file in the secrets
       directory for this project.

    3. Simultaneously enable environment variable based configurations for
       deployment environment differentiation while also enabling manage.py
       execution with those same configurations. This is implemented by
       loading the environment variables from the Upstart config file that is
       used to execute the web application. This approach allows us to keep a
       single definitive source for environment settings in deployment, being
       the Upstart config file located in /etc/init/apps.
"""
import os
import re
import sys
import yaml

PROJECT_NAME = 'django-multimail'
WARNING = '\033[93m'
ENDC = '\033[0m'
ENV_REGEX = re.compile(r"^\s*env\s+(.*?)='(.*)'\s*$")


def get_dev_secrets():
    secrets_dir = os.environ.get('SECRETS_DIR', '~/.secrets')
    secrets_file = os.path.join(secrets_dir, PROJECT_NAME, 'vault.dev.yml')
    try:
        with open(secrets_file) as f:
            cfg = yaml.safe_load(f)
        return { k.upper()[len('vault_'):]:v for k,v in cfg.items() }
    except IOError:
        return {}


def get_init_env():
    r = {}
    try:
        with open('/etc/init/apps/%s.conf' % PROJECT_NAME) as f:
            for line in f:
                m = ENV_REGEX.match(line)
                if m:
                    r[m.group(1)] = m.group(2)
        return r
    except IOError:
        return {}


def get_env_vars():
    r = get_dev_secrets()
    if not r:
        r = get_init_env()
    if not r:
        print(WARNING  \
            + 'No local secrets or init env found. ' \
            + 'Extra environment not loaded.' \
            + ENDC)
    return r


if __name__ == "__main__":
    if '--debug' in sys.argv:
        os.environ.setdefault('DJANGO_DEBUG', 'True')
        sys.argv.remove('--debug')
    for k,v in get_env_vars().items():
        os.environ.setdefault(k, v)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.dev')
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
