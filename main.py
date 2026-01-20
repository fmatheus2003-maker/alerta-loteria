import requests
import os
import urllib.parse
from datetime import datetime, timedelta, timezone

# --- CONFIGURAÇÕES ---
RAW_PHONE = os.environ.get('PHONE_NUMBER')
API_KEY = os.environ.get('API_KEY')
NUMEROS_ALVO = ['852', '193']

# --- FUNÇÕES DE LIMPEZA (MANTIDAS) ---
def limpar_telefone(telefone):
    if not telefone: return ""
    return str(telefone).replace(" ", "").replace("-", "").replace("+", "").replace("(", "").replace(")", "").strip()

def limpar_chave(chave):
    if not chave: return ""
    return str(chave).strip()

PHONE_NUMBER = limpar_telefone(RAW_PHONE)
REAL_KEY = limpar_chave(API_KEY)

# --- O PORTEIRO (NOVA LÓGICA DE DATA) ---
def hoje_e_o_dia_certo():
    # Pega a hora atual em UTC e converte para horário de Brasília (UTC-3)
    # Isso é CRUCIAL pois o servidor do GitHub roda em horário de Londres
    fuso_brasil = timezone(timedelta(hours=-3))
    hoje = datetime.now(fuso_brasil)
    
    dia_atual = hoje.day
    
    # Se por algum milagre o cron rodar dia 21 ou depois, aborta
    if dia_atual >= 21:
        print(f"📅 Hoje é dia {dia_atual}. A regra é rodar ANTES do dia 21. Abortando.")
        return False

    # Descobre o próximo dia de sorteio
    # weekday(): 0=Seg, 1=Ter, 2=Qua ... 5=Sab ... 6=Dom
    dia_semana = hoje.weekday()
    
    dias_para_proximo_sorteio = 0
    
    if dia_semana == 2: # Se hoje é Quarta
        dias_para_proximo_sorteio = 3 # Próximo é Sábado
    elif dia_semana == 5: # Se hoje é Sábado
        dias_para_proximo_sorteio = 4 # Próximo é Quarta
    else:
        print("📅 Hoje não é nem quarta nem sábado. O Cron acordou no dia errado.")
        return False
        
    data_proximo_sorteio = hoje + timedelta(days=dias_para_proximo_sorteio)
    
    # A LÓGICA DE OURO:
    # Se o PRÓXIMO sorteio já cair dia 21 ou depois, então HOJE é o último dia válido.
    # Pode rodar!
    if data_proximo_sorteio.day >= 21:
        print(f"✅ Hoje (dia {dia_atual}) é o último sorteio antes do dia 21. Vamos rodar!")
        print(f"(O próximo sorteio seria dia {data_proximo_sorteio.day}, que já passa do limite)")
        return True
    else:
        print(f"💤 Hoje (dia {dia_atual}) ainda está cedo.")
        print(f"Ainda teremos outro sorteio no dia {data_proximo_sorteio.day} que é antes do dia 21.")
        return False

# --- FUNÇÕES DE ENVIO E BUSCA (MANTIDAS) ---
def enviar_whatsapp(mensagem):
    msg_encoded = urllib.parse.quote(mensagem)
    url = f"https://api.callmebot.com/whatsapp.php?phone={PHONE_NUMBER}&text={msg_encoded}&apikey={REAL_KEY}"
    try:
        requests.get(url, timeout=20)
    except Exception as e:
        print(f"Erro envio: {e}")

def verificar_loteria():
    # PRIMEIRA COISA: Pergunta ao porteiro se pode entrar
    if not hoje_e_o_dia_certo():
        return # Encerra o programa silenciosamente

    print("--- Iniciando Verificação ---")
    try:
        r = requests.get("https://api.guidi.dev.br/loteria/federal/ultimo", verify=False, timeout=15)
        dados = r.json()
        
        numero = dados['dezenas'][0]
        concurso = dados['numero']
        final = numero[-3:]
        
        print(f"Sorteio: {numero} | Final: {final}")
        
        if final in NUMEROS_ALVO:
            msg = f"🚨 BINGO! (Ref Dia 21) Federal {concurso}: {numero}. Final {final} bateu!"
        else:
            msg = f"📢 Federal (Ref Dia 21) {concurso}: {numero}. Final {final}. (Não bateu)"
            
        enviar_whatsapp(msg)
            
    except Exception as e:
        print(f"Erro: {e}")
        enviar_whatsapp(f"Erro no robô mensal: {e}")

if __name__ == "__main__":
    if not PHONE_NUMBER or not REAL_KEY:
        print("❌ Configure as chaves no GitHub!")
    else:
        verificar_loteria()
