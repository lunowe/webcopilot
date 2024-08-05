from flask import Flask, request, jsonify, session, redirect, url_for, make_response, render_template, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from chatbot import Chatbot
import re

app = Flask(__name__)
# CORS(app)
# socketio = SocketIO(app, cors_allowed_origins="*")

chatbot = Chatbot()

global chain
global docs
chain = ""
docs = ""

def format_message(message):
    # Replace newline characters with <br>
    formatted_message = message.replace('\n', '<br>')
    
    # Replace **text** with <strong>text</strong>
    formatted_message = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', formatted_message)
    
    return formatted_message


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/test")
def test():
    docs = chatbot.load_web_docs("https://en.wikipedia.org/wiki/Python_(programming_language)")
    chain = chatbot.setup_summary_chain("detailed")
    message = chain.invoke(docs)["output_text"]
    formatted_message = format_message(message)
    return formatted_message

@app.route("/load_webpage", methods=["POST"])
def load_webpage():
    global chain
    global docs
    url = request.json["url"]
    docs = chatbot.load_web_docs(url)
    chain = chatbot.setup_summary_chain("detailed")

    return jsonify({"message": "page loaded successfully"})

@app.route("/summarize")
def summarize():
    global chain
    global docs
    message = chain.invoke(docs)["output_text"]
    formatted_message = format_message(message)
    return jsonify({"message": formatted_message})

if __name__ == "__main__":
    # socketio.run(app, debug=True, port=8080)
    app.run(debug=True, host='0.0.0.0', port=8080)