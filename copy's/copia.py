import google.generativeai as genai
import speech_recognition as sr
import pyttsx3
import threading

google_api_key = 'AIzaSyA1PwVsVYDTgT65ozZ87A6bq5CGv9aEuLA'
genai.configure(api_key=google_api_key)

generation_config = {
    'candidate_count': 1,
    'temperature': 0.5,
}

model = genai.GenerativeModel(model_name='gemini-1.0-pro',
                              generation_config=generation_config
                              )
chat = model.start_chat(history=[])

motor_de_sintese_de_fala = pyttsx3.init()
voices = motor_de_sintese_de_fala.getProperty('voices')
motor_de_sintese_de_fala.setProperty('voice', voices[0].id)

# Flags globais para controle da conversa e da fala
interromper_conversa = False
interromper_fala_atual = False

def falar_interrompivel(frase):
    """
    Fala a mensagem, permitindo interrupção se um novo prompt for recebido.
    """
    global interromper_fala_atual
    interromper_fala_atual = False  # Reinicia a flag antes de começar a fala
    motor_de_sintese_de_fala.stop()  # Para qualquer fala em andamento
    motor_de_sintese_de_fala.say(frase)
    motor_de_sintese_de_fala.runAndWait()

def remover_caracteres_especiais(texto):
    """
    Remove caracteres especiais de uma string.
    """
    return "".join(c for c in texto if c not in "*!@$%&''-+.*/=+-_")

def reconhecer_fala():
    """
    Captura e reconhece a fala do usuário, retornando o texto reconhecido ou None se não compreendido.
    """
    microfone = sr.Recognizer()
    with sr.Microphone() as source:
        microfone.adjust_for_ambient_noise(source)
        audio = microfone.listen(source)
        try:
            return microfone.recognize_google(audio, language='pt').lower()
        except sr.UnknownValueError:
            falar_interrompivel("Não entendi o que você disse.")
        except sr.RequestError as e:
            falar_interrompivel(f"Ocorreu um erro ao reconhecer a fala: {e}")
    return None

def detectar_comando_interrupcao(comando):
    """
    Verifica se o comando de voz contém palavras-chave para interromper a conversa.
    """
    return comando and ("pare" in comando or "fim" in comando)

def verificar_interrupcao():
    """
    Monitora continuamente a entrada de voz para detectar comandos de interrupção.
    """
    global interromper_conversa
    while not interromper_conversa:
        comando = reconhecer_fala()
        if detectar_comando_interrupcao(comando):
            interromper_conversa = True
            falar_interrompivel("Conversa encerrada a seu pedido.")

def iniciar_conversa():
    """
    Inicia uma conversa contínua com o usuário, monitorando entrada de voz e processando
    respostas até que um comando de interrupção seja detectado.
    """
    global interromper_conversa, interromper_fala_atual
    interromper_conversa = False  # Reinicia a flag antes de começar a conversa

    # Inicia a verificação de interrupção em uma thread separada
    interrupcao_thread = threading.Thread(target=verificar_interrupcao, daemon=True)
    interrupcao_thread.start()
    
    falar_interrompivel("Seja bem-vindo, chefe. Como posso lhe servir?")
    
    # Loop principal da conversa
    while not interromper_conversa:
        prompt = reconhecer_fala()  # Captura o comando de voz do usuário
        
        # Processa a entrada de voz se houver um comando e a conversa não estiver interrompida
        if prompt and not interromper_conversa:
            # Verifica se o comando atual é de interrupção antes de processar a resposta
            if detectar_comando_interrupcao(prompt):
                interromper_conversa = True
                break

            # Interrompe qualquer fala atual e processa o novo comando
            interromper_fala_atual = True
            response = chat.send_message(prompt)
            falar_interrompivel(remover_caracteres_especiais(response.text))

    # Mensagem final de encerramento da conversa
    falar_interrompivel("Conversa encerrada.")

iniciar_conversa()
