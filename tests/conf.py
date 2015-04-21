import os
import os.path
from configparser import ConfigParser

from kii import KiiAPI, KiiAdminAPI, Site
from kii import exceptions as exc


def get_env():
    config = ConfigParser()
    filepath = os.path.join(os.path.dirname(__file__), 'test.ini')
    config.read(filepath)
    return dict(((k, dict(v)) for k, v in config.items()))


def get_api():
    env = get_env()
    api = KiiAPI(env['kii_info']['app_id'],
                 env['kii_info']['app_key'],
                 region=Site[env['location']['region']])
    return api


def get_api_with_test_user():
    env = get_env()
    api = KiiAPI(env['kii_info']['app_id'],
                 env['kii_info']['app_key'],
                 region=Site[env['location']['region']])
    test_user = get_test_user()
    return api.clone(access_token=test_user.access_token)


def get_admin_api():
    env = get_env()
    api = KiiAdminAPI(
        env['kii_info']['app_id'],
        env['kii_info']['app_key'],
        env['kii_info']['client_id'],
        env['kii_info']['client_secret'],
        region=Site[env['location']['region']])
    return api


def clean_up_of_user():
    api = get_api()
    env = get_env()
    test_user = env['test_user']

    # check exists user
    try:
        token = api.user.login(test_user['login_name'],
                               test_user['password'])
        # delete user, if already exists
        api.with_access_token(token).user.delete_a_user()
    except exc.KiiInvalidGrantError:
        pass


def get_test_user():
    clean_up_of_user()

    api = get_api()
    env = get_env()
    test_user = env['test_user']

    user = api.user.create_a_user_and_obtain_access_token(login_name=test_user['login_name'],
                                                          password=test_user['password'],
                                                          email_address=test_user['email'],
                                                          phone_number=test_user['phone'])
    return user


def cleanup():
    clean_up_of_user()
