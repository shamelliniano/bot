import requests
import openai
from flask import Flask, request, jsonify

GOOGLE_SHEET_WEBHOOK = "https://script.google.com/macros/s/AKfycbzOCJq7Qy1gSxUvxJDzB5XWutGL09d8q_96QagIIwGc_GOxYprE323ZRqDga6NrmZ7j/exec"
OPENAI_API_KEY = "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"

openai.api_key = OPENAI_API_KEY

app = Flask(__name__)

def get_products_from_sheets(query):
    try:
        params = {"query": query}
        response = requests.get(GOOGLE_SHEET_WEBHOOK, params=params, timeout=10)
        if response.status_code == 200:
            return response.text.strip()
        else:
            print("Ошибка Google Sheets:", response.status_code, response.text)
            return ""
    except Exception as e:
        print("Ошибка при обращении к Google Sheets:", e)
        return ""

def ask_gpt(user_message, products):
    prompt = (
        "Ниже приведён разговор с помощником ИИ, использующим WhatsApp. "
        "Помощник услужливый, умный, дружелюбный и всегда старается помочь клиенту подобрать подходящий товар.\n\n"
        "Вот список всех товаров магазина:\n"
        f"{products}\n\n"
        "Если клиент спрашивает о товаре, ищи не только точные совпадения, но и похожие по смыслу. "
        "Если не нашёл точного совпадения — предложи похожие товары. "
        "Если не понял запрос — уточни у клиента. "
        "В ответе используй дружелюбный и профессиональный стиль.\n\n"
        f"Вопрос клиента: {user_message}\n2::"
    )
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("OpenAI error:", e)
        return "Ошибка при обращении к ИИ. Попробуйте позже."

@app.route("/whatsapp", methods=["POST"])
def whatsapp_webhook():
    data = request.json
    user_message = data.get("message", "")
    products = get_products_from_sheets(user_message)
    answer = ask_gpt(user_message, products)
   return jsonify({"replies": [answer]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
