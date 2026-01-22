import requests
import os
import urllib.parse
from datetime import datetime, timedelta, timezone

# --- CONFIGURAÇÕES ---
RAW_PHONE = os.environ.get('PHONE_NUMBER')
API_KEY = os.environ.get('API_KEY')

# === ⚙️ PAINEL DE CONTROLE ===
NUMEROS_ALVO = ['852', '193']
DIA_DO_CORTE = 24  # <--- MUDE AQUI O DIA LIMITE (Antes era 21)
# =============================

# --- FUNÇÕES DE LIMPEZA ---
def limpar_telefone(telefone):
    if not telefone: return ""
    return str(telefone).replace(" ", "").replace("-", "").replace("+", "").replace("(", "").replace(")", "").strip()

def limpar_chave(chave):
    if not chave: return ""
    return str(chave).strip()

PHONE_NUMBER = limpar_telefone(RAW_PHONE)
REAL_KEY = limpar_chave(API_KEY)

# --- O PORTEIRO ---
def hoje_e_o_dia_certo():
    fuso_brasil = timezone(timedelta(hours=-3))
    hoje = datetime.now(fuso_brasil)
    dia_atual = hoje.day
    
    # Se hoje já passou do dia de corte, aborta
    if dia_atual >= DIA_DO_CORTE:
        print(f"📅 Hoje é dia {dia_atual}. A regra é rodar ANTES do dia {DIA_DO_CORTE}. Abortando.")
        return False

    # Descobre o próximo sorteio (Quarta ou Sábado)
    dia_semana = hoje.weekday() # 0=Seg ... 6=Dom
    dias_para_proximo = 0
    
    if dia_semana == 2: # Quarta
        dias_para_proximo = 3 # Próximo é Sábado
    elif dia_semana == 5: # Sábado
        dias_para_proximo = 4 # Próximo é Quarta
    else:
        print(f"📅 Hoje ({dia_atual}) não é quarta nem sábado. Cron errado.")
        return False
        
    data_proximo_sorteio = hoje + timedelta(days=dias_para_proximo)
    
    # LÓGICA DINÂMICA:
    # Se o PRÓXIMO sorteio cair no dia do corte ou depois, HOJE é o dia!
    if data_proximo_sorteio.day >= DIA_DO_CORTE:
        print(f"✅ Hoje ({dia_atual}) é o último sorteio antes do dia {DIA_DO_CORTE}. Vamos rodar!")
        print(f"(O próximo seria dia {data_proximo_sorteio.day}, estourando o prazo)")
        return True
    else:
        print(f"💤 Hoje ({dia_atual}) ainda está cedo.")
        print(f"O próximo sorteio ({data_proximo_sorteio.day}) ainda é antes do dia {DIA_DO_CORTE}.")
        return False

# --- FUNÇÕES DE ENVIO E BUSCA ---
def enviar_whatsapp(mensagem):
    msg_encoded = urllib.parse.quote(mensagem)
    url = f"https://api.callmebot.com/whatsapp.php?phone={PHONE_NUMBER}&text={msg_encoded}&apikey={REAL_KEY}"
    try:
        requests.get(url, timeout=20)
    except Exception as e:
        print(f"Erro envio: {e}")

def verificar_loteria():
    # Pergunta ao porteiro
    if not hoje_e_o_dia_certo():
        return

    print("--- Iniciando Verificação ---")
    try:
        r = requests.get("https://api.guidi.dev.br/loteria/federal/ultimo", verify=False, timeout=15)
        dados = r.json()
        
        numero = dados['dezenas'][0]
        concurso = dados['numero']
        final = numero[-3:]
        
        print(f"Sorteio: {numero} | Final: {final}")
        
        if final in NUMEROS_ALVO:
            msg = f"🚨 BINGO! (Ref Dia {DIA_DO_CORTE}) Federal {concurso}: {numero}. Final {final} bateu!"
        else:
            msg = f"📢 Federal (Ref Dia {DIA_DO_CORTE}) {concurso}: {numero}. Final {final}. (Não bateu)"
            
        enviar_whatsapp(msg)
            
    except Exception as e:
        print(f"Erro: {e}")
        enviar_whatsapp(f"Erro no robô mensal: {e}")

if __name__ == "__main__":
    if not PHONE_NUMBER or not REAL_KEY:
        print("❌ Configure as chaves no GitHub!")
    else:
        verificar_loteria()
