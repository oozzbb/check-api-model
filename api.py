# -*- coding: utf-8 -*-

# @version  : python-
# @license  : MIT
# @Software : PyCharm
# @Time     : 2024/8/21 14:44
# @Author   : yzl
# @File     : check.py

# @Features : # Enter feature name here
# Enter feature description here
import random
import time
import requests

class ClsCheckApi(object):

    def __init__(self, api_base: str = "", api_key: str = ""):
        super().__init__()

        if 'v1' not in api_base:
            self._api_base = self.joinURL(api_base, "/v1/")
        else:
            self._api_base = api_base

        self._api_key = api_key

        self.PATH_MODELS = r"/models"
        self.PATH_CHAT = r"/chat/completions"

        self._b_debug = False

        self._b_proxy = False

    def get_proxies(self):
        if self._b_debug:
            return {"http": "192.168.0.68:8888", "https": "192.168.0.68:8888"}
        elif self._b_proxy:
            return {"http": "192.168.0.58:9999", "https": "192.168.0.58:9999"}
        else:
            return {}


    @classmethod
    def joinURL(cls, base_url: str, path_: str):
        """
        在已有的 URL 后, 增加新的 Path

        :param base_url:
        :type base_url: str
        :param path_:
        :type path_: str
        :return: final_url
        :rtype: str
        """

        # urllib 的 urljoin 无法满足拼接操作, 仅拼接 Domain + path

        base_url = base_url.rstrip("/")
        path_ = path_.lstrip("/")
        return "{}/{}".format(base_url, path_)

    @property
    def proxy(self):
        return self._b_proxy

    @proxy.setter
    def proxy(self, value: str):
        self._b_proxy = value

    @property
    def api_base(self):
        return self._api_base

    @api_base.setter
    def api_base(self, value: str):
        if 'v1' not in value:
            self._api_base = self.joinURL(value, "/v1/")
        else:
            self._api_base = value

    @property
    def api_key(self):
        return self._api_key

    @api_key.setter
    def api_key(self, value: str):
        self._api_key = value

    def check_single_model(self, model_name):
        start_time = time.time()

        # # 这里我们用random.uniform模拟1到3秒之间的随机耗时
        # sleep_time = round(random.uniform(1, 3), 1)
        # time.sleep(sleep_time)  # 模拟网络请求

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": model_name,
            "messages": [{"role": "user", "content": "Hi"}],
            "max_tokens": 1,
            "stream": False
        }

        try:
            response = requests.post(
                self.joinURL(self._api_base, self.PATH_CHAT),
                headers=headers,
                proxies=self.get_proxies(),
                verify=False,
                json=data,
                timeout=10  # 设置10秒超时
            )

            if response.status_code == 200 and "choices" in response.json():
                elapsed_time = round(time.time() - start_time, 2)
                return model_name, elapsed_time
            else:
                elapsed_time = round(time.time() - start_time, 2)
                return None, elapsed_time

        except requests.exceptions.RequestException as e:
            elapsed_time = round(time.time() - start_time, 2)
            return None, elapsed_time


    def get_models(self):
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.get(
                self.joinURL(self._api_base, self.PATH_MODELS),
                headers=headers,
                proxies=self.get_proxies(),
                verify=False,
                timeout=10  # 设置10秒超时
            )

            if response.status_code == 200:
                models_data = response.json()
                model_names = [model['id'] for model in models_data['data']]
                return model_names
            else:
                return []

        except requests.exceptions.RequestException as e:
            print(str(e))
            return []


    def get_care_modes(self):
        return [
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k",
            "gpt-4",
            "gpt-4-32k",
            "gpt-4-all",
            "gpt-4-turbo",
            "gpt-4o",
            "gpt-4o-mini",
            "360-gpt-4o",
            "360-gpt-4o-mini",
            "360gpt-pro",
            "360gpt-pro-32k",
            "360gpt-turbo",
            "360gpt-turbo-32k",
            "360gpt-turbo-360k",
            "chatgpt-4o-latest",
            "claude-3-5-sonnet",
            "claude-3-5-sonnet-20240620",
            "claude-3-5-sonnet@20240620",
            "claude-3.5-sonnet",
            "deepseek-chat",
            "deepseek-coder",
            "Doubao-pro-32k-functioncall",
            "Doubao-pro-4k-functioncall",
            "gemini-1.5-pro",
            "gemini-pro",
            "glm-4",
        ]