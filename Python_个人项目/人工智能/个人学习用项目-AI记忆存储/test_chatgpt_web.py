from flask import Flask, request, jsonify, render_template_string
import requests

app = Flask(__name__)

# ================================
# 配置项（你只需要改这里）
# ================================
API_KEY = "rk-000001"
API_URL = "http://127.0.0.1:8765/v1/chat/completions"
MODEL = "gpt-4o-mini"
# ================================


# --------- 简约唯美网页 ---------
PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>GPT Chat</title>

    <style>
        body {
            margin: 0;
            font-family: "Segoe UI", sans-serif;
            background: linear-gradient(135deg, #f7f7f7, #e9eef6);
            display: flex;
            flex-direction: column;
            height: 100vh;
        }

        header {
            background: #ffffffcc;
            backdrop-filter: blur(6px);
            padding: 15px;
            text-align: center;
            font-size: 22px;
            font-weight: bold;
            box-shadow: 0 2px 4px #0001;
        }

        #chat {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
        }

        .msg {
            max-width: 75%;
            padding: 10px 14px;
            margin: 10px 0;
            border-radius: 12px;
            line-height: 1.5;
            white-space: pre-wrap;
            box-shadow: 0 2px 6px #0001;
        }

        .user {
            background: #d8e9ff;
            align-self: flex-end;
        }

        .bot {
            background: #ffffff;
            align-self: flex-start;
        }

        #input-area {
            display: flex;
            padding: 10px;
            background: #fff;
            box-shadow: 0 -2px 4px #0001;
        }

        #input-box {
            flex: 1;
            padding: 10px;
            font-size: 16px;
            border-radius: 8px;
            border: 1px solid #ccc;
        }

        button {
            padding: 10px 18px;
            margin-left: 10px;
            font-size: 16px;
            background: #4a82ff;
            border: none;
            border-radius: 8px;
            color: white;
            cursor: pointer;
            box-shadow: 0 2px 4px #0003;
        }

        button:hover {
            background: #336BFF;
        }
    </style>
</head>

<body>
<header>GPT Chat</header>

<div id="chat"></div>

<div id="input-area">
    <input id="input-box" placeholder="说点什么..." onkeydown="if(event.key==='Enter') sendMsg()">
    <button onclick="sendMsg()">发送</button>
</div>

<script>
function addMessage(text, sender) {
    const chat = document.getElementById("chat");
    const msg = document.createElement("div");
    msg.className = "msg " + sender;
    msg.textContent = text;
    chat.appendChild(msg);
    chat.scrollTop = chat.scrollHeight;
}

function sendMsg() {
    const input = document.getElementById("input-box");
    const text = input.value.trim();
    if (!text) return;

    addMessage(text, "user");
    input.value = "";

    fetch("/chat", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({msg: text})
    })
    .then(res => res.json())
    .then(data => addMessage(data.reply, "bot"))
    .catch(err => addMessage("错误：" + err, "bot"));
}
</script>

</body>
</html>
"""



@app.route("/")
def index():
    return render_template_string(PAGE)



@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("msg")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": user_msg}
        ]
    }

    try:
        r = requests.post(API_URL, headers=headers, json=payload)
        r.raise_for_status()
        reply = r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        reply = f"API 调用失败：{e}"

    return jsonify({"reply": reply})


if __name__ == "__main__":
    print("服务器已启动")
    app.run(host="0.0.0.0", port=5000, debug=False)
