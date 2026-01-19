import requests
import os

# --- CONFIGURAÇÕES ---
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
    try:
        # Busca o resultado
        response = requests.get("https://loteriascaixa-api.herokuapp.com/api/federal", timeout=20)
        dados = response.json()
        
        # Extrai as informações
        primeiro_premio = dados[0]['dezenas'][0] # Ex: "054852"
        concurso = dados[0]['concurso']
        data_sorteio = dados[0]['data']
        
        # Pega os 3 últimos dígitos
        final_sorteado = primeiro_premio[-3:]
        
        print(f"Sorteado: {primeiro_premio} | Final: {final_sorteado}")
        
        # --- LÓGICA DA MENSAGEM ---
        
        if final_sorteado in NUMEROS_ALVO:
            # Mensagem de Vitória
            msg = (f"🚨 *BINGO! DEU BOM!* 🚨\n\n"
                   f"Federal Conc. *{concurso}*\n"
                   f"Número: {primeiro_premio}\n"
                   f"Final: *{final_sorteado}*\n\n"
                   f"Bateu com seus números fixos!")
        else:
            # Mensagem de Acompanhamento (Só informa)
            msg = (f"📢 *Resultado da Federal*\n"
                   f"Conc. {concurso} ({data_sorteio})\n\n"
                   f"Número: {primeiro_premio}\n"
                   f"Final: *{final_sorteado}*\n\n"
                   f"(Não bateu com {NUMEROS_ALVO})")
        
        # Envia a mensagem independente do resultado
        enviar_whatsapp(msg)
            
    except Exception as e:
        print(f"Erro ao buscar loteria: {e}")
        # Opcional: Avisar no zap se der erro na API
        # enviar_whatsapp(f"Erro no robô da loteria: {e}")

if __name__ == "__main__":
    if not PHONE_NUMBER or not API_KEY:
        print("ERRO: Configure as chaves PHONE_NUMBER e API_KEY nas Settings do GitHub!")
    else:
        verificar_loteria()
