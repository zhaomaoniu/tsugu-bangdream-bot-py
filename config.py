import json
from pydantic import BaseModel
from typing import Optional, List
from pathlib import Path


class Config(BaseModel):
    agree_disclaimer: str = "Y"
    api_base: str = "http://tsugubot.com:8080"
    use_easy_bg: Optional[bool] = True
    default_servers: Optional[List[str]] = ["3", "0"]
    bind_api_base: str = "http://uid.ksm.ink:7722"
    bot_name: Optional[str] = "tsugu"
    help_trigger: Optional[str] = "help"
    bandori_station_token: Optional[str] = "ZtV4EX2K9Onb"
    token_name: Optional[str] = "Tsugu"
    admin: Optional[List[str]] = ["ALL"]
    ban_groups: Optional[List[str]] = []
    ban_gacha_simulate_groups: Optional[List[str]] = []
    ban_car_station_send: Optional[List[str]] = []
    status_on_echo: Optional[str] = "喜多喜多"
    status_off_echo: Optional[str] = "呜呜zoule"


config_file_path = Path.cwd() / "tsugu_config" / "config.json"
if not config_file_path.parent.exists():
    config_file_path.parent.mkdir()

config = Config()
if config_file_path.exists():
    config = Config.parse_file(config_file_path)
else:
    with open(config_file_path, "w", encoding="UTF-8") as file:
        json.dump(Config().dict(), file, indent=4, ensure_ascii=False)
        disclaimer = """
        kumorin：
        你可以看到，config 文件夹下 config.json 里面的 bind_api_base 默认为 http://uid.ksm.ink:7722 ，是我的api实现绑定。
        必须说的一点：我这里确实可以通过一个人的QQ号查找到绑定过的一个人的游戏uid，我觉得这根本不算什么，又不是uid查QQ号，
        我做这个项目为的是让更多的群用上 Tsugu，而不是为了某些人遮遮掩掩的特殊需求。
        你要是觉得你数据绑定关系不安全，请务必不要绑定，已经绑了的再绑定一次覆盖掉，不会有存留。
        这是一个很方便的 Tsugu，我也希望大家都能使用。
        有问题、建议、困难，需求 进群 666808414 问 就行，美少女客服在线解答（
        这个项目大方向上支持 Tsugu 后端全部功能，细微操作上稍有出入，未来也会同步更新。
        bug一经发现会修复，遇到问题欢迎来群里反馈，或者提 issue，专栏评论回复。
        感谢您的部署。
        
        已创建好默认配置文件，直接重启本程序即可运行。可以查看配置项是否需要修改，遇到问题欢迎从上方渠道交流反馈。
        
        zhaomaoniu：
        kumorin可爱捏。
        
        """
        print(f"默认配置已写入到: {config_file_path}\n请修改配置后重启。\n免责声明：\n{disclaimer}")
        exit()


# cmd_dict 可以用来设置别名
cmd_dict = {
    config.help_trigger: "Help",
    "swc": "Swc",
    "查曲": "/searchSong",
    "查活动": "/searchEvent",
    "查谱面": "/songChart",
    "查铺面": "/songChart",  # 别名
    "查卡面": "/getCardIllustration",
    "查角色": "/searchCharacter",
    "查卡池": "/searchGacha",
    "查卡": "/searchCard",  # 查卡一定要放在 查卡面 查卡池 后面，原因自己想
    "查玩家": "/searchPlayer",
    "玩家状态": "PlayerStatus",
    "国服玩家状态": "PlayerStatus",
    "日服玩家状态": "PlayerStatus",
    "国际服玩家状态": "PlayerStatus",
    "台服玩家状态": "PlayerStatus",
    "韩服玩家状态": "PlayerStatus",
    "绑定玩家": "BindPlayer",  # （使用自建数据库api，只支持日服，国服）
    # （支持自动车牌转发）
    "查询分数表": "/songMeta",
    "查分数表": "/songMeta",  # 别名 # 别名放在后面
    "ycm": "/roomList",  # （只支持官方车站的车）
    "ycxall": "/ycxAll",
    "ycx": "/ycx",  # ycx一定要放在 ycxall 后面，原因自己想
    "lsycx": "/lsycx",
    "抽卡模拟": "/gachaSimulate",
    "开启个人车牌转发": "BD_STATION_ON_PERSONAL",
    "关闭个人车牌转发": "BD_STATION_OFF_PERSONAL",
    "主服务器": "Main_server",
    "国服模式": "SET_mode",
    "日服模式": "SET_mode",
    "国际服模式": "SET_mode",
    "台服模式": "SET_mode",
    "韩服模式": "SET_mode",
}

