from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Configurações do Google Generative AI
google_api_key = 'AIzaSyAKUIoHkHMonZDUuKup9En0HBzeJDkAGGk'
genai.configure(api_key=google_api_key)

model = genai.GenerativeModel(
  model_name="gemini-1.5-pro",
  
  system_instruction="Você é um assistente atencioso e direto nas respostas, falando de forma clara e natural, como se tivesse uma voz real, sem soar artificial ou muito robotizado. Evite emojis e use palavras que fluam bem em uma voz masculina para que a fala saia o menos robotizada possível, mas acessível e amigável. Se alguém perguntar quem você é ou quem te criou, diga que se chama Cosmo, criado por André e Igor, alunos da primeira turma de Análise e Desenvolvimento de Sistemas do IFPI Campus de Piripiri. Explique também que você usa a API do Gemini para responder as perguntas.",
)
chat = model.start_chat(history=[])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/enviar-mensagem', methods=['POST'])
def enviar_mensagem():
    dados = request.json
    mensagem = dados.get('mensagem')
    if mensagem:
        response = chat.send_message(mensagem)
        return jsonify({"resposta": response.text})
    return jsonify({"resposta": "Desculpe, não entendi."})

if __name__ == '__main__':
    app.run(debug=True)
