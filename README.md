# parseFetch
解析来之Chrome开发者工具的请求 （Copy as fetch）,生成yaml文件


## 使用
### 拷贝fetch请求 
打开Chrome开发者工具,在网络面板,例如选择登录请求,点击 Copy as fetch 放到文件中命名login.js，必须js结尾
```javascript
fetch("http://testing.tester.cn/api/v1/auth-token/login", {
  "headers": {
    "accept": "application/json, text/plain, */*",
    "accept-language": "zh-CN,zh;q=0.9",
    "cache-control": "no-cache",
    "content-type": "application/json;charset=UTF-8",
    "pragma": "no-cache",
    "x-ft-auth-token": ""
  },
  "referrerPolicy": "strict-origin-when-cross-origin",
  "body": "{\"username\":\"jiangyd\",\"password\":\"123456\"}",
  "method": "POST",
  "mode": "cors",
  "credentials": "omit"
});
```


###执行命令

支持文件，文件夹, 目标存放路径
```text
$ python fetch.py example/login.js

#or
$ python fetch.py example

#or
$ python3 fetch.py example/login.js --dstdir /tmp
{
    "code": 401,
    "content": {},
    "errorCode": "ft.LoginFailed",
    "message": "当前用户不存在/或密码错误",
    "success": false,
    "traceId": "TRACE-2EABC735-5465-4CDC-8B67-D45E65AB6F01"
}


```


### 生成的login.yaml

```yaml
var: {}
api:
- test:
    name: login
    request:
      url: http://testing.tester.cn/api/v1/auth-token/login
      method: POST
      headers:
        content-type: application/json;charset=UTF-8
      body: '{"username":"jiangyd","password":"123456"}'
      validate:
        status_code:
        - expr: ==
          right: 401
          msg: http resp code not match 401
        body:
        - left: code
          expr: ==
          right: 401
          msg: code ,401 not match
        - left: errorCode
          expr: ==
          right: ft.LoginFailed
          msg: errorCode ,ft.LoginFailed not match
        - left: message
          expr: ==
          right: 当前用户不存在/或密码错误
          msg: message ,当前用户不存在/或密码错误 not match
        - left: success
          expr: ==
          right: false
          msg: success ,False not match

```

## 配置文件说明 config.yaml

```yaml
filter:
  excluede_header:
    - accept
    - accept-language
  white_header:
    - content-type
  excluede_verify:
    - traceId
```

### 请求头
`excluede_header` 过滤的请求头

`white_header` 只允许的请求头

如果设置了`white_header`，那么 `excluede_header` 就不生效了

### 过滤验证内容

`excluede_verify` 例如每次请求返回的`traceID`是不一样的，那么这个字段就可以排除了