# 此列表键与 cmd_dict 保持一致
cmd_help_dict = {
    "swc": f"swc off {config.bot_name} ·关闭本群Tsugu\nswc on {config.bot_name} ·开启本群Tsugu",
    "查曲": "查曲 信息 ·列表查曲\n查曲 ID ·查寻单曲信息",
    "查活动": "查活动 信息 ·列表查活动\n查活动 ID ·查寻活动信息",
    "查谱面": "查谱面 ID 难度 ·输出谱面预览",
    "查铺面": "查谱面 ID 难度 ·输出谱面预览",  # 别名
    "查卡面": "查卡面 ID ·查询卡片插画",
    "查角色": "查角色 ID/关键词 ·查询角色的信息",
    "查卡池": "查卡池 ID 查询卡池信息",
    "查卡": "查卡 信息 ·列表查卡面\n查卡 ID ·查询卡面信息",  # 查卡一定要放在 查卡面 查卡池 后面，原因自己想
    "查玩家": "查玩家 UID 服务器 ·查询对应玩家信息",
    "玩家状态": "玩家状态 ·查询自己的玩家状态\n玩家状态 服务器 ·查询指定服务器的玩家状态",
    "国服玩家状态": "国服玩家状态 ·查询自己的国服玩家状态",
    "日服玩家状态": "日服玩家状态 ·查询自己的日服玩家状态",
    "国际服玩家状态": "国际服玩家状态 ·查询自己的国际服玩家状态",
    "台服玩家状态": "台服玩家状态 ·查询自己的台服玩家状态",
    "韩服玩家状态": "韩服玩家状态 ·查询自己的韩服玩家状态",
    "绑定玩家": "发送 绑定玩家 uid cn ·绑定国服\n发送 绑定玩家 uid jp ·绑定日服\n发送 绑定玩家 uid kr ·绑定韩服\n发送 绑定玩家 uid en ·绑定国际服\n发送 绑定玩家 uid tw ·绑定台服\n注意：客观存在通过聊天平台账号查询UID的风险，介意者慎绑，请不要绑定他人账号。",
    # （支持自动车牌转发）
    "查询分数表": "查询分数表 服务器 ·查询歌曲分数表，服务器非必填",
    "查分数表": "查询分数表 服务器 ·查询歌曲分数表，服务器非必填",  # 别名 # 别名放在后面
    "ycm": "ycm ·获取所有车牌车牌",  # （只支持官方车站的车）
    "ycxall": "ycxAll 活动ID ·查询所有档位的预测线，只支持国服，活动ID非必填",
    "ycx": "ycx 档位 活动ID ·查询预测线，只支持国服，活动ID非必填",  # ycx一定要放在 ycxall 后面，原因自己想
    "lsycx": "lsycx 档位 活动ID ·返回档线、预测线、近4期同类活动的档线，只支持国服，活动ID非必填",
    "抽卡模拟": "抽卡模拟 次数 卡池ID ·抽卡模拟，次数、卡池ID非必填",
    "开启个人车牌转发": "开启个人车牌转发",
    "关闭个人车牌转发": "开启个人车牌转发",
    "主服务器": "主服务器 cn ·切换国服\n主服务器 jp ·切换日服\n主服务器 kr ·切换韩服\n主服务器 en ·切换国际服\n主服务器 tw ·切换台服\n",
    "国服模式": "国服模式",
    "日服模式": "日服模式",
    "国际服模式": "国际服模式",
    "台服模式": "台服模式",
    "韩服模式": "韩服模式",
}

language_mapping = {"jp": 0, "en": 1, "tw": 2, "cn": 3, "kr": 4}
chinese_language_mapping = {"日服": 0, "国际服": 1, "台服": 2, "国服": 3, "韩服": 4}

car_config = {
    "car": [
        "车",
        "w",
        "W",
        "国",
        "日",
        "火",
        "q",
        "开",
        "Q",
        "万",
        "缺",
        "来",
        "差",
        "奇迹",
        "冲",
        "途",
        "分",
        "禁",
    ],
    "fake": [
        "114514",
        "假车",
        "测试",
        "野兽",
        "恶臭",
        "1919",
        "下北泽",
        "粪",
        "糞",
        "臭",
        "雀魂",
        "麻将",
        "打牌",
        "maj",
        "麻",
        "[",
        "]",
        "断幺",
        "11451",
        "xiabeize",
        "qq.com",
        "@",
        "q0",
        "q5",
        "q6",
        "q7",
        "q8",
        "q9",
        "q10",
        "腾讯会议",
        "master",
        "疯狂星期四",
        "离开了我们",
        "日元",
        "av",
        "bv",
    ],
}
