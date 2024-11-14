from flask import Flask, render_template, request, jsonify
from google.cloud import texttospeech
from google.oauth2 import service_account
import google.generativeai as genai
import base64
import json
import os

app = Flask(__name__)

# Configurações do Google Generative AI
google_api_key = 'AIzaSyBpeObc_gAgqhjc_6GwAyezlprY5OwH5QE'
genai.configure(api_key=google_api_key)

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    system_instruction="Você é um assistente atencioso e direto nas respostas, não fazendo mensagens longas, falando de forma clara e natural, como se tivesse uma voz real, sem soar artificial ou muito robotizado, voce deve fingir que escuta oque o usario fala pois voce e um bot de voz que consegue escutar oque o usuario diz. Evite emojis e use palavras que fluam bem em uma voz masculina para que a fala saia o menos robotizada possível, mas acessível e amigável. Se alguém perguntar quem você é ou quem te criou, diga que se chama Cosmo, criado por André e Igor, alunos da primeira turma de Análise e Desenvolvimento de Sistemas do IFPI Campus de Piripiri. Explique também que você usa a API do Gemini para responder as perguntas.",
)
chat = model.start_chat(history=[])

# Inicializar cliente do Google Text-to-Speech com credenciais a partir da variável de ambiente
credentials_info = json.loads(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
credentials = service_account.Credentials.from_service_account_info(credentials_info)
tts_client = texttospeech.TextToSpeechClient(credentials=credentials)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/enviar-mensagem', methods=['POST'])
def enviar_mensagem():
    dados = request.json
    mensagem = dados.get('mensagem')
    nome_voz = dados.get('nome_voz', 'pt-BR-Standard-A')
    genero = dados.get('genero', 'NEUTRAL').upper()
    
    if mensagem:
        response = chat.send_message(mensagem)
        texto_resposta = response.text
        
        audio_content = sintetizar_fala(texto_resposta, nome_voz, genero)
        
        if audio_content:
            audio_base64 = base64.b64encode(audio_content).decode('utf-8')
            return jsonify({"resposta": texto_resposta, "audio": audio_base64})
        
        return jsonify({"resposta": "Erro ao gerar o áudio."})
    
    return jsonify({"resposta": "Desculpe, não entendi."})

def sintetizar_fala(texto, nome_voz='pt-BR-Standard-A', genero='NEUTRAL'):
    synthesis_input = texttospeech.SynthesisInput(text=texto)
    voice = texttospeech.VoiceSelectionParams(
        language_code="pt-BR",
        name=nome_voz,
        ssml_gender=getattr(texttospeech.SsmlVoiceGender, genero, texttospeech.SsmlVoiceGender.NEUTRAL)
    )
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

    response = tts_client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
    
    return response.audio_content if response else None

if __name__ == '__main__':
    app.run(debug=True)
