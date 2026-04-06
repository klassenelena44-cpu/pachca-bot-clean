from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

API_TOKEN = "aCgIdxZ1YL3JXlX1SVlTbx7CaIRRAo-a_TscQ3yMLX8"

headers = {
    "Authorization": f"Bearer {API_TOKEN}"
}

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Бот-почтальон</title>

    <style>
        body {
            font-family: Arial;
            background: #f4f6f9;
            display: flex;
            justify-content: center;
            padding: 40px;
        }

        .container {
            background: white;
            padding: 25px;
            border-radius: 14px;
            width: 520px;
        }

        h2 {
            margin-bottom: 15px;
        }

        input, textarea {
            width: 100%;
            padding: 10px;
            border-radius: 8px;
            border: 1px solid #ddd;
        }

        textarea {
            margin-top: 10px;
        }

        .chat-list {
            max-height: 250px;
            overflow-y: auto;
            border: 1px solid #eee;
            padding: 10px;
            margin-bottom: 15px;
        }

        .chat-item {
            padding: 5px 0;
        }

        button {
            margin-top: 15px;
            width: 100%;
            padding: 12px;
            background: #4f46e5;
            color: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 500;
        }

        button:hover {
            background: #4338ca;
        }

        .status {
            margin-top: 15px;
            padding: 10px;
            border-radius: 8px;
            background: #e6f9ec;
            color: #1e7e34;
            display: none;
        }
    </style>

    <script>
        function searchChats() {
            let input = document.getElementById("search").value.toLowerCase();
            let chats = document.getElementsByClassName("chat-item");

            for (let i = 0; i < chats.length; i++) {
                let text = chats[i].innerText.toLowerCase();
                chats[i].style.display = text.includes(input) ? "" : "none";
            }
        }
    </script>

</head>

<body>
<div class="container">
    <h2>Рассылка</h2>

    <input type="text" id="search" onkeyup="searchChats()" placeholder="Поиск..."><br><br>

    <form method="post">
        <div class="chat-list">
            {% for chat in chats %}
                <div class="chat-item">
                    <label>
                        <input type="checkbox" name="chat_ids" value="{{ chat['id'] }}">
                        {{ chat['name'] }}
                    </label>
                </div>
            {% endfor %}
        </div>

        <textarea name="message" rows="4" style="width:100%"></textarea><br><br>

        <button type="submit">Отправить</button>
    </form>

    <p>{{ status }}</p>
</div>
</body>
</html>
"""

def get_all_chats():
    all_chats = []
    page = 1

    while True:
        response = requests.get(
            f"https://api.pachca.com/api/shared/v1/chats?page={page}",
            headers=headers
        )

        data = response.json()
        chats = data.get("data", [])

        if not chats:
            break

        all_chats.extend(chats)
        page += 1

    for chat in all_chats:
        chat["name"] = (
            chat.get("name")
            or chat.get("title")
            or f"Chat {chat['id']}"
        )

    return all_chats


@app.route("/", methods=["GET", "POST"])
def index():
    chats = get_all_chats()
    status = ""

    if request.method == "POST":
        chat_ids = request.form.getlist("chat_ids")
        message = request.form["message"]

        success = 0

        for chat_id in chat_ids:
            response = requests.post(
                "https://api.pachca.com/api/shared/v1/messages",
                headers=headers,
                json={
                    "message": {
                        "entity_id": chat_id,
                        "content": message
                    }
                }
            )
            if response.status_code == 200:
                success += 1

        status = f"Отправлено в {success} чатов"

    return render_template_string(HTML, chats=chats, status=status)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
