# encoding:utf-8

from bot.bot import Bot
from bot.session_manager import SessionManager
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from common.log import logger
from config import conf, load_config
from .dashscope_session import DashscopeSession
import os
import dashscope
from http import HTTPStatus

dashscope_models = {
    "qwen-max": dashscope.Generation.Models.qwen_max,
    "qwen-plus": dashscope.Generation.Models.qwen_plus,
    "qwen-turbo": dashscope.Generation.Models.qwen_turbo,
    "qwen-max-0107": "qwen-max-0107",
    "qwen-max-0403": "qwen-max-0403",
    "qwen-max-longcontext": "qwen-max-longcontext",
    "灵儿-5-turbo": "灵儿-5-turbo", # 实际上是qwen-max-0107
    "qwen1.5-72b-chat": "qwen1.5-72b-chat", # qwen1.5只能在灵积看使用情况
    "qwen1.5-14b-chat": "qwen1.5-14b-chat",
    "qwen1.5-7b-chat": "qwen1.5-7b-chat",
    "qwen-72b-chat": "qwen-72b-chat",
    "qwen-14b-chat": "qwen-14b-chat",
    "qwen-7b-chat": "qwen-7b-chat",
    "qwen-1.8b-chat": "qwen-1.8b-chat",
    "qwen-1.8b-longcontext-chat": "qwen-1.8b-longcontext-chat",
    "chatglm3-6b": "chatglm3-6b" # 删除了其他申请试用无线Pending的第三发大模型
}

# Dashscope对话模型API
class DashscopeBot(Bot):
    def __init__(self):
        super().__init__()
        self.sessions = SessionManager(DashscopeSession, model=conf().get("model") or "qwen-plus")
        self.model_name = conf().get("model") or "qwen-plus"
        self.model_name = "qwen-max-0107" if self.model_name=="灵儿-5-turbo" else self.model_name
        self.api_key = conf().get("dashscope_api_key")
        os.environ["DASHSCOPE_API_KEY"] = self.api_key
        self.client = dashscope.Generation

    def reply(self, query, context=None):
        # acquire reply content
        if context.type == ContextType.TEXT:
            logger.info("[DASHSCOPE] query={}".format(query))

            session_id = context["session_id"]
            reply = None
            clear_memory_commands = conf().get("clear_memory_commands", ["#清除记忆"])
            if query in clear_memory_commands:
                self.sessions.clear_session(session_id)
                reply = Reply(ReplyType.INFO, "记忆已清除")
            elif query == "#清除所有":
                self.sessions.clear_all_session()
                reply = Reply(ReplyType.INFO, "所有人记忆已清除")
            elif query == "#更新配置":
                load_config()
                reply = Reply(ReplyType.INFO, "配置已更新")
            if reply:
                return reply
            session = self.sessions.session_query(query, session_id)
            # START: 添加了如下纠正session.messages的代码
            session_messages = self.filter_messages(session.messages)
            if session.messages != session_messages:
                logger.warning(f"[DASHSCOPE] Session messages have been corrected, old message: {session.messages}")
                session.messages = session_messages
            # END
            logger.debug("[DASHSCOPE] session query={}".format(session.messages))

            reply_content = self.reply_text(session)
            logger.debug(
                "[DASHSCOPE] new_query={}, session_id={}, reply_cont={}, completion_tokens={}".format(
                    session.messages,
                    session_id,
                    reply_content["content"],
                    reply_content["completion_tokens"],
                )
            )
            if reply_content["completion_tokens"] == 0 and len(reply_content["content"]) > 0:
                reply = Reply(ReplyType.ERROR, reply_content["content"])
            elif reply_content["completion_tokens"] > 0:
                self.sessions.session_reply(reply_content["content"], session_id, reply_content["total_tokens"])
                reply = Reply(ReplyType.TEXT, reply_content["content"])
            else:
                reply = Reply(ReplyType.ERROR, reply_content["content"])
                logger.debug("[DASHSCOPE] reply {} used 0 tokens.".format(reply_content))
            return reply
        else:
            reply = Reply(ReplyType.ERROR, "Bot不支持处理{}类型的消息".format(context.type))
            return reply

    def reply_text(self, session: DashscopeSession, retry_count=0) -> dict:
        """
        call openai's ChatCompletion to get the answer
        :param session: a conversation session
        :param session_id: session id
        :param retry_count: retry count
        :return: {}
        """
        try:
            dashscope.api_key = self.api_key
            response = self.client.call(
                dashscope_models[self.model_name],
                messages=session.messages,
                result_format="message"
            )
            if response.status_code == HTTPStatus.OK:
                content = response.output.choices[0]["message"]["content"]
                return {
                    "total_tokens": response.usage["total_tokens"],
                    "completion_tokens": response.usage["output_tokens"],
                    "content": content,
                }
            else:
                logger.error('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
                    response.request_id, response.status_code,
                    response.code, response.message
                ))
                result = {"completion_tokens": 0, "content": "我现在有点累了，等会再来吧"}
                need_retry = retry_count < 2
                result = {"completion_tokens": 0, "content": "我现在有点累了，等会再来吧"}
                if need_retry:
                    return self.reply_text(session, retry_count + 1)
                else:
                    return result
        except Exception as e:
            logger.exception(e)
            need_retry = retry_count < 2
            result = {"completion_tokens": 0, "content": "我现在有点累了，等会再来吧"}
            if need_retry:
                return self.reply_text(session, retry_count + 1)
            else:
                return result

    # 添加了如下纠正session.messages的函数，避免经常发生我现在有点累了
    def filter_messages(self, messages: list):
        res = []
        if not messages:
            return res
        turn = "user"
        for i in range(len(messages) - 1, -1, -1):
            message = messages[i]
            if message.get("role") == 'system':
                res.insert(0, message)
                break
            if message.get("role") != turn:
                continue
            res.insert(0, message)
            if turn == "user":
                turn = "assistant"
            elif turn == "assistant":
                turn = "user"
        return res