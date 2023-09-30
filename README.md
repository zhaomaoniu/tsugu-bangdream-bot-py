# tsugu-bangdream-bot-py
✨ 使用 Python 编写的  tsugu-bangdream-bot 接口实现 ✨

## 简介
本项目重构自 [tsugu-bangdream-bot-lite-py](https://github.com/kumoSleeping/tsugu-bangdream-bot-lite-py)，根据 [tsugu-bangdream-bot](https://github.com/Yamamoto-2/tsugu-bangdream-bot) backend 的 API 实现了一套能够直接调用的函数与部分数据存储功能，提供了一个 `get_result` 函数，能够方便地接入到各个基于 Python 的机器人框架中。

（不会写 README，等 kumo 在 tsugu-bangdream-bot-lite-py 完善吧）

## 环境
支持 Python38 及以上
```
pip install -r requirements.txt
```

## 配置
导入本模块时，模块会进行初始化，请根据提示，在 `运行目录/tsugu_config/config.json` 中，修改配置文件

## 调用
将仓库克隆到本地后，重命名项目文件夹为 `tsugu`

```
from .tsugu import get_result

# 获取必要的数据
message: str
user_id: int
group_id: Optional[int]

# 调用函数
result = get_result(message, user_id, group_id)

"""
result 是一个 List[Dict[str, str]] 形式的对象
例:
[
    {
        "type": "string",
        "string": "myc",
    },
    {
        "type": "base64",
        "string": "...",
    },
]
"""
```


## 感谢
- [GetQPlayerUid](https://github.com/kumoSleeping/GetQPlayerUid) > [kumo](https://github.com/kumoSleeping)
- [tsugu-bangdream-bot-lite-py](https://github.com/kumoSleeping/tsugu-bangdream-bot-lite-py) > [kumo](https://github.com/kumoSleeping)
- [tsugu-bangdream-bot](https://github.com/Yamamoto-2/tsugu-bangdream-bot) > [山本](https://github.com/Yamamoto-2)