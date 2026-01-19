import requests
import os
from datetime import datetime

# --- CONFIGURAÇÕES ---
# Pegamos as senhas dos "Segredos" do GitHub para segurança
PHONE_NUMBER = os.environ.get('PHONE_NUMBER')
API_KEY = os.environ.get('API_KEY')

# Seus números da sorte
NUMEROS_ALVO = ['852', '193']

def enviar_whatsapp(mensagem):
    url = f"https://api.callmebot.com/whatsapp.php?phone={PHONE_NUMBER}&text={mensagem}&apikey={API_KEY}"
    try:
        requests.get(url, timeout=10)
        print("Mensagem enviada com sucesso!")
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")

def verificar_loteria():
    print("Consultando API da Loteria...")
    # Usando uma API pública para pegar o resultado
    try:
        response = requests.get("https://loteriascaixa-api.herokuapp.com/api/federal", timeout=20)
        dados = response.json()
        
        # Pega o primeiro prêmio (ex: "054852")
        primeiro_premio = dados[0]['dezenas'][0] 
        concurso = dados[0]['concurso']
        data_sorteio = dados[0]['data']
        
        # Pega os últimos 3 dígitos
        final_sorteado = primeiro_premio[-3:]
        
        print(f"Concurso: {concurso} | Sorteado: {primeiro_premio} | Final: {final_sorteado}")
        
        if final_sorteado in NUMEROS_ALVO:
            msg = (f"🚨 *BINGO!* 🚨\n\n"
                   f"Na Federal (Conc. {concurso}), deu o número: *{primeiro_premio}*.\n"
                   f"O final *{final_sorteado}* bate com seus números!\n"
                   f"Confira o bilhete!")
            enviar_whatsapp(msg)
        else:
            print(f"O final {final_sorteado} não bateu com {NUMEROS_ALVO}.")
            
    except Exception as e:
        print(f"Erro ao buscar loteria: {e}")

if __name__ == "__main__":
    if not PHONE_NUMBER or not API_KEY:
        print("ERRO: Configure as chaves PHONE_NUMBER e API_KEY nas Settings do GitHub!")
    else:
        verificar_loteria()
