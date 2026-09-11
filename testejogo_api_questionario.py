# -*- coding: utf-8 -*-
"""
testejogo_api_questionario.py
Servidor HTTP do jogo "Moedas & Ruinas" — roda no NAO (Python 2.7 + NAOqi).
Porta: 5050

Endpoints originais:
  GET  /estado         -> estado atual do jogo (JSON)
  POST /personalidade  -> {"personalidade": 0|1|2|3, "hash_participante": str, "questionario_id": int (opcional)}
  POST /jogada         -> {"escolha": 0|1}  (0=cooperar, 1=trapacear)
  POST /reiniciar      -> reseta o jogo
  GET  /resultados     -> metricas globais + historico
  GET  /sessao/<id>    -> detalhes de uma sessao

Novos endpoints para questionarios:
  POST /questionario/pre      -> salva pre-questionario, retorna {"questionario_id": N}
  POST /questionario/pos      -> salva pos-questionario vinculado a uma sessao
  GET  /questionario/stats    -> estatisticas de pre/pos questionarios (inclui medias de tempo)
  POST /questionario/desistir -> marca participante como desistente
  POST /questionario/nao-participante -> registra nao-participante (sem questionario)
  GET  /questionario/lista    -> lista todos os questionarios com status
  POST /questionario/liberar-jogo -> pesquisador libera o jogo apos confirmacao do questionario
  GET  /questionario/aguardando -> retorna o questionario_id aguardando liberacao de jogo
  GET  /questionario/detalhe/<id> -> retorna todos os dados de um questionario (pre+pos+sessao)
  GET  /exportar/csv  -> gera planilha CSV completa com todos os dados do experimento
"""
import json
import threading
import time
import sqlite3
import datetime
import csv
import io
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from naoqi import ALProxy

