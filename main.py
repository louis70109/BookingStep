import logging
import os

if os.getenv('API_ENV') != 'production':
    from dotenv import load_dotenv

    load_dotenv()

import uvicorn
from fastapi import FastAPI, Request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from langchain.chat_models import ChatOpenAI
from langchain.agents import AgentType
from langchain.agents import initialize_agent
from g_calendar import CalendarTool


logging.basicConfig(level=os.getenv('LOG', 'WARNING'))
logger = logging.getLogger(__file__)

app = FastAPI()
line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET', None))
model = ChatOpenAI(
    model="gpt-3.5-turbo-0613",
    openai_api_key=os.getenv('OPENAI_API_KEY'))

tools = [CalendarTool()]

open_ai_agent = initialize_agent(
    tools,
    model,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=False)


@app.post("/webhooks/line")
async def callback(request: Request):
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = await request.body()
    body = body.decode('utf-8')

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        return 'Invalid signature. Please check your channel access token/channel secret.'

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    tool_result = open_ai_agent.run(event.message.text)
    print('-------------------')
    print(tool_result)
    print('-------------------')
    line_bot_api.reply_message(
        event.reply_token,
        [
            TextSendMessage(text="點選以下網址前，先確認時間地點："),
            TextSendMessage(
                text=tool_result)]
    )


if __name__ == "__main__":
    port = int(os.environ.get('PORT', default=8080))
    debug = True if os.environ.get(
        'API_ENV', default='develop') == 'develop' else False
    logging.info('Application will start...')
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=debug)
