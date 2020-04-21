# -*- coding: utf-8 -*-

import glob
import json
import os
import platform
import sys
import urllib.request


def download_file(url, file_name):
    urllib.request.urlretrieve(url, file_name)


class AppInfo:
    def __init__(self, app_name: str, app_version: str, app_urls: list):
        self.app_name = app_name
        self.app_version = app_version
        self.app_urls = app_urls

    @staticmethod
    def __resolve_url(url=''):
        return url.replace('://', '_').replace('#/dl.7z', '_dl.7z').replace('%', '_').replace('/', '_')

    def get_app_file_names(self, one_of_urls):
        return self.app_name + '#' + self.app_version + '#' + self.__resolve_url(one_of_urls)

    def download_app(self):
        for app_url in self.app_urls:
            new_app_name = self.get_app_file_names(app_url)
            print('[cache_file_name]: ', new_app_name)
            new_app_path = os.path.join(Scoop.scoop_cache_path, new_app_name)
            if not os.path.exists(new_app_path):
                # replace mirror url
                if self.app_name in MirrorInfo.mirror_infos:
                    mirror_info = MirrorInfo.mirror_infos[self.app_name]
                    origin_host = mirror_info.origin_host.replace('{{app_name}}', self.app_name).replace(
                        '{{version}}', self.app_version)
                    mirror_host = mirror_info.mirror_host.replace('{{app_name}}', self.app_name).replace(
                        '{{version}}', self.app_version)
                    download_file(app_url.replace(origin_host, mirror_host), new_app_path)
                else:
                    download_file(app_url, new_app_path)
        print('download the app {} successfully.'.format(self.app_name))


class Scoop:
    os_bits = platform.architecture()[0]
    user_home = os.path.expanduser('~')

    scoop_home_path = None
    scoop_cache_path = None
    scoop_buckets_path = None
    scoop_app_jsons = None
    scoop_app_list = None

    @staticmethod
    def get_scoop_home_path():
        scoop_home = os.environ.get('SCOOP')
        if scoop_home is None:
            scoop_home = os.path.join(Scoop.user_home, 'scoop')
        return scoop_home

    @staticmethod
    def get_scoop_cache_path():
        return os.path.join(Scoop.scoop_home_path, 'cache')

    @staticmethod
    def get_scoop_buckets_path():
        return os.path.join(Scoop.scoop_home_path, 'buckets')

    @staticmethod
    def __get_scoop_app_jsons():
        scoop_buckets = Scoop.scoop_buckets_path
        buckets = os.listdir(scoop_buckets)

        all_jsons = list()
        for bucket in buckets:
            bucket_path = os.path.join(scoop_buckets, bucket)
            all_jsons.extend(glob.glob(os.path.join(bucket_path, '*.json')))
            inner_path = os.path.join(bucket_path, 'bucket')
            if os.path.exists(inner_path):
                all_jsons.extend(glob.glob(os.path.join(inner_path, '*.json')))
        return all_jsons

    @staticmethod
    def get_scoop_app_list():
        all_jsons = Scoop.scoop_app_jsons
        app_list = list()
        for json_file in all_jsons:
            app_name = os.path.splitext(os.path.basename(json_file))[0]
            try:
                with open(json_file, mode='r', encoding='utf-8') as file:
                    json_data = json.load(file)
                    app_version = json_data['version']

                    if 'url' in json_data:
                        url = json_data['url']
                    else:
                        if 'architecture' not in json_data or \
                                Scoop.os_bits not in json_data['architecture'] or \
                                'url' not in json_data['architecture'][Scoop.os_bits]:
                            print('the json {} can not find architecture url'.format(json_file))
                            continue
                        url = json_data['architecture'][Scoop.os_bits]['url']

                    if isinstance(url, str):
                        app_urls = [url]
                    elif isinstance(url, list):
                        app_urls = url
                    else:
                        print('the json {}, url do not match.'.format(json_file))
                        continue

                    app_list.append(AppInfo(app_name, app_version, app_urls))
            except Exception as e:
                print('exception happened. json file is {}.'.format(json_file))
                raise
        return app_list

    @staticmethod
    def find_scoop_app(app_name: str):
        for app in Scoop.scoop_app_list:
            if app.app_name == app_name:
                return app
        return None

    @staticmethod
    def init_scoop():
        Scoop.scoop_home_path = Scoop.get_scoop_home_path()
        Scoop.scoop_cache_path = Scoop.get_scoop_cache_path()
        Scoop.scoop_buckets_path = Scoop.get_scoop_buckets_path()
        Scoop.scoop_app_jsons = Scoop.__get_scoop_app_jsons()
        Scoop.scoop_app_list = Scoop.get_scoop_app_list()


class MirrorInfo:
    def __init__(self, app_name: str, origin_host: str, mirror_host: str):
        self.app_name = app_name
        self.origin_host = origin_host
        self.mirror_host = mirror_host

    mirror_infos = None

    @staticmethod
    def get_mirror_info():
        current_path = os.path.dirname(__file__)
        json_file = os.path.join(current_path, 'conf/mirror.json')
        try:
            with open(json_file, mode='r', encoding='utf-8') as file:
                info = dict()
                mirror_obj = json.load(file)
                for mirror_id in mirror_obj:
                    mirror = mirror_obj[mirror_id]
                    if 'origin_host' in mirror and 'mirror_host' in mirror and 'support_apps' in mirror:
                        support_apps = mirror['support_apps']
                        for app_name in support_apps:
                            mirror_info = MirrorInfo(app_name=app_name, origin_host=mirror['origin_host'],
                                                     mirror_host=mirror['mirror_host'])
                            info[app_name] = mirror_info
                return info
        except Exception as e:
            print('exception happened. json file is {}.'.format(json_file))
            raise

    @staticmethod
    def init_mirror_info():
        MirrorInfo.mirror_infos = MirrorInfo.get_mirror_info()


def main(app_names):
    for app_name in app_names:
        app: AppInfo = Scoop.find_scoop_app(app_name)
        if app is not None:
            app.download_app()
    print('download end.')


if __name__ == '__main__':
    MirrorInfo.init_mirror_info()
    Scoop.init_scoop()
    args = sys.argv
    args.pop(0)
    main(args)
