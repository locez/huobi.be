# huobi.be

2021 年发起抽奖活动, 为中奖者写 50 行代码, 为中奖者需求

# 简介

可爬取 huobi.be 指定货币的价格趋势, 然后绘图发送到指定邮箱

# 安装依赖

```shell script
pip install -U matplotlib selenium
```

还需要安装 [chromedriver](https://sites.google.com/a/chromium.org/chromedriver) [chrome](https://www.google.com/chrome)

# 使用

修改 main.py 中的配置
```shell script
# config
# 监控的地址
url = "https://www.huobi.be/zh-cn/exchange/ada_usdt/"
# 每天抓取多少次数据
times_of_one_day = 3

# smtp 配置
email_smtp_host = "smtp.qq.com"
email_smtp_port = 465
email_user = "example@example.com"
email_pass = "pass"

# 发送者
sender = email_user
# 接受方, 为数组
receivers = ["example@example.com"]
# 邮件主题
subject = "Monitor Ada"
```

# 运行

```shell script
python main.py
```

