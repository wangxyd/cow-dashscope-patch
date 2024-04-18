#!/bin/bash

function pause (){
    read -p "按任意键继续..."
}

echo -e "🟣 1. 请确保您已经进入chatgpt-on-wechat目录下！\n示例：如果您的chatgpt-on-wechat安装在/root/chatgpt-on-wechat目录，使用如下命令切换到该目录: cd /root/chatgpt-on-wechat"
pause
ls -l app.py config.py channel/chat_channel.py plugins/plugin.py &> /dev/null
if [ $? -ne 0 ]; then
    echo "🔴 安装失败！请检查是否在chatgpt-on-wechat目录！"
    exit 1
fi

echo -e "🟣 2. 安装灵积模型的Python SDK，如果安装失败或者使用了自定义目录的Python3请手动安装！"
pause
pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple dashscope || pip install -i https://pypi.tuna.tsinghua.edu.cn/simple dashscope || (echo "🟡灵积模型的Python SDK安装失败！请在本程序运行结束后手动安装！" && pause)

echo -e "🟣 3. 开始替换文件以添加支持更多灵积模型，被替换的文件会自动备份！"
pause
TIME=$(date '+%y%m%d%H%M%S')
if [ ! -d "bot/dashscope/" ]; then
    echo "🟢 bot/dashscope不存在，直接将/tmp/cow-dashscope-patch/bot/dashscope复制到bot/dashscope"
    cp -r /tmp/cow-dashscope-patch/bot/dashscope bot/
else
    echo "🟢 备份bot/dashscope/dashscope_bot.py到bot/dashscope/dashscope_bot.py-$TIME"
    mv bot/dashscope/{dashscope_bot.py,dashscope_bot.py-$TIME}
    cp /tmp/cow-dashscope-patch/bot/dashscope/dashscope_bot.py bot/dashscope/dashscope_bot.py
    echo "🟢 备份bot/dashscope/dashscope_session.py到bot/dashscope/dashscope_session.py-$TIME"
    mv bot/dashscope/{dashscope_session.py,dashscope_session.py-$TIME}
    cp /tmp/cow-dashscope-patch/bot/dashscope/dashscope_session.py bot/dashscope/dashscope_session.py
fi
echo "🟢 备份bot/bot_factory.py到bot/bot_factory.py-$TIME"
mv bot/{bot_factory.py,bot_factory.py-$TIME}
cp /tmp/cow-dashscope-patch/bot/bot_factory.py bot/bot_factory.py
echo "🟢 备份bridge/bridge.py到bridge/bridge.py-$TIME"
mv bridge/{bridge.py,bridge.py-$TIME}
cp /tmp/cow-dashscope-patch/bridge/bridge.py bridge/bridge.py
echo "🟢 备份common/const.py到common/const.py-$TIME"
mv common/{const.py,const.py-$TIME}
cp /tmp/cow-dashscope-patch/common/const.py common/const.py
echo "🟢 备份plugins/godcmd/godcmd.py到plugins/godcmd/godcmd.py-$TIME"
mv plugins/godcmd/{godcmd.py,godcmd.py-$TIME}
cp /tmp/cow-dashscope-patch/plugins/godcmd/godcmd.py plugins/godcmd/godcmd.py
echo "🟢 备份config.py到config.py-$TIME"
mv config.py config.py-$TIME
cp /tmp/cow-dashscope-patch/config.py config.py

echo -e "🟣 4. 文件替换完成，开始检查是否替换成功..."
pause
ls -l bot/dashscope/{dashscope_bot.py,dashscope_session.py} bot/bot_factory.py bridge/bridge.py common/const.py plugins/godcmd/godcmd.py config.py
if [ $? -ne 0 ]; then
    echo "🔴 文件替换失败！请保存上面的输出结果，用于手动恢复文件！"
    exit 1
else
    echo -e "🟣 文件替换成功！下一步请手动编辑当前目录下的config.json文件，添加灵积模型的api_key！\n如果您还没有api_key，请访问阿里云灵积模型服务控制台创建API-KEY：https://dashscope.console.aliyun.com/apiKey\n配置示例如下：\n  \"dashscope_api_key\": \"sk-8526ce275dc3r4d43a26z9f91rsa3288\",\n"
    echo -e "🟣 配置完成灵积模型的api_key之后，重启chatgpt-on-wechat即可使用阿里云的灵积模型！\n支持的模型有：qwen-max、qwen-plus、qwen-turbo、qwen-max-0107, qwen-max-0403, qwen-max-longcontext, qwen1.5-72b-chat, qwen1.5-14b-chat, qwen1.5-7b-chat, qwen-72b-chat, qwen-14b-chat, qwen-7b-chat, qwen-1.8b-chat, qwen-1.8b-longcontext-chat, chatglm3-6b\n部分模型可能需要单独申请，另外请注意模型的免费额度有效期及免费额度使用情况！\n安装结束！"
fi