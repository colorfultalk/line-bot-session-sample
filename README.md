# line-bot-session-sample

line-bot-sdk-pythonのgithubに上がっているサンプルをベースにセッション管理してみた．  
https://github.com/line/line-bot-sdk-python/tree/master/examples/flask-kitchensink

以下の情報をデータベースに格納している．

| id | user | data | expiration |
|:---|:-----|:-----|:-----------|
| オートインクリメントのid | ユーザを識別する文字列(lineでは`user_id`) | 保存したい情報(json形式) | 有効期限 |

## Getting started

```
$ export LINE_CHANNEL_SECRET=YOUR_LINE_CHANNEL_SECRET
$ export LINE_CHANNEL_ACCESS_TOKEN=YOUR_LINE_CHANNEL_ACCESS_TOKEN

$ pip install -r requirements.txt

$ python app.py
```

## How to use

botSessionInterfaceをインスタンス化
```
from botsession import BotSessionInterface
botSessionInterface = BotSessionInterface()
```

session moduleがlineのuser_idを参照できるようにするために，flask.gに格納する
`open_session` でセッションを復帰/新規作成する(戻り値はsession object)

```
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        events = parser.parse(body, signature)

        # set user_id to global variable
        user_id = events.pop().source.user_id
        g.user_id = user_id

        # set bot session
        session = botSessionInterface.open_session(app, request)
        g.session = session

        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'
```

セッションに持たせたい情報はdictionaryで格納できる．

```
session['status'] = event.message.text
```

リクエスト処理の後にセッションを保存しておくと，次のリクエスト時にlineの`user_id`をキーとして保存したセッションを復帰させることができる．
```
@app.after_request
def after_request(response):
    session = getattr(g, 'session', None)
    botSessionInterface.save_session(app, session, response)

    return response
```

## flask session customize
flaskで独自のセッション管理モジュールを作るには，`CallbackDict`, `SessionMixin`を継承したsessionクラスと，
`SessionInterface`の`open_session`と`save_session`を実装すればよい．

flaskの標準セッションモジュール`SecureCookieSession`の実装が参考になる．  
https://github.com/pallets/flask/blob/master/flask/sessions.py

## Reference
- flask API reference: http://flask.pocoo.org/docs/0.12/api/#flask.Flask.after_request
- Server-side sessions with MongoDB: http://flask.pocoo.org/snippets/110/
- flaskのソースコード: https://github.com/pallets/flask