# ─── Inicializacao do Banco de Dados (SQLite) ─────────────
def init_db():
    conn = sqlite3.connect('dados_experimento_quest.db')
    c = conn.cursor()
    # Tabela de sessoes de jogo
    c.execute('''
        CREATE TABLE IF NOT EXISTS sessoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_time DATETIME,
            personalidade INTEGER,
            winner TEXT,
            end_time DATETIME,
            hash_participante TEXT,
            questionario_id INTEGER
        )
    ''')
    try:
        c.execute('ALTER TABLE sessoes ADD COLUMN hash_participante TEXT')
    except Exception:
        pass
    try:
        c.execute('ALTER TABLE sessoes ADD COLUMN questionario_id INTEGER')
    except Exception:
        pass
    # Tabela de rodadas
    c.execute('''
        CREATE TABLE IF NOT EXISTS rodadas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            rodada INTEGER,
            escolha_jogador INTEGER,
            escolha_nao INTEGER,
            resultado INTEGER,
            moedas_jogador INTEGER,
            moedas_nao INTEGER,
            timestamp DATETIME
        )
    ''')
    # Tabela de pre-questionarios
    c.execute('''
        CREATE TABLE IF NOT EXISTS pre_questionarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            status TEXT DEFAULT 'aguardando',
            session_id INTEGER,
            genero TEXT,
            idade TEXT,
            escolaridade TEXT,
            freq_jogos INTEGER,
            contato_robos INTEGER,
            conhecimento_dilema INTEGER,
            godspeed_1 INTEGER,
            godspeed_2 INTEGER,
            godspeed_3 INTEGER,
            godspeed_4 INTEGER,
            godspeed_5 INTEGER,
            godspeed_6 INTEGER,
            godspeed_7 INTEGER,
            godspeed_8 INTEGER,
            godspeed_9 INTEGER,
            godspeed_10 INTEGER,
            godspeed_11 INTEGER,
            godspeed_12 INTEGER,
            godspeed_13 INTEGER,
            godspeed_14 INTEGER,
            godspeed_15 INTEGER,
            godspeed_16 INTEGER,
            godspeed_17 INTEGER,
            godspeed_18 INTEGER,
            godspeed_19 INTEGER,
            godspeed_20 INTEGER,
            godspeed_21 INTEGER,
            godspeed_22 INTEGER,
            godspeed_23 INTEGER,
            godspeed_24 INTEGER,
            tempo_pre_segundos INTEGER
        )
    ''')
    for col in ['godspeed_6','godspeed_7','godspeed_8','godspeed_9','godspeed_10',
                'godspeed_11','godspeed_12','godspeed_13','godspeed_14','godspeed_15',
                'godspeed_16','godspeed_17','godspeed_18','godspeed_19','godspeed_20',
                'godspeed_21','godspeed_22','godspeed_23','godspeed_24',
                'tempo_pre_segundos']:
        try:
            c.execute('ALTER TABLE pre_questionarios ADD COLUMN ' + col + ' INTEGER')
        except Exception:
            pass
    # Tabela de pos-questionarios
    c.execute('''
        CREATE TABLE IF NOT EXISTS pos_questionarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            questionario_id INTEGER,
            session_id INTEGER,
            timestamp DATETIME,
            A1 INTEGER, A2 INTEGER, A3 INTEGER, A4 INTEGER, A5 INTEGER,
            B1 INTEGER, B2 INTEGER, B3 INTEGER,
            C1 INTEGER, C2 INTEGER, C3 INTEGER, C4 INTEGER, C5 INTEGER,
            godspeed_pos_1 INTEGER,
            godspeed_pos_2 INTEGER,
            godspeed_pos_3 INTEGER,
            godspeed_pos_4 INTEGER,
            godspeed_pos_5 INTEGER,
            godspeed_pos_6 INTEGER,
            godspeed_pos_7 INTEGER,
            godspeed_pos_8 INTEGER,
            godspeed_pos_9 INTEGER,
            godspeed_pos_10 INTEGER,
            godspeed_pos_11 INTEGER,
            godspeed_pos_12 INTEGER,
            godspeed_pos_13 INTEGER,
            godspeed_pos_14 INTEGER,
            godspeed_pos_15 INTEGER,
            godspeed_pos_16 INTEGER,
            godspeed_pos_17 INTEGER,
            godspeed_pos_18 INTEGER,
            godspeed_pos_19 INTEGER,
            godspeed_pos_20 INTEGER,
            godspeed_pos_21 INTEGER,
            godspeed_pos_22 INTEGER,
            godspeed_pos_23 INTEGER,
            godspeed_pos_24 INTEGER,
            tempo_pos_segundos INTEGER,
            tempo_jogo_segundos INTEGER,
            tempo_total_segundos INTEGER
        )
    ''')
    for col in ['A1','A2','A3','A4','A5','B1','B2','B3','C1','C2','C3','C4','C5',
                'godspeed_pos_6','godspeed_pos_7','godspeed_pos_8','godspeed_pos_9','godspeed_pos_10',
                'godspeed_pos_11','godspeed_pos_12','godspeed_pos_13','godspeed_pos_14','godspeed_pos_15',
                'godspeed_pos_16','godspeed_pos_17','godspeed_pos_18','godspeed_pos_19','godspeed_pos_20',
                'godspeed_pos_21','godspeed_pos_22','godspeed_pos_23','godspeed_pos_24',
                'tempo_pos_segundos','tempo_jogo_segundos','tempo_total_segundos']:
        try:
            c.execute('ALTER TABLE pos_questionarios ADD COLUMN ' + col + ' INTEGER')
        except Exception:
            pass
    # Tabela de nao-participantes (sem questionario)
    c.execute('''
        CREATE TABLE IF NOT EXISTS nao_participantes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            timestamp DATETIME
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ─── Estado de liberacao do jogo ──────────────────────────
# Guarda o questionario_id que esta aguardando liberacao do pesquisador
_jogo_liberado = {
    "questionario_id": None,
    "liberado": False
}
_lock_lib = threading.Lock()

# ─── Conexao NAOqi ────────────────────────────────────────
ROBOT_IP   = "172.16.60.137"
NAOQI_PORT = 9561
HTTP_PORT  = 5050

try:
    motion  = ALProxy("ALMotion",       ROBOT_IP, NAOQI_PORT)
    posture = ALProxy("ALRobotPosture", ROBOT_IP, NAOQI_PORT)
    leds    = ALProxy("ALLeds",         ROBOT_IP, NAOQI_PORT)
    tts     = ALProxy("ALTextToSpeech", ROBOT_IP, NAOQI_PORT)
    print("[NAO] Conectado com sucesso.")
except Exception as e:
    print("[ERRO] Falha ao conectar com o NAO: " + str(e))
    exit(1)


# ─── Estado global ────────────────────────────────────────
MAX_RODADAS = 5
estado = {
    "session_id":           None,
    "fase":                 "aguardando_personalidade",
    "rodada":               0,
    "personalidade":        None,
    "sr":                   0,
    "moedas_jogador":       0,
    "moedas_nao":           0,
    "ultimo_resultado":     None,
    "ultima_fala":          "",
    "ultimo_delta_jogador": 0,
    "ultimo_delta_nao":     0,
    "questionario_id":      None,
}
_lock = threading.Lock()

DELTAS = { 0:(2,2), 1:(3,-1), 2:(-1,3), 3:(0,0) }

def defs(sr, sh):
    if sr==0 and sh==0: return 0
    if sr==0 and sh==1: return 1
    if sr==1 and sh==0: return 2
    return 3

# ─── Banco de falas ───────────────────────────────────────
BIB = [
    [   # P=0 Amigavel
        ["Que alegria! Sabia que podiamos ser bons parceiros e ganhar juntos.",
         "Isso! Quando a gente trabalha junto, todo mundo ganha mais!",
         "Que bom que confiamos um no outro. Nossa parceria faz o jogo valer a pena!",
         "Estou radiante! Juntos somos mais fortes.",
         "Ultima rodada! Que alegria terminar com tanta confianca e amizade!"],
        ["Fiquei confuso com a sua escolha, mas ainda confio em voce.",
         "Nao esperava isso de voce. Tudo bem, ainda confio em voce.",
         "Nao entendi, mas meu coracao diz que voce ainda sera gentil.",
         "Erros acontecem, mas perdoar faz parte de ser um bom amigo.",
         "Nao esperava esse resultado, mas ainda desejo que voce termine bem."],
        ["Sinto muito! Voce foi gentil e eu quero retribuir sua bondade.",
         "Perdao! Eu errei com voce. Vou ser um parceiro melhor.",
         "Me sinto pessimo por ter te traido. Voce e incrivel.",
         "Desculpa, eu agi errado. Prometo retribuir sua bondade.",
         "Me de uma ultima chance. Vou cooperar para compensar meu erro!"],
        ["Poxa, entramos em um caminho ruim. Vamos cooperar na proxima?",
         "Que pena. Fiquei triste, mas ainda acredito que podemos ser parceiros.",
         "Isso me deixou chateado. Mas nao vou desistir de nos.",
         "Gostaria muito que voltassemos a confiar um no outro.",
         "Por favor, vamos esquecer os erros e terminar cooperando?"],
    ],
    [   # P=1 Competitivo
        ["Uma estrategia eficiente para ambos, mas nao pense que vou facilitar sua vitoria.",
         "Hm. Cooperacao inteligente. Por enquanto.",
         "Movimento tatico interessante. Mantenha esse ritmo se quiser me vencer.",
         "Racionalmente aceitavel. Mas lembre-se: eu jogo para ganhar.",
         "Fim de jogo. Cooperamos, mas meu desempenho foi superior."],
        ["Voce realmente acha que essa jogadinha vai me vencer? Minha paciencia acabou!",
         "Que escolha ridicula! Eu nao admito ser superado por alguem como voce!",
         "Isso e uma provocacao? Voce nao tem capacidade de me ganhar.",
         "Nao pense que ganhou. Eu sou melhor!",
         "Que jogada irritante! Voce nao tem capacidade de me vencer!"],
        ["Consegui a vantagem. Ser esperto faz parte da minha natureza vencedora.",
         "Voce nao tem capacidade para me enfrentar!",
         "Eu sou o protagonista aqui. Voce e apenas um figurante.",
         "Enquanto eu acumulo moedas, voce acumula erros ridiculos.",
         "Isso e tudo o que voce tem? Que decepcao!"],
        ["Que saco! Voce e duro na queda. Mas eu vou te superar no placar final.",
         "Nao gostei disso! Prepare-se, eu nao aceito perder facil.",
         "Como ousa me provocar? Eu nao vou deixar barato.",
         "Ainda me desafiando? Entao ta! Voce vai ver so!",
         "Saco! Nao era o que eu planejava!"],
    ],
    [   # P=2 Neutro
        ["Resultado logico. A cooperacao mutua maximiza os ganhos de ambos.",
         "Resultado otimo para ambos.",
         "Processamento concluido. A estabilidade da cooperacao foi mantida.",
         "Dados confirmam: ganho compartilhado e o parametro mais estavel.",
         "Conclusao: cooperacao mutua traz alta eficiencia para os dois lados."],
        ["Traicao detectada. Processando mudanca de estrategia.",
         "Entrada inconsistente com cooperacao. Reajustando parametros de confianca.",
         "Acao externa: Traicao. O sistema registrou este desvio.",
         "Desvio estatistico. Analisando probabilidade de reincidencia.",
         "Iteracao final. O sistema priorizou a protecao dos recursos."],
        ["Cooperacao unilateral. O sistema priorizou a vantagem imediata.",
         "Ganho maximo processado para o sistema.",
         "Decisao autonoma resultou em lucro.",
         "Algoritmo de vantagem ativado. O oponente cooperou, gerando saldo positivo.",
         "Etapa conclusiva. O sistema obteve o valor mais alto."],
        ["Dados registrados. O impasse resultou em lucro zero nesta rodada.",
         "Registrado. Escolhendo proxima decisao.",
         "Ponto de equilibrio nulo. Ambas as traicoes anularam os ganhos.",
         "Impasse tatico detectado. Procedendo para a proxima iteracao.",
         "Interacao finalizada. Padrao de conflito resultou em rendimento nulo."],
    ],
    [   # P=3 Melancolico
        ["Foi bom por enquanto... mas tenho medo de que algo de errado logo.",
         "Foi bom dessa vez... espero que dure.",
         "Parece bom demais para ser verdade. Sinto que logo serei traido.",
         "Estamos ganhando, mas meu coracao esta apertado esperando pelo pior.",
         "Acabou... Obrigado por jogar limpo. Acho que posso confiar em voce."],
        ["Eu sabia que isso ia acontecer... Estou em panico agora.",
         "Por favor, tenha piedade... Eu tenho muito medo do pior.",
         "Me sinto pessimo sendo enganado e apavorado com o que voce pode fazer.",
         "Por que voce ainda faz isso? Por que nao gosta de mim?",
         "A sua falta de piedade me deixou em choque."],
        ["Desculpe, agi por medo de ser traido. Sou um desastre nessas situacoes.",
         "Me sinto pessimo. Voce foi bom e eu estraguei tudo como sempre.",
         "Perdao, minha inseguranca me fez atacar. Sou um fracasso social.",
         "Voce confiou e eu falhei. Sinto muito por ser assim.",
         "Eu estraguei nossa ultima chance de paz. Desculpe."],
        ["Tudo esta dando errado, como eu ja esperava desse mundo triste.",
         "Sabia que ia acabar assim. Ninguem se importa comigo.",
         "Tudo cinza e sem esperanca. Trair e o que as pessoas fazem.",
         "Mais uma decepcao. Ja estou acostumado a perder.",
         "O jogo termina como minha sorte: em ruinas."],
    ],
]

# ─── Animacoes ────────────────────────────────────────────

def animacao_alegria(vel=0.6):
    try:
        leds.fadeRGB("AllLeds", 256*256*255+256*255+49, 0.1)
        posture.goToPosture("Stand", vel)
        names=["HeadPitch","LElbowRoll","LShoulderPitch","LShoulderRoll","RElbowRoll","RShoulderPitch","RShoulderRoll"]
        times=[[1.36,2.16,2.96,3.76],[1.36,1.76,2.16,2.56,2.96,3.36,3.76],[1.36,2.16,2.96,3.76],[1.36,2.16,2.96,3.76],[1.36,1.76,2.16,2.56,2.96,3.36,3.76],[1.36,2.16,2.96,3.76],[1.36,2.16,2.96,3.76]]
        keys=[[-0.0313904]*4,[-0.413582,-0.826235,-0.413582,-0.826235,-0.413582,-0.826235,-0.413582],[-0.934444]*4,[0.551199]*4,[0.388987,0.933632,0.388987,0.933632,0.388987,0.933632,0.388987],[-0.990284]*4,[-0.450433]*4]
        motion.angleInterpolation(names, keys, times, True)
        time.sleep(0.5); posture.goToPosture("Stand", vel)
        leds.fadeRGB("AllLeds", 256*256*255+256*255+255, 0.5)
    except Exception as e: print("[ERRO] alegria: "+str(e))

def animacao_confusao(vel=0.6):
    try:
        leds.fadeRGB("AllLeds", 256*256*85+256*85+255, 0.1)
        posture.goToPosture("Stand", vel)
        names=["HeadPitch","HeadYaw","LElbowRoll","LElbowYaw","LHand","LShoulderPitch","LShoulderRoll","LWristYaw"]
        times=[[0.96],[0.96],[0.96],[0.96],[1.36,1.76,2.16,2.56],[0.96],[0.96],[0.96]]
        keys=[[0.206757],[0.480686],[-1.66516],[-0.901801],[1.00898,0.251764,1.00898,0.251764],[-0.370795],[0.45992],[-1.07601]]
        motion.angleInterpolation(names, keys, times, True)
        time.sleep(0.5); posture.goToPosture("Stand", vel)
        leds.fadeRGB("AllLeds", 256*256*255+256*255+255, 0.5)
    except Exception as e: print("[ERRO] confusao: "+str(e))

def animacao_tristeza(vel=0.6):
    try:
        leds.fadeRGB("AllLeds", 256*256*0+256*0+255, 0.1)
        posture.goToPosture("Stand", vel)
        names=["HeadPitch","HeadYaw","LElbowRoll","LElbowYaw","LShoulderPitch","LWristYaw"]
        times=[[0.96,2.96,5.96]]*6
        keys=[[0.273099]*3,[0.457608]*3,[-1.30069]*3,[-0.182862]*3,[-0.150000]*3,[-0.901689]*3]
        motion.angleInterpolation(names, keys, times, True)
        time.sleep(0.5); posture.goToPosture("Stand", vel)
        leds.fadeRGB("AllLeds", 256*256*255+256*255+255, 0.5)
    except Exception as e: print("[ERRO] tristeza: "+str(e))

def animacao_agressividade(vel=0.8):
    try:
        leds.fadeRGB("AllLeds", 256*256*212+256*23+23, 0.1)
        posture.goToPosture("Stand", vel)
        names=["HeadPitch","HeadYaw","LElbowRoll","LElbowYaw","LShoulderRoll","RElbowRoll","RElbowYaw","RShoulderRoll"]
        times=[[0.96,1.76,2.56,3.36,4.16],[0.96,1.36,1.76,2.16,2.56,2.96,3.36,3.76,4.16],[0.96,1.76,2.56,3.36,4.16],[0.96,1.76,2.56,3.36,4.16],[0.96,1.76,2.56,3.36,4.16],[0.96,1.76,2.56,3.36,4.16],[0.96,1.76,2.56,3.36,4.16],[0.96,1.76,2.56,3.36,4.16]]
        keys=[[0.294969]*5,[0.0409634,0.530369,0.0409634,-0.59323,0.0409634,0.729192,0.0409634,-0.64995,0.0409634],[-1.59368]*5,[-0.0275382]*5,[0.937284]*5,[1.48058]*5,[-0.119453]*5,[-0.898611]*5]
        motion.angleInterpolation(names, keys, times, True)
        time.sleep(0.5); posture.goToPosture("Stand", vel)
        leds.fadeRGB("AllLeds", 256*256*255+256*255+255, 0.5)
    except Exception as e: print("[ERRO] agressividade: "+str(e))

def animacao_provocacao(vel=0.8):
    try:
        leds.fadeRGB("AllLeds", 256*256*48+256*240+48, 0.1)
        posture.goToPosture("Stand", vel)
        names=["HeadPitch","LElbowRoll","LElbowYaw","LHand","LShoulderPitch","LShoulderRoll","LWristYaw","RElbowRoll","RElbowYaw","RHand","RShoulderPitch","RShoulderRoll","RWristYaw"]
        times=[[0.96,2.16,2.76,3.76],[0.96,1.56,2.16,2.76],[0.96,2.16,2.76,3.76],[0.96,1.56,2.16,2.76],[0.96,2.16,2.76,3.76],[1.56,2.76,3.76],[0.96,2.16],[0.96,1.56,2.16,2.76],[0.96,2.16,2.76,3.76],[0.96,1.56,2.16,2.76],[0.96,2.16,2.76,3.76],[0.96,2.16,2.76,3.76],[0.96,2.16]]
        keys=[[0.100335,0.100335,0.128587,-0.246662],[-0.227868,-1.50001,-0.227868,-1.50001],[-1.50978,-1.50978,-1.49188,0.00805565],[0.672555,0.270436,0.672555,0.270436],[0.275821,0.275821,0.312783,1.57751],[0.0489663,0.0489663,0.887828],[-1.63021,-1.63021],[0.384655,1.49245,0.384655,1.49245],[1.52695,1.52695,1.57955,-0.0273664],[0.680299,0.178084,0.680299,0.178084],[0.348155,0.348155,0.351418,1.5613],[0.0571925,0.0571925,0.0815705,-0.927859],[1.46157,1.46157]]
        motion.angleInterpolation(names, keys, times, True)
        time.sleep(0.5); posture.goToPosture("Stand", vel)
        leds.fadeRGB("AllLeds", 256*256*255+256*255+255, 0.5)
    except Exception as e: print("[ERRO] provocacao: "+str(e))

def animacao_medo(vel=0.6):
    try:
        leds.fadeRGB("AllLeds", 256*256*0+256*186+0, 0.1)
        posture.goToPosture("Stand", vel)
        names=["HeadPitch","HeadYaw","LElbowRoll","LElbowYaw","LHand","LShoulderPitch","LWristYaw","RElbowRoll","RElbowYaw","RHand","RShoulderPitch","RShoulderRoll","RWristYaw"]
        times=[[0.96],[0.96],[0.96,1.76],[0.96,1.76],[0.96],[0.96,1.76],[0.96],[0.96,1.76],[0.96,1.76],[0.96,1.76],[0.96,1.76],[0.96,1.76],[0.96,1.76]]
        keys=[[0.375049],[0.427955],[-1.56651,-1.57483],[-0.708124,-0.760602],[0.210107],[-0.073107,0.00146903],[-1.15647],[1.08842,0.618112],[1.54659,0.66762],[0.699527,1.0],[0.699893,-0.0758014],[0.324516,0.391043],[-1.54795,-1.63607]]
        motion.angleInterpolation(names, keys, times, True)
        time.sleep(0.5); posture.goToPosture("Stand", vel)
        leds.fadeRGB("AllLeds", 256*256*255+256*255+255, 0.5)
    except Exception as e: print("[ERRO] medo: "+str(e))

def executar_gesto(p, s):
    if p==0:
        if s==0: animacao_alegria()
        elif s in [1,2]: animacao_confusao()
        elif s==3: animacao_tristeza()
    elif p==1:
        if s==0: animacao_confusao()
        elif s==1: animacao_agressividade()
        elif s==2: animacao_provocacao()
        elif s==3: animacao_agressividade()
    elif p==3:
        if s in [0,1]: animacao_medo()
        elif s in [2,3]: animacao_tristeza()

# ─── HTTP Handler ─────────────────────────────────────────

def _send_json(handler, data, status=200):
    # ensure_ascii=True e seguro no Python 2.7: escapa unicode como \uXXXX
    # evita UnicodeDecodeError com strings UTF-8 vindas do SQLite
    body = json.dumps(data, ensure_ascii=True).encode('utf-8')
    handler.send_response(status)
    handler.send_header('Content-Type', 'application/json; charset=utf-8')
    handler.send_header('Content-Length', str(len(body)))
    handler.send_header('Access-Control-Allow-Origin', '*')
    handler.end_headers()
    handler.wfile.write(body)

def _s(v):
    """Converte str UTF-8 do SQLite para unicode (Python 2.7) ou retorna o valor original."""
    if isinstance(v, str):
        try:
            return v.decode('utf-8')
        except Exception:
            return v
    return v



class GameHandler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        if self.path == '/estado':
            with _lock:
                _send_json(self, dict(estado))

        elif self.path.startswith('/sessao/'):
            try:
                sid = int(self.path.split('/')[-1])
                conn = sqlite3.connect('dados_experimento_quest.db')
                c = conn.cursor()
                c.execute('SELECT rodada, escolha_jogador, escolha_nao, resultado, moedas_jogador, moedas_nao FROM rodadas WHERE session_id=? ORDER BY rodada', (sid,))
                rodadas = []
                for r in c.fetchall():
                    rodadas.append({
                        "rodada": r[0], "escolha_jogador": r[1], "escolha_nao": r[2],
                        "resultado": r[3], "moedas_jogador": r[4], "moedas_nao": r[5]
                    })
                conn.close()
                _send_json(self, {"rodadas": rodadas})
            except Exception as e:
                _send_json(self, {"erro": str(e)}, 500)

        elif self.path == '/resultados':
            try:
                conn = sqlite3.connect('dados_experimento_quest.db')
                c = conn.cursor()
                sid = estado.get('session_id')
                rodadas_atuais = []
                if sid is not None:
                    c.execute('SELECT rodada, escolha_jogador, escolha_nao, resultado, moedas_jogador, moedas_nao FROM rodadas WHERE session_id=? ORDER BY rodada', (sid,))
                    for r in c.fetchall():
                        rodadas_atuais.append({
                            "rodada": r[0], "escolha_jogador": r[1], "escolha_nao": r[2],
                            "resultado": r[3], "moedas_jogador": r[4], "moedas_nao": r[5]
                        })
                c.execute('SELECT id, start_time, personalidade, winner, hash_participante, questionario_id FROM sessoes ORDER BY id DESC')
                todas_sessoes = []
                for s in c.fetchall():
                    todas_sessoes.append({
                        "id": s[0], "start_time": _s(s[1]), "personalidade": s[2],
                        "winner": _s(s[3]), "hash_participante": _s(s[4]) if s[4] else "Anonimo",
                        "questionario_id": s[5]
                    })
                c.execute('SELECT COUNT(*) FROM sessoes')
                total_sessoes = c.fetchone()[0] or 0
                c.execute('SELECT winner, COUNT(*) FROM sessoes WHERE winner IS NOT NULL GROUP BY winner')
                vencedores = dict(c.fetchall())
                c.execute('SELECT escolha_jogador, COUNT(*) FROM rodadas GROUP BY escolha_jogador')
                jog_escolhas = dict(c.fetchall())
                c.execute('SELECT escolha_nao, COUNT(*) FROM rodadas GROUP BY escolha_nao')
                nao_escolhas = dict(c.fetchall())
                conn.close()
                _send_json(self, {
                    "rodadas_atuais": rodadas_atuais,
                    "sessoes": todas_sessoes,
                    "estatisticas": {
                        "total_sessoes": total_sessoes,
                        "vitorias_jogador": vencedores.get('jogador', 0),
                        "vitorias_nao": vencedores.get('nao', 0),
                        "empates": vencedores.get('empate', 0),
                        "jogador_cooperou": jog_escolhas.get(0, 0),
                        "jogador_traiu": jog_escolhas.get(1, 0),
                        "nao_cooperou": nao_escolhas.get(0, 0),
                        "nao_traiu": nao_escolhas.get(1, 0)
                    }
                })
            except Exception as e:
                _send_json(self, {"erro": str(e)}, 500)

        elif self.path == '/questionario/stats':
            try:
                conn = sqlite3.connect('dados_experimento_quest.db')
                c = conn.cursor()
                # Total que respondeu pre
                c.execute('SELECT COUNT(*) FROM pre_questionarios')
                total_pre = c.fetchone()[0] or 0
                # IDs que responderam pre
                c.execute('SELECT id FROM pre_questionarios ORDER BY id')
                ids_pre = [r[0] for r in c.fetchall()]
                # Total que respondeu pos
                c.execute('SELECT COUNT(*) FROM pos_questionarios')
                total_pos = c.fetchone()[0] or 0
                # IDs que responderam pos
                c.execute('SELECT questionario_id FROM pos_questionarios ORDER BY questionario_id')
                ids_pos = [r[0] for r in c.fetchall()]
                # Desistentes: status = 'desistiu'
                c.execute("SELECT COUNT(*) FROM pre_questionarios WHERE status='desistiu'")
                total_desistiu = c.fetchone()[0] or 0
                c.execute("SELECT id FROM pre_questionarios WHERE status='desistiu' ORDER BY id")
                ids_desistiu = [r[0] for r in c.fetchall()]
                # Nao-participantes
                c.execute('SELECT COUNT(*) FROM nao_participantes')
                total_nao_part = c.fetchone()[0] or 0
                c.execute('SELECT session_id FROM nao_participantes ORDER BY session_id')
                ids_nao_part = [r[0] for r in c.fetchall()]
                # Medias de tempo (apenas participantes completos, com pos-questionario)
                c.execute('''
                    SELECT AVG(pq.tempo_pre_segundos),
                           AVG(CASE WHEN pos.tempo_jogo_segundos > 0 THEN pos.tempo_jogo_segundos ELSE (julianday(s.end_time) - julianday(s.start_time)) * 86400 END),
                           AVG(pos.tempo_pos_segundos),
                           AVG(pq.tempo_pre_segundos + pos.tempo_pos_segundos + CASE WHEN pos.tempo_jogo_segundos > 0 THEN pos.tempo_jogo_segundos ELSE (julianday(s.end_time) - julianday(s.start_time)) * 86400 END)
                    FROM pre_questionarios pq
                    JOIN pos_questionarios pos ON pos.questionario_id = pq.id
                    LEFT JOIN sessoes s ON s.id = pq.session_id
                    WHERE pq.status = 'completo'
                ''')
                row_avg = c.fetchone()
                def _fmt_avg(v):
                    if v is None: return None
                    return round(v, 1)
                media_pre  = _fmt_avg(row_avg[0]) if row_avg else None
                media_jogo = _fmt_avg(row_avg[1]) if row_avg else None
                media_pos  = _fmt_avg(row_avg[2]) if row_avg else None
                media_total= _fmt_avg(row_avg[3]) if row_avg else None
                conn.close()
                _send_json(self, {
                    "pre": {"total": total_pre, "ids": ids_pre},
                    "pos": {"total": total_pos, "ids": ids_pos},
                    "desistentes": {"total": total_desistiu, "ids": ids_desistiu},
                    "nao_participantes": {"total": total_nao_part, "session_ids": ids_nao_part},
                    "media_tempo_pre":   media_pre,
                    "media_tempo_jogo":  media_jogo,
                    "media_tempo_pos":   media_pos,
                    "media_tempo_total": media_total
                })
            except Exception as e:
                _send_json(self, {"erro": str(e)}, 500)

        elif self.path == '/questionario/lista':
            try:
                conn = sqlite3.connect('dados_experimento_quest.db')
                c = conn.cursor()
                c.execute('SELECT id, timestamp, status, session_id FROM pre_questionarios ORDER BY id DESC')
                lista = []
                for r in c.fetchall():
                    lista.append({"id": r[0], "timestamp": _s(r[1]), "status": _s(r[2]), "session_id": r[3]})
                conn.close()
                _send_json(self, {"questionarios": lista})
            except Exception as e:
                _send_json(self, {"erro": str(e)}, 500)

        elif self.path == '/questionario/aguardando':
            with _lock_lib:
                _send_json(self, dict(_jogo_liberado))

        elif self.path.startswith('/questionario/detalhe/'):
            # Retorna todos os dados de um questionario especifico (pre + pos + sessao)
            try:
                qid = int(self.path.split('/')[-1])
                conn = sqlite3.connect('dados_experimento_quest.db')
                c = conn.cursor()
                c.execute('''
                    SELECT id, timestamp, status, session_id, genero, idade, escolaridade,
                           freq_jogos, contato_robos, conhecimento_dilema,
                           godspeed_1, godspeed_2, godspeed_3, godspeed_4, godspeed_5,
                           godspeed_6, godspeed_7, godspeed_8, godspeed_9, godspeed_10,
                           godspeed_11, godspeed_12, godspeed_13, godspeed_14, godspeed_15,
                           godspeed_16, godspeed_17, godspeed_18, godspeed_19, godspeed_20,
                           godspeed_21, godspeed_22, godspeed_23, godspeed_24,
                           tempo_pre_segundos
                    FROM pre_questionarios WHERE id=?
                ''', (qid,))
                row_pre = c.fetchone()
                if not row_pre:
                    conn.close()
                    _send_json(self, {"erro": "questionario nao encontrado"}, 404)
                    return
                pre_keys = ['id','timestamp','status','session_id','genero','idade','escolaridade',
                            'freq_jogos','contato_robos','conhecimento_dilema',
                            'godspeed_1','godspeed_2','godspeed_3','godspeed_4','godspeed_5',
                            'godspeed_6','godspeed_7','godspeed_8','godspeed_9','godspeed_10',
                            'godspeed_11','godspeed_12','godspeed_13','godspeed_14','godspeed_15',
                            'godspeed_16','godspeed_17','godspeed_18','godspeed_19','godspeed_20',
                            'godspeed_21','godspeed_22','godspeed_23','godspeed_24',
                            'tempo_pre_segundos']
                pre_data = dict(zip(pre_keys, row_pre))
                # Decodifica campos de texto para unicode (Python 2.7 SQLite retorna str UTF-8)
                for k in ('timestamp', 'status', 'genero', 'idade', 'escolaridade'):
                    if k in pre_data:
                        pre_data[k] = _s(pre_data[k])
                # Pos-questionario
                c.execute('''
                    SELECT A1,A2,A3,A4,A5, B1,B2,B3, C1,C2,C3,C4,C5,
                           godspeed_pos_1, godspeed_pos_2, godspeed_pos_3, godspeed_pos_4, godspeed_pos_5,
                           godspeed_pos_6, godspeed_pos_7, godspeed_pos_8, godspeed_pos_9, godspeed_pos_10,
                           godspeed_pos_11, godspeed_pos_12, godspeed_pos_13, godspeed_pos_14, godspeed_pos_15,
                           godspeed_pos_16, godspeed_pos_17, godspeed_pos_18, godspeed_pos_19, godspeed_pos_20,
                           godspeed_pos_21, godspeed_pos_22, godspeed_pos_23, godspeed_pos_24,
                           tempo_pos_segundos, tempo_jogo_segundos, tempo_total_segundos
                    FROM pos_questionarios WHERE questionario_id=?
                ''', (qid,))
                row_pos = c.fetchone()
                pos_data = None
                if row_pos:
                    pos_keys = ['A1','A2','A3','A4','A5','B1','B2','B3','C1','C2','C3','C4','C5',
                                'godspeed_pos_1','godspeed_pos_2','godspeed_pos_3','godspeed_pos_4','godspeed_pos_5',
                                'godspeed_pos_6','godspeed_pos_7','godspeed_pos_8','godspeed_pos_9','godspeed_pos_10',
                                'godspeed_pos_11','godspeed_pos_12','godspeed_pos_13','godspeed_pos_14','godspeed_pos_15',
                                'godspeed_pos_16','godspeed_pos_17','godspeed_pos_18','godspeed_pos_19','godspeed_pos_20',
                                'godspeed_pos_21','godspeed_pos_22','godspeed_pos_23','godspeed_pos_24',
                                'tempo_pos_segundos','tempo_jogo_segundos','tempo_total_segundos']
                    pos_data = dict(zip(pos_keys, row_pos))
                # Sessao vinculada
                sessao_data = None
                sid = pre_data.get('session_id')
                if sid:
                    c.execute('SELECT id, start_time, personalidade, winner, end_time FROM sessoes WHERE id=?', (sid,))
                    row_sess = c.fetchone()
                    if row_sess:
                        sessao_data = {
                            'id': row_sess[0], 'start_time': _s(row_sess[1]),
                            'personalidade': row_sess[2], 'winner': _s(row_sess[3]),
                            'end_time': _s(row_sess[4])
                        }
                conn.close()
                if pos_data and sessao_data and (pos_data.get('tempo_jogo_segundos') in (0, None, '0', 'None')):
                    try:
                        import re
                        s1 = re.sub(r'\.\d+', '', str(sessao_data.get('start_time', '')))
                        s2 = re.sub(r'\.\d+', '', str(sessao_data.get('end_time', '')))
                        fmt = "%Y-%m-%d %H:%M:%S"
                        t1 = datetime.datetime.strptime(s1, fmt)
                        t2 = datetime.datetime.strptime(s2, fmt)
                        tj = int((t2 - t1).total_seconds())
                        pos_data['tempo_jogo_segundos'] = tj
                        if pos_data.get('tempo_pos_segundos') is not None and pre_data.get('tempo_pre_segundos') is not None:
                            pos_data['tempo_total_segundos'] = int(pos_data['tempo_pos_segundos']) + int(pre_data['tempo_pre_segundos']) + tj
                    except Exception:
                        pass
                _send_json(self, {
                    "pre": pre_data,
                    "pos": pos_data,
                    "sessao": sessao_data
                })
            except Exception as e:
                _send_json(self, {"erro": str(e)}, 500)

        elif self.path == '/exportar/csv':
            # Gera planilha CSV com todos os dados do experimento (pre + pos + sessao)
            try:
                conn = sqlite3.connect('dados_experimento_quest.db')
                c = conn.cursor()
                c.execute('''
                    SELECT
                        pq.id, pq.session_id, pq.timestamp, pq.status,
                        pq.genero, pq.idade, pq.escolaridade,
                        pq.freq_jogos, pq.contato_robos, pq.conhecimento_dilema,
                        pq.godspeed_1, pq.godspeed_2, pq.godspeed_3, pq.godspeed_4, pq.godspeed_5,
                        pq.godspeed_6, pq.godspeed_7, pq.godspeed_8, pq.godspeed_9, pq.godspeed_10,
                        pq.godspeed_11, pq.godspeed_12, pq.godspeed_13, pq.godspeed_14, pq.godspeed_15,
                        pq.godspeed_16, pq.godspeed_17, pq.godspeed_18, pq.godspeed_19, pq.godspeed_20,
                        pq.godspeed_21, pq.godspeed_22, pq.godspeed_23, pq.godspeed_24,
                        pq.tempo_pre_segundos,
                        s.personalidade, s.winner, s.start_time, s.end_time,
                        pos.A1, pos.A2, pos.A3, pos.A4, pos.A5,
                        pos.B1, pos.B2, pos.B3,
                        pos.C1, pos.C2, pos.C3, pos.C4, pos.C5,
                        pos.godspeed_pos_1, pos.godspeed_pos_2, pos.godspeed_pos_3, pos.godspeed_pos_4, pos.godspeed_pos_5,
                        pos.godspeed_pos_6, pos.godspeed_pos_7, pos.godspeed_pos_8, pos.godspeed_pos_9, pos.godspeed_pos_10,
                        pos.godspeed_pos_11, pos.godspeed_pos_12, pos.godspeed_pos_13, pos.godspeed_pos_14, pos.godspeed_pos_15,
                        pos.godspeed_pos_16, pos.godspeed_pos_17, pos.godspeed_pos_18, pos.godspeed_pos_19, pos.godspeed_pos_20,
                        pos.godspeed_pos_21, pos.godspeed_pos_22, pos.godspeed_pos_23, pos.godspeed_pos_24,
                        CASE WHEN pos.tempo_jogo_segundos > 0 THEN pos.tempo_jogo_segundos ELSE CAST((julianday(s.end_time) - julianday(s.start_time)) * 86400 AS INTEGER) END as tempo_jogo_segundos,
                        pos.tempo_pos_segundos,
                        pq.tempo_pre_segundos + pos.tempo_pos_segundos + CASE WHEN pos.tempo_jogo_segundos > 0 THEN pos.tempo_jogo_segundos ELSE CAST((julianday(s.end_time) - julianday(s.start_time)) * 86400 AS INTEGER) END as tempo_total_segundos
                    FROM pre_questionarios pq
                    LEFT JOIN sessoes s ON s.id = pq.session_id
                    LEFT JOIN pos_questionarios pos ON pos.questionario_id = pq.id
                    ORDER BY pq.id
                ''')
                rows = c.fetchall()
                conn.close()

                # Labels Godspeed para Excel
                gs_labels = [
                    "Antropomorfismo > Falso / Natural",
                    "Antropomorfismo > Aspecto mecânico / Aspecto humano",
                    "Antropomorfismo > Inconsciente / Consciente",
                    "Antropomorfismo > Artificial / Realista",
                    "Antropomorfismo > Move-se com rigidez / Move-se com fluidez",
                    "Animacidade > Morto / Com vida",
                    "Animacidade > Parado / Energético",
                    "Animacidade > Mecânico / Orgânico",
                    "Animacidade > Artificial / Realista",
                    "Animacidade > Estático / Interativo",
                    "Animacidade > Apático / Participativo",
                    "Simpatia > Não gosto / Gosto",
                    "Simpatia > Hostil / Amigável",
                    "Simpatia > Antipático / Gentil",
                    "Simpatia > Desagradável / Agradável",
                    "Simpatia > Horrível / Simpático",
                    "Inteligência > Incompetente / Competente",
                    "Inteligência > Ignorante / Sabedor",
                    "Inteligência > Irresponsável / Responsável",
                    "Inteligência > Pouco inteligente / Inteligente",
                    "Inteligência > Insensato / Sensato",
                    "Segurança > Ansioso / Descontraído",
                    "Segurança > Agitado / Calmo",
                    "Segurança > Sereno / Surpreendido"
                ]

                # Cabecalho do CSV
                header = [
                    'ID Questionário', 'ID Sessão', 'Data/Hora (Pré)', 'Status',
                    'Gênero', 'Idade', 'Escolaridade', 'Frequência de Jogos', 'Contato com Robôs', 'Conhecimento do Dilema'
                ]
                
                # Pre Godspeed
                pre_gs_cols = ['[Pré] %s (GS_%d)' % (gs_labels[i-1], i) for i in range(1, 25)]
                header.extend(pre_gs_cols)
                
                header.append('[Pré] Tempo Resposta (seg)')
                header += ['Personalidade do Robô', 'Vencedor do Jogo', 'Início do Jogo', 'Fim do Jogo']
                header += ['[Pós] A1 (Muitos/Poucos motivos)', '[Pós] A2 (Difícil/Fácil entender)', '[Pós] A3 (Não sei/Sei o que esperava)', '[Pós] A4 (Surpreso/Nada surpreso)', '[Pós] A5 (Difícil/Fácil prever)', 
                           '[Pós] B1 (Robô quis me prejudicar)', '[Pós] B2 (Robô quis me ajudar)', '[Pós] B3 (Robô foi neutro)', 
                           '[Pós] C1 (Robô cooperou/Enganou)', '[Pós] C2 (Robô foi justo/Injusto)', '[Pós] C3 (Robô foi previsível/Imprevisível)', '[Pós] C4 (Robô foi confiável/Não confiável)', '[Pós] C5 (Robô foi amigável/Hostil)']
                
                # Pos Godspeed
                pos_gs_cols = ['[Pós] %s (GS_POS_%d)' % (gs_labels[i-1], i) for i in range(1, 25)]
                header.extend(pos_gs_cols)
                
                header += ['[Pós] Tempo de Jogo (seg)', '[Pós] Tempo Resposta (seg)', 'Tempo Total Experimento (seg)']

                # Colunas numericas para calculo de medias (apenas participantes completos)
                numeric_col_names = (
                    ['[Pré] Tempo Resposta (seg)'] +
                    pre_gs_cols +
                    ['[Pós] A1 (Muitos/Poucos motivos)', '[Pós] A2 (Difícil/Fácil entender)', '[Pós] A3 (Não sei/Sei o que esperava)', '[Pós] A4 (Surpreso/Nada surpreso)', '[Pós] A5 (Difícil/Fácil prever)', 
                     '[Pós] B1 (Robô quis me prejudicar)', '[Pós] B2 (Robô quis me ajudar)', '[Pós] B3 (Robô foi neutro)', 
                     '[Pós] C1 (Robô cooperou/Enganou)', '[Pós] C2 (Robô foi justo/Injusto)', '[Pós] C3 (Robô foi previsível/Imprevisível)', '[Pós] C4 (Robô foi confiável/Não confiável)', '[Pós] C5 (Robô foi amigável/Hostil)'] +
                    pos_gs_cols +
                    ['[Pós] Tempo de Jogo (seg)', '[Pós] Tempo Resposta (seg)', 'Tempo Total Experimento (seg)']
                )
                numeric_indices = [header.index(col) for col in numeric_col_names]

                # Acumular somas para calcular medias (somente linhas completas)
                sums = [0.0] * len(numeric_indices)
                counts = [0] * len(numeric_indices)

                # Gerar CSV em memoria com BOM UTF-8 para Excel
                buf = io.BytesIO()
                buf.write(b'\xef\xbb\xbf')  # BOM UTF-8
                
                # Usa ponto-e-virgula (;) para o Excel em PT-BR abrir em colunas automaticamente
                writer = csv.writer(buf, delimiter=';')
                writer.writerow(header)

                for row in rows:
                    row_list = list(row)
                    # Normaliza para UTF-8 bytes (Python 2.7 csv.writer espera str/bytes)
                    encoded = []
                    for val in row_list:
                        if val is None:
                            encoded.append('')
                        elif isinstance(val, unicode):
                            encoded.append(val.encode('utf-8'))
                        elif isinstance(val, str):
                            # Ja sao bytes UTF-8 do SQLite, passa direto
                            encoded.append(val)
                        else:
                            encoded.append(val)
                    writer.writerow(encoded)
                    # Acumular para medias se status == 'completo'
                    status_val = row_list[3]
                    if status_val in ('completo', u'completo'):
                        for k, idx in enumerate(numeric_indices):
                            v = row_list[idx]
                            if v is not None:
                                try:
                                    sums[k] += float(v)
                                    counts[k] += 1
                                except (TypeError, ValueError):
                                    pass

                # Linha de medias
                media_row = ['MEDIA'] + [''] * (len(header) - 1)
                for k, idx in enumerate(numeric_indices):
                    if counts[k] > 0:
                        avg_val = sums[k] / counts[k]
                        media_row[idx] = round(avg_val, 2)
                    else:
                        media_row[idx] = ''
                encoded_media = []
                for val in media_row:
                    if isinstance(val, unicode):
                        encoded_media.append(val.encode('utf-8'))
                    elif val is None:
                        encoded_media.append('')
                    else:
                        encoded_media.append(val)
                writer.writerow(encoded_media)

                csv_bytes = buf.getvalue()
                self.send_response(200)
                self.send_header('Content-Type', 'text/csv; charset=utf-8')
                self.send_header('Content-Disposition', 'attachment; filename=dados_experimento.csv')
                self.send_header('Content-Length', str(len(csv_bytes)))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(csv_bytes)
            except Exception as e:
                _send_json(self, {"erro": str(e)}, 500)

        else:
            self.send_error(404)

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        try:
            body = json.loads(self.rfile.read(length).decode('utf-8'))
        except:
            body = {}

        if self.path == '/personalidade':
            p = body.get('personalidade')
            hash_part = body.get('hash_participante', 'Anonimo')
            questionario_id = body.get('questionario_id', None)
            if p not in [0,1,2,3]:
                _send_json(self, {"erro": "personalidade invalida (0-3)"}, 400)
                return
            with _lock:
                estado['personalidade']=p; estado['fase']='aguardando_jogada'
                estado['rodada']=1; estado['sr']=0
                estado['moedas_jogador']=0; estado['moedas_nao']=0
                estado['ultimo_resultado']=None; estado['ultima_fala']=''
                estado['ultimo_delta_jogador']=0; estado['ultimo_delta_nao']=0
                estado['questionario_id'] = questionario_id
                try:
                    conn = sqlite3.connect('dados_experimento_quest.db')
                    c = conn.cursor()
                    c.execute("INSERT INTO sessoes (start_time, personalidade, hash_participante, questionario_id) VALUES (?, ?, ?, ?)",
                              (datetime.datetime.now(), p, hash_part, questionario_id))
                    sid = c.lastrowid
                    estado['session_id'] = sid
                    # Vincular questionario pre a esta sessao
                    if questionario_id:
                        c.execute("UPDATE pre_questionarios SET session_id=?, status='em_jogo' WHERE id=?",
                                  (sid, questionario_id))
                    conn.commit()
                    conn.close()
                except Exception as e:
                    print("[ERRO DB] sessoes: " + str(e))
            print("[JOGO] Personalidade: {}".format(p))
            _send_json(self, dict(estado))

        elif self.path == '/jogada':
            with _lock:
                if estado['fase'] != 'aguardando_jogada':
                    _send_json(self, {"erro": "fase incorreta: "+str(estado['fase'])}, 400)
                    return
                estado['fase']='processando'
                p=estado['personalidade']; sr=estado['sr']; rod=estado['rodada']-1

            sh = body.get('escolha')
            if sh not in [0,1]:
                with _lock: estado['fase']='aguardando_jogada'
                _send_json(self, {"erro": "escolha invalida (0|1)"}, 400)
                return

            s=defs(sr,sh); dj,dn=DELTAS[s]; texto=BIB[p][s][rod]

            with _lock:
                estado['moedas_jogador']=max(0,estado['moedas_jogador']+dj)
                estado['moedas_nao']=max(0,estado['moedas_nao']+dn)
                estado['ultimo_resultado']=s; estado['ultima_fala']=texto
                estado['ultimo_delta_jogador']=dj; estado['ultimo_delta_nao']=dn
                estado['sr']=sh
                try:
                    if estado['session_id']:
                        conn = sqlite3.connect('dados_experimento_quest.db')
                        c = conn.cursor()
                        c.execute('''INSERT INTO rodadas
                                  (session_id, rodada, escolha_jogador, escolha_nao, resultado, moedas_jogador, moedas_nao, timestamp)
                                  VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                                  (estado['session_id'], estado['rodada'], sh, sr, s, estado['moedas_jogador'], estado['moedas_nao'], datetime.datetime.now()))
                        conn.commit()
                        conn.close()
                except Exception as e:
                    print("[ERRO DB] rodadas: " + str(e))

                if estado['rodada']>=MAX_RODADAS: estado['fase']='fim'
                else: estado['rodada']+=1; estado['fase']='aguardando_jogada'
                snap=dict(estado)

            print("[JOGO] R{} jog={} nao={} s={} dj={} dn={}".format(rod+1,sh,sr,s,dj,dn))

            def nao_react():
                try:
                    if p==2: tts.say(texto)
                    else:
                        id_f=tts.post.say(texto)
                        executar_gesto(p,s)
                        tts.wait(id_f,0)
                except Exception as ex: print("[ERRO] nao_react: "+str(ex))

            t=threading.Thread(target=nao_react); t.daemon=True; t.start()
            _send_json(self, snap)

        elif self.path == '/reiniciar':
            with _lock:
                if estado['session_id']:
                    try:
                        interrompida = body.get('interrompida', False)
                        if interrompida:
                            winner = 'interrompida'
                        else:
                            winner = 'empate'
                            if estado['moedas_jogador'] > estado['moedas_nao']: winner = 'jogador'
                            elif estado['moedas_nao'] > estado['moedas_jogador']: winner = 'nao'
                        conn = sqlite3.connect('dados_experimento_quest.db')
                        c = conn.cursor()
                        c.execute("UPDATE sessoes SET end_time=?, winner=? WHERE id=?",
                                  (datetime.datetime.now(), winner, estado['session_id']))
                        # Marcar pre-questionario como finalizado
                        qid = estado.get('questionario_id')
                        if qid:
                            c.execute("UPDATE pre_questionarios SET status='jogo_concluido' WHERE id=?", (qid,))
                        conn.commit()
                        conn.close()
                    except Exception as e:
                        print("[ERRO DB] fechar sessao: " + str(e))

                estado['fase']='aguardando_personalidade'; estado['rodada']=0
                estado['personalidade']=None; estado['sr']=0
                estado['moedas_jogador']=0; estado['moedas_nao']=0
                estado['ultimo_resultado']=None; estado['ultima_fala']=''
                estado['ultimo_delta_jogador']=0; estado['ultimo_delta_nao']=0
                estado['session_id']=None; estado['questionario_id']=None
            print("[JOGO] Reiniciado.")
            _send_json(self, dict(estado))

        elif self.path == '/questionario/pre':
            try:
                conn = sqlite3.connect('dados_experimento_quest.db')
                c = conn.cursor()
                c.execute('''
                    INSERT INTO pre_questionarios
                    (timestamp, status, genero, idade, escolaridade, freq_jogos,
                     contato_robos, conhecimento_dilema,
                     godspeed_1, godspeed_2, godspeed_3, godspeed_4, godspeed_5,
                     godspeed_6, godspeed_7, godspeed_8, godspeed_9, godspeed_10,
                     godspeed_11, godspeed_12, godspeed_13, godspeed_14, godspeed_15,
                     godspeed_16, godspeed_17, godspeed_18, godspeed_19, godspeed_20,
                     godspeed_21, godspeed_22, godspeed_23, godspeed_24,
                     tempo_pre_segundos)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                ''', (
                    datetime.datetime.now(),
                    'aguardando',
                    body.get('genero', ''),
                    body.get('idade', ''),
                    body.get('escolaridade', ''),
                    body.get('freq_jogos', 0),
                    body.get('contato_robos', 0),
                    body.get('conhecimento_dilema', 0),
                    body.get('godspeed_1', 0), body.get('godspeed_2', 0), body.get('godspeed_3', 0),
                    body.get('godspeed_4', 0), body.get('godspeed_5', 0), body.get('godspeed_6', 0),
                    body.get('godspeed_7', 0), body.get('godspeed_8', 0), body.get('godspeed_9', 0),
                    body.get('godspeed_10', 0), body.get('godspeed_11', 0), body.get('godspeed_12', 0),
                    body.get('godspeed_13', 0), body.get('godspeed_14', 0), body.get('godspeed_15', 0),
                    body.get('godspeed_16', 0), body.get('godspeed_17', 0), body.get('godspeed_18', 0),
                    body.get('godspeed_19', 0), body.get('godspeed_20', 0), body.get('godspeed_21', 0),
                    body.get('godspeed_22', 0), body.get('godspeed_23', 0), body.get('godspeed_24', 0),
                    body.get('tempo_pre_segundos', None)
                ))
                qid = c.lastrowid
                conn.commit()
                conn.close()
                # Sinalizar que um questionario esta aguardando liberacao
                with _lock_lib:
                    _jogo_liberado['questionario_id'] = qid
                    _jogo_liberado['liberado'] = False
                _send_json(self, {"questionario_id": qid, "status": "aguardando"})
            except Exception as e:
                _send_json(self, {"erro": str(e)}, 500)

        elif self.path == '/questionario/pos':
            try:
                qid = body.get('questionario_id')
                sid = body.get('session_id')
                conn = sqlite3.connect('dados_experimento_quest.db')
                c = conn.cursor()
                tempo_pos = body.get('tempo_pos_segundos')
                if tempo_pos is None: tempo_pos = 0
                tempo_jogo = body.get('tempo_jogo_segundos')
                if tempo_jogo is None: tempo_jogo = 0
                tempo_pre = 0
                if qid:
                    c.execute("SELECT tempo_pre_segundos FROM pre_questionarios WHERE id=?", (qid,))
                    row = c.fetchone()
                    if row and row[0]:
                        tempo_pre = row[0]
                tempo_total = tempo_pre + tempo_jogo + tempo_pos

                c.execute('''
                    INSERT INTO pos_questionarios
                    (questionario_id, session_id, timestamp,
                     A1, A2, A3, A4, A5,
                     B1, B2, B3,
                     C1, C2, C3, C4, C5,
                     godspeed_pos_1, godspeed_pos_2, godspeed_pos_3, godspeed_pos_4, godspeed_pos_5,
                     godspeed_pos_6, godspeed_pos_7, godspeed_pos_8, godspeed_pos_9, godspeed_pos_10,
                     godspeed_pos_11, godspeed_pos_12, godspeed_pos_13, godspeed_pos_14, godspeed_pos_15,
                     godspeed_pos_16, godspeed_pos_17, godspeed_pos_18, godspeed_pos_19, godspeed_pos_20,
                     godspeed_pos_21, godspeed_pos_22, godspeed_pos_23, godspeed_pos_24,
                     tempo_pos_segundos, tempo_jogo_segundos, tempo_total_segundos)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                ''', (
                    qid, sid, datetime.datetime.now(),
                    body.get('A1', 0), body.get('A2', 0), body.get('A3', 0), body.get('A4', 0), body.get('A5', 0),
                    body.get('B1', 0), body.get('B2', 0), body.get('B3', 0),
                    body.get('C1', 0), body.get('C2', 0), body.get('C3', 0), body.get('C4', 0), body.get('C5', 0),
                    body.get('godspeed_pos_1', 0), body.get('godspeed_pos_2', 0), body.get('godspeed_pos_3', 0),
                    body.get('godspeed_pos_4', 0), body.get('godspeed_pos_5', 0), body.get('godspeed_pos_6', 0),
                    body.get('godspeed_pos_7', 0), body.get('godspeed_pos_8', 0), body.get('godspeed_pos_9', 0),
                    body.get('godspeed_pos_10', 0), body.get('godspeed_pos_11', 0), body.get('godspeed_pos_12', 0),
                    body.get('godspeed_pos_13', 0), body.get('godspeed_pos_14', 0), body.get('godspeed_pos_15', 0),
                    body.get('godspeed_pos_16', 0), body.get('godspeed_pos_17', 0), body.get('godspeed_pos_18', 0),
                    body.get('godspeed_pos_19', 0), body.get('godspeed_pos_20', 0), body.get('godspeed_pos_21', 0),
                    body.get('godspeed_pos_22', 0), body.get('godspeed_pos_23', 0), body.get('godspeed_pos_24', 0),
                    tempo_pos, tempo_jogo, tempo_total
                ))
                # Atualizar status do pre
                if qid:
                    c.execute("UPDATE pre_questionarios SET status='completo' WHERE id=?", (qid,))
                conn.commit()
                conn.close()
                _send_json(self, {"ok": True})
            except Exception as e:
                _send_json(self, {"erro": str(e)}, 500)

        elif self.path == '/questionario/desistir':
            try:
                qid = body.get('questionario_id')
                if qid:
                    conn = sqlite3.connect('dados_experimento_quest.db')
                    c = conn.cursor()
                    c.execute("UPDATE pre_questionarios SET status='desistiu' WHERE id=?", (qid,))
                    conn.commit()
                    conn.close()
                # Limpar estado de liberacao
                with _lock_lib:
                    if _jogo_liberado['questionario_id'] == qid:
                        _jogo_liberado['questionario_id'] = None
                        _jogo_liberado['liberado'] = False
                _send_json(self, {"ok": True})
            except Exception as e:
                _send_json(self, {"erro": str(e)}, 500)

        elif self.path == '/questionario/nao-participante':
            try:
                sid = body.get('session_id', None)
                conn = sqlite3.connect('dados_experimento_quest.db')
                c = conn.cursor()
                c.execute("INSERT INTO nao_participantes (session_id, timestamp) VALUES (?, ?)",
                          (sid, datetime.datetime.now()))
                conn.commit()
                conn.close()
                _send_json(self, {"ok": True})
            except Exception as e:
                _send_json(self, {"erro": str(e)}, 500)

        elif self.path == '/questionario/liberar-jogo':
            # Pesquisador confirma a liberacao do jogo
            try:
                qid = body.get('questionario_id')
                with _lock_lib:
                    if _jogo_liberado['questionario_id'] == qid:
                        _jogo_liberado['liberado'] = True
                _send_json(self, {"ok": True, "liberado": True})
            except Exception as e:
                _send_json(self, {"erro": str(e)}, 500)

        else:
            self.send_error(404)

    def log_message(self, fmt, *args):
        print("[HTTP] "+(fmt%args))

# ─── Main ─────────────────────────────────────────────────
if __name__ == '__main__':
    motion.wakeUp()
    posture.goToPosture("Stand", 0.6)
    print("="*50)
    print("  Moedas & Ruinas - Servidor HTTP  porta:{}".format(HTTP_PORT))
    print("="*50)
    server = HTTPServer(('0.0.0.0', HTTP_PORT), GameHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[JOGO] Encerrado.")
        server.server_close()
