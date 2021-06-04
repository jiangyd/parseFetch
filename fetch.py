import sys
import os
import yaml
import json
import collections
import requests
import argparse

null = None
true = True
false = False


class parseFetch(object):
    def __init__(self, path, dstdir=None):
        self.path = path
        self.file = None
        if os.path.exists(dstdir) and not os.path.isdir(dstdir):
            print("目标存放必须为目录")
            sys.exit(1)
        if not os.path.exists(dstdir):
            os.makedirs(dstdir)
        self.dstdir = dstdir
        with open('config.yaml', 'r') as f:
            config = f.read()
        self.config = yaml.load(config, Loader=yaml.FullLoader)
        self.excluede_verify = []
        self.white_header = []
        self.excluede_header = []
        try:
            self.excluede_header = [x.lower() for x in self.config.get("filter").get("excluede_header", [])]
        except Exception as e:
            pass
        try:
            self.white_header = [x.lower() for x in self.config.get("filter").get("white_header", [])]
        except Exception as e:
            pass
        try:
            self.excluede_verify = [x.lower() for x in self.config.get("filter").get("excluede_verify", [])]
        except Exception as e:
            pass

        self.endswith = ".js"

    def run(self):
        """

        :return:
        """
        filepath = self.getFilePath(path=self.path)
        self.getFileData(path=filepath)

    def getFilePath(self, path):
        """
        :param path: 文件路径或目录
        :return: 符合条件的文件列表
        """
        fs = []
        if os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                [fs.append(os.path.join(root, f)) for f in files if f.endswith(self.endswith)]
        elif os.path.isfile(path):
            fs.append(path)
        return fs

    def getFileData(self, path):
        """
        :param path:  读取文件内容
        :return:
        """
        for file in path:
            self.file = file
            with open(file, 'r') as f:
                data = f.read()
                self.parseData(data)

    def parseData(self, data):
        """
        :param data: 代码内容
        :return:
        """
        data = "self." + data.rstrip(";")
        exec(compile(data, '', 'exec'))

    def filter(self, data=None, status_code=None, type=None):
        """

        :param data: 响应内容
        :param status_code: 响应code
        :param type: header or verify
        :return:
        """
        if type == "header":
            newheader = {}
            # 优先白名单，如果白名单有设置，黑名单就无效了
            if len(self.white_header) > 0:
                for key in self.white_header:
                    newheader[key] = data[key]
            else:
                for key in data.keys():
                    if not key.lower() in self.excluede_header:
                        newheader[key] = data[key]
            return newheader
        elif type == "verify":
            newdata = {}

            # 加入响应码
            newdata["status_code"] = [{"expr": "==", "right": status_code,
                                       "msg": "http resp code not match {code}".format(code=status_code)}]

            newdata["body"] = []

            # newdata["duration"] = [
            #     {"expr": "<=", "right": data.elapsed.seconds + 8, "msg": "duration not less then 8 second"}]
            #
            # # 加入响应时间

            for key, value in data.items():
                item = {}
                if not key.lower() in self.excluede_verify and isinstance(value, (int, float, str, bool)):
                    item["left"] = key
                    item["expr"] = "=="
                    item["right"] = value
                    item["msg"] = r"{key} ,{value} not match".format(key=key, value=value)
                    newdata["body"].append(item)
            return newdata

    def fetch(self, url, req):
        try:
            yamldata = {"var": {}, "api": []}
            test = lambda: collections.defaultdict(test)
            some_test = test()

            some_test["name"] = os.path.basename(self.file).rstrip(self.endswith)
            some_test["request"]["url"] = url
            some_test["request"]["method"] = req["method"]
            some_test["request"]["headers"] = self.filter(data=req["headers"], type="header")
            some_test["request"]["body"] = req["body"]

            if req.get("response", None) is not None and req.get("response_code", None) is not None:
                data = req.get("response")
                status_code = req.get("response_code")
                # print(json.dumps(data, indent=4))


            else:
                resp = requests.request(method=req["method"], url=url, headers=req["headers"], data=req["body"])
                data = resp.json()
                status_code = resp.status_code
                print(json.dumps(data, indent=4,ensure_ascii=False))

            some_test["request"]["validate"] = self.filter(data=data, status_code=status_code, type="verify")
            yamldata["api"].append({"test": json.loads(json.dumps(some_test))})

            yamlname = os.path.join(self.dstdir, os.path.basename(self.file).rstrip(self.endswith) + ".yaml")
            yamlname = os.path.abspath(yamlname)

            with open(yamlname, "w") as f:
                yaml.safe_dump(yamldata, f, sort_keys=False, allow_unicode=True)
        except Exception as e:
            print(e)


parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument("path", type=str, help="源文件或目录")
parser.add_argument("--dstdir", default=".", required=False, type=str, help="目标存放目录")
args = parser.parse_args()

path = args.path
# path = sys.argv[1]
if os.path.exists(path):
    t = parseFetch(path=path, dstdir=args.dstdir)
    t.run()

else:
    print(f"{path} is not found")
    sys.exit(1)
