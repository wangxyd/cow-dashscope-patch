## 功能

用于一键升级chatgpt-on-wechat以便支持阿里云灵积模型。

支持的模型有：qwen-max、qwen-plus、qwen-turbo、qwen-max-0107, qwen-max-0403, qwen-max-longcontext, qwen1.5-72b-chat, qwen1.5-14b-chat, qwen1.5-7b-chat, qwen-72b-chat, qwen-14b-chat, qwen-7b-chat, qwen-1.8b-chat, qwen-1.8b-longcontext-chat, chatglm3-6b

## 升级方法

1. 运行升级脚本
```sh
# 1. pull项目到本地。为了升级步骤简单，这里必须将项目pull到/root目录
cd /root && git pull https://github.com/wangxyd/cow-dashscope-patch.git

# 2. 切换到您的chatgpt-on-wechat安装目录。如果您的chatgpt-on-wechat安装在/root/chatgpt-on-wechat目录，使用如下命令切换到该目录:
cd /root/chatgpt-on-wechat

# 3. 运行升级脚本patch.sh。
bash /root/cow-dashscope-patch/patch.sh
```

2. 文件替换成功后请手动编辑当前目录下的chatgpt-on-wechat主配置文件`config.json`，修改模型并添加灵积模型的api_key！
    + 如果您还没有api_key，请访问阿里云灵积模型服务控制台创建API-KEY：https://dashscope.console.aliyun.com/apiKey
    + 配置示例如下：
    ```json
    "model": "qwen-max-0107",
    "dashscope_api_key": "sk-8526ce275dc3r4d43a26z9f91rsa3288",
    ```

3. 配置修改完成之后，重启chatgpt-on-wechat即可使用阿里云的众多灵积模型！

## 备注

1. 如果出现“🔴”，表示升级过程出现问题，请检查输出信息，处理问题后再继续下一步！
2. 可以通过私聊机器人使用管理员命令`#model`切换模型，例如：`#model qwen-max-0403`
3. 支持的模型有：qwen-max、qwen-plus、qwen-turbo、qwen-max-0107, qwen-max-0403, qwen-max-longcontext, qwen1.5-72b-chat, qwen1.5-14b-chat, qwen1.5-7b-chat, qwen-72b-chat, qwen-14b-chat, qwen-7b-chat, qwen-1.8b-chat, qwen-1.8b-longcontext-chat, chatglm3-6b
4. 部分模型可能需要单独申请，另外请注意模型的免费额度有效期及免费额度使用情况！