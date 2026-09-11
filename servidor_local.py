# -*- coding: utf-8 -*-
"""
servidor_local.py
Servidor HTTP local (Python 3) para visualizar dados do experimento sem o robô NAO.
Porta: 5050

Serve os mesmos endpoints do testejogo_api_questionario.py, mas SEM NAOqi.
Use para: ver dados de participantes, exportar CSV, visualizar questionários.

Uso:
    python servidor_local.py
Em seguida abra novopesquisador.html no navegador com IP = 127.0.0.1
"""

import json
import sqlite3
import csv
import io
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

# ─── Caminho do banco de dados ───────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Prefere dados_experimento_quest.db (usado pelo backend do NAO com questionários).
# Se estiver vazio ou não existir, cai para dados_experimento.db.
_DB_QUEST = os.path.join(SCRIPT_DIR, 'dados_experimento_quest.db')
_DB_MAIN  = os.path.join(SCRIPT_DIR, 'dados_experimento.db')

def _pick_db():
    if os.path.exists(_DB_QUEST) and os.path.getsize(_DB_QUEST) > 4096:
        return _DB_QUEST
    if os.path.exists(_DB_MAIN):
        return _DB_MAIN
    return _DB_QUEST  # deixa falhar com mensagem clara

DB_PATH = _pick_db()

HTTP_PORT = 5050

# ─── Estado simulado (somente leitura/visualização) ──────
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
    "hash_participante":    None,
}


def _send_json(handler, data, code=200):
    body = json.dumps(data, ensure_ascii=False).encode('utf-8')
    handler.send_response(code)
    handler.send_header('Content-Type', 'application/json; charset=utf-8')
    handler.send_header('Content-Length', str(len(body)))
    handler.send_header('Access-Control-Allow-Origin', '*')
    handler.end_headers()
    handler.wfile.write(body)


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


class Handler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        print(f"[HTTP] {self.address_string()} - {fmt % args}")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path

        # ── /estado ──────────────────────────────────────────
        if path == '/estado':
            _send_json(self, dict(estado))

        # ── /resultados ──────────────────────────────────────
        elif path == '/resultados':
            try:
                conn = get_db()
                c = conn.cursor()
                c.execute('SELECT id, start_time, personalidade, winner, hash_participante, questionario_id FROM sessoes ORDER BY id DESC')
                todas_sessoes = []
                for s in c.fetchall():
                    todas_sessoes.append({
                        "id": s[0], "start_time": s[1], "personalidade": s[2],
                        "winner": s[3], "hash_participante": s[4] if s[4] else "Anônimo",
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
                    "rodadas_atuais": [],
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

        # ── /sessao/<id> ─────────────────────────────────────
        elif path.startswith('/sessao/'):
            try:
                sid = int(path.split('/')[-1])
                conn = get_db()
                c = conn.cursor()
                c.execute(
                    'SELECT rodada, escolha_jogador, escolha_nao, resultado, moedas_jogador, moedas_nao '
                    'FROM rodadas WHERE session_id=? ORDER BY rodada', (sid,)
                )
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

        # ── /questionario/stats ──────────────────────────────
        elif path == '/questionario/stats':
            try:
                conn = get_db()
                c = conn.cursor()

                # Verifica tabelas existentes (compatibilidade com banco legado)
                c.execute("SELECT name FROM sqlite_master WHERE type='table'")
                existing_tables = {r[0] for r in c.fetchall()}

                ids_pre, ids_pos, ids_desistiu, total_desistiu = [], [], [], 0
                total_nao_part, ids_nao_part = 0, []
                row_avg = None

                if 'pre_questionarios' in existing_tables:
                    c.execute('SELECT id FROM pre_questionarios ORDER BY id')
                    ids_pre = [r[0] for r in c.fetchall()]
                    c.execute("SELECT COUNT(*) FROM pre_questionarios WHERE status='desistiu'")
                    total_desistiu = c.fetchone()[0] or 0
                    c.execute("SELECT id FROM pre_questionarios WHERE status='desistiu' ORDER BY id")
                    ids_desistiu = [r[0] for r in c.fetchall()]

                if 'pos_questionarios' in existing_tables:
                    c.execute('SELECT questionario_id FROM pos_questionarios ORDER BY questionario_id')
                    ids_pos = [r[0] for r in c.fetchall()]

                if 'nao_participantes' in existing_tables:
                    c.execute('SELECT COUNT(*) FROM nao_participantes')
                    total_nao_part = c.fetchone()[0] or 0
                    c.execute('SELECT session_id FROM nao_participantes ORDER BY session_id')
                    ids_nao_part = [r[0] for r in c.fetchall()]

                if 'pre_questionarios' in existing_tables and 'pos_questionarios' in existing_tables:
                    c.execute("PRAGMA table_info(pos_questionarios)")
                    pos_cols = {r[1] for r in c.fetchall()}
                    c.execute("PRAGMA table_info(pre_questionarios)")
                    pre_cols = {r[1] for r in c.fetchall()}

                    sel_pre  = 'pq.tempo_pre_segundos'    if 'tempo_pre_segundos'   in pre_cols else 'NULL'
                    sel_jogo = 'pos.tempo_jogo_segundos'  if 'tempo_jogo_segundos'  in pos_cols else 'NULL'
                    sel_pos  = 'pos.tempo_pos_segundos'   if 'tempo_pos_segundos'   in pos_cols else 'NULL'
                    sel_tot  = 'pos.tempo_total_segundos' if 'tempo_total_segundos' in pos_cols else 'NULL'

                    c.execute(f'''
                        SELECT AVG({sel_pre}), AVG({sel_jogo}), AVG({sel_pos}), AVG({sel_tot})
                        FROM pre_questionarios pq
                        JOIN pos_questionarios pos ON pos.questionario_id = pq.id
                        WHERE pq.status = 'completo'
                    ''')
                    row_avg = c.fetchone()

                def _fmt(v):
                    return round(v, 1) if v is not None else None

                conn.close()
                _send_json(self, {
                    "pre":  {"total": len(ids_pre),  "ids": ids_pre},
                    "pos":  {"total": len(ids_pos),  "ids": ids_pos},
                    "desistentes": {"total": total_desistiu, "ids": ids_desistiu},
                    "nao_participantes": {"total": total_nao_part, "session_ids": ids_nao_part},
                    "media_tempo_pre":   _fmt(row_avg[0]) if row_avg else None,
                    "media_tempo_jogo":  _fmt(row_avg[1]) if row_avg else None,
                    "media_tempo_pos":   _fmt(row_avg[2]) if row_avg else None,
                    "media_tempo_total": _fmt(row_avg[3]) if row_avg else None,
                })
            except Exception as e:
                _send_json(self, {"erro": str(e)}, 500)

        # ── /questionario/lista ──────────────────────────────
        elif path == '/questionario/lista':
            try:
                conn = get_db()
                c = conn.cursor()
                c.execute('SELECT id, timestamp, status, session_id FROM pre_questionarios ORDER BY id DESC')
                lista = [{"id": r[0], "timestamp": r[1], "status": r[2], "session_id": r[3]} for r in c.fetchall()]
                conn.close()
                _send_json(self, {"questionarios": lista})
            except Exception as e:
                _send_json(self, {"erro": str(e)}, 500)

        # ── /questionario/detalhe/<id> ───────────────────────
        elif path.startswith('/questionario/detalhe/'):
            try:
                qid = int(path.split('/')[-1])
                conn = get_db()
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
                pre_keys = ['id', 'timestamp', 'status', 'session_id', 'genero', 'idade', 'escolaridade',
                            'freq_jogos', 'contato_robos', 'conhecimento_dilema',
                            'godspeed_1', 'godspeed_2', 'godspeed_3', 'godspeed_4', 'godspeed_5',
                            'godspeed_6', 'godspeed_7', 'godspeed_8', 'godspeed_9', 'godspeed_10',
                            'godspeed_11', 'godspeed_12', 'godspeed_13', 'godspeed_14', 'godspeed_15',
                            'godspeed_16', 'godspeed_17', 'godspeed_18', 'godspeed_19', 'godspeed_20',
                            'godspeed_21', 'godspeed_22', 'godspeed_23', 'godspeed_24',
                            'tempo_pre_segundos']
                pre_data = dict(zip(pre_keys, row_pre))
                # Pós-questionário
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
                    pos_keys = ['A1', 'A2', 'A3', 'A4', 'A5', 'B1', 'B2', 'B3', 'C1', 'C2', 'C3', 'C4', 'C5',
                                'godspeed_pos_1', 'godspeed_pos_2', 'godspeed_pos_3', 'godspeed_pos_4', 'godspeed_pos_5',
                                'godspeed_pos_6', 'godspeed_pos_7', 'godspeed_pos_8', 'godspeed_pos_9', 'godspeed_pos_10',
                                'godspeed_pos_11', 'godspeed_pos_12', 'godspeed_pos_13', 'godspeed_pos_14', 'godspeed_pos_15',
                                'godspeed_pos_16', 'godspeed_pos_17', 'godspeed_pos_18', 'godspeed_pos_19', 'godspeed_pos_20',
                                'godspeed_pos_21', 'godspeed_pos_22', 'godspeed_pos_23', 'godspeed_pos_24',
                                'tempo_pos_segundos', 'tempo_jogo_segundos', 'tempo_total_segundos']
                    pos_data = dict(zip(pos_keys, row_pos))
                # Sessão vinculada
                sessao_data = None
                sid = pre_data.get('session_id')
                if sid:
                    c.execute('SELECT id, start_time, personalidade, winner, end_time FROM sessoes WHERE id=?', (sid,))
                    row_sess = c.fetchone()
                    if row_sess:
                        sessao_data = {
                            'id': row_sess[0], 'start_time': row_sess[1],
                            'personalidade': row_sess[2], 'winner': row_sess[3],
                            'end_time': row_sess[4]
                        }
                conn.close()
                _send_json(self, {"pre": pre_data, "pos": pos_data, "sessao": sessao_data})
            except Exception as e:
                _send_json(self, {"erro": str(e)}, 500)

        # ── /exportar/csv ────────────────────────────────────
        elif path == '/exportar/csv':
        try:
            import xml.sax.saxutils as saxutils
            conn = sqlite3.connect('dados_experimento_quest.db') if 'elif path == '/exportar/csv':'.startswith('elif self') else get_db()
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
                    pos.tempo_jogo_segundos, pos.tempo_pos_segundos, pos.tempo_total_segundos
                FROM pre_questionarios pq
                LEFT JOIN sessoes s ON s.id = pq.session_id
                LEFT JOIN pos_questionarios pos ON pos.questionario_id = pq.id
                ORDER BY pq.id
            ''')
            rows = c.fetchall()
            conn.close()

            gs_labels = [
                "Antropomorfismo > Falso / Natural",
                "Antropomorfismo > Aspecto mecanico / Aspecto humano",
                "Antropomorfismo > Inconsciente / Consciente",
                "Antropomorfismo > Artificial / Realista",
                "Antropomorfismo > Rigidez / Fluidez",
                "Animacidade > Morto / Com vida",
                "Animacidade > Parado / Energetico",
                "Animacidade > Mecanico / Organico",
                "Animacidade > Artificial / Realista",
                "Animacidade > Estatico / Interativo",
                "Animacidade > Apatico / Participativo",
                "Simpatia > Nao gosto / Gosto",
                "Simpatia > Hostil / Amigavel",
                "Simpatia > Antipatico / Gentil",
                "Simpatia > Desagradavel / Agradavel",
                "Simpatia > Horrivel / Simpatico",
                "Inteligencia > Incompetente / Competente",
                "Inteligencia > Ignorante / Sabedor",
                "Inteligencia > Irresponsavel / Responsavel",
                "Inteligencia > Pouco inteligente / Inteligente",
                "Inteligencia > Insensato / Sensato",
                "Seguranca > Ansioso / Descontraido",
                "Seguranca > Agitado / Calmo",
                "Seguranca > Sereno / Surpreendido"
            ]

            xml = []
            xml.append('<?xml version="1.0" encoding="utf-8"?>')
            xml.append('<?mso-application progid="Excel.Sheet"?>')
            xml.append('<Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet" xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:x="urn:schemas-microsoft-com:office:excel" xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet" xmlns:html="http://www.w3.org/TR/REC-html40">')
            
            xml.append('<Styles>')
            xml.append(' <Style ss:ID="HeaderPre"><Font ss:Bold="1" ss:Color="#000000"/><Interior ss:Color="#D9EAD3" ss:Pattern="Solid"/></Style>')
            xml.append(' <Style ss:ID="HeaderJogo"><Font ss:Bold="1" ss:Color="#000000"/><Interior ss:Color="#FFF2CC" ss:Pattern="Solid"/></Style>')
            xml.append(' <Style ss:ID="HeaderPos"><Font ss:Bold="1" ss:Color="#000000"/><Interior ss:Color="#F4CCCC" ss:Pattern="Solid"/></Style>')
            xml.append('</Styles>')

            def _s2(val):
                if val is None: return u""
                try:
                    if isinstance(val, unicode): return val
                except NameError: pass
                try:
                    if isinstance(val, bytes): return val.decode('utf-8')
                except Exception: pass
                return str(val)

            def format_row(row_data):
                r = ['   <Row>']
                for val, style in row_data:
                    s_val = _s2(val)
                    t = "Number" if isinstance(val, (int, float)) else "String"
                    cell = '    <Cell'
                    if style: cell += ' ss:StyleID="{}"'.format(style)
                    cell += '><Data ss:Type="{}">{}</Data></Cell>'.format(t, saxutils.escape(s_val).encode('utf-8').decode('utf-8'))
                    r.append(cell)
                r.append('   </Row>')
                return "\n".join(r)

            # 1. PLANILHA PRÉ
            xml.append(' <Worksheet ss:Name="Pre-Questionario">')
            xml.append('  <Table>')
            header_pre = ['ID Questionario', 'ID Sessao', 'Data/Hora (Pre)', 'Status', 'Genero', 'Idade', 'Escolaridade', 'Freq Jogos', 'Contato Robos', 'Conhec Dilema']
            header_pre.extend(['{} (GS_{})'.format(gs_labels[i-1], i) for i in range(1, 25)])
            header_pre.append('Tempo Resposta (seg)')
            xml.append(format_row([(h, "HeaderPre") for h in header_pre]))
            for row in rows:
                row_pre = list(row[0:35])
                xml.append(format_row([(v, None) for v in row_pre]))
            xml.append('  </Table>')
            xml.append(' </Worksheet>')

            # 2. PLANILHA JOGO
            xml.append(' <Worksheet ss:Name="Sessao de Jogo">')
            xml.append('  <Table>')
            header_jogo = ['ID Sessao', 'ID Questionario', 'Personalidade', 'Vencedor', 'Inicio', 'Fim']
            xml.append(format_row([(h, "HeaderJogo") for h in header_jogo]))
            for row in rows:
                if row[1] is not None:
                    row_jogo = [row[1], row[0], row[35], row[36], row[37], row[38]]
                    xml.append(format_row([(v, None) for v in row_jogo]))
            xml.append('  </Table>')
            xml.append(' </Worksheet>')

            # 3. PLANILHA PÓS
            xml.append(' <Worksheet ss:Name="Pos-Questionario">')
            xml.append('  <Table>')
            header_pos = ['ID Questionario', 'ID Sessao']
            header_pos += ['A1 (Muitos/Poucos motivos)', 'A2 (Dificil/Facil entender)', 'A3 (Nao sei/Sei o que esperava)', 'A4 (Surpreso/Nada surpreso)', 'A5 (Dificil/Facil prever)', 
                           'B1 (Robo quis me prejudicar)', 'B2 (Robo quis me ajudar)', 'B3 (Robo foi neutro)', 
                           'C1 (Robo cooperou/Enganou)', 'C2 (Robo foi justo/Injusto)', 'C3 (Robo previsivel/Imprevisivel)', 'C4 (Robo confiavel/Nao confiavel)', 'C5 (Robo amigavel/Hostil)']
            header_pos.extend(['{} (GS_POS_{})'.format(gs_labels[i-1], i) for i in range(1, 25)])
            header_pos += ['Tempo Jogo (s)', 'Tempo Resposta (s)', 'Tempo Total Experimento (s)']
            xml.append(format_row([(h, "HeaderPos") for h in header_pos]))
            for row in rows:
                if row[39] is not None:
                    row_pos = [row[0], row[1]] + list(row[39:79])
                    xml.append(format_row([(v, None) for v in row_pos]))
            xml.append('  </Table>')
            xml.append(' </Worksheet>')

            xml.append('</Workbook>')
            
            xls_bytes = ("\n".join(xml)).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/vnd.ms-excel; charset=utf-8')
            self.send_header('Content-Disposition', 'attachment; filename="dados_experimento.xls"')
            self.send_header('Content-Length', str(len(xls_bytes)))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(xls_bytes)
        except Exception as e:
            _send_json(self, {"erro": str(e)}, 500)
elif path == '/questionario/aguardando':
            _send_json(self, {"questionario_id": None, "liberado": False})

        else:
            self.send_error(404)

    def do_POST(self):
        """Endpoints POST são somente-leitura no servidor local — retorna resposta simulada."""
        path = urlparse(self.path).path
        length = int(self.headers.get('Content-Length', 0))
        try:
            body = json.loads(self.rfile.read(length).decode('utf-8')) if length else {}
        except Exception:
            body = {}

        # Endpoints que o painel chama mas não têm efeito sem o NAO
        if path in ('/questionario/liberar-jogo', '/questionario/nao-participante',
                    '/questionario/desistir', '/reiniciar', '/jogada'):
            _send_json(self, {"ok": True, "aviso": "Servidor local: ação ignorada (sem NAO)"})

        elif path == '/personalidade':
            _send_json(self, {"ok": True, "aviso": "Servidor local: sem NAO, sessão não iniciada"})

        else:
            self.send_error(404)


if __name__ == '__main__':
    if not os.path.exists(DB_PATH):
        print(f"[ERRO] Banco de dados não encontrado: {DB_PATH}")
        print("Certifique-se de que 'dados_experimento_quest.db' está na mesma pasta.")
        exit(1)

    server = HTTPServer(('127.0.0.1', HTTP_PORT), Handler)
    print("=" * 60)
    print(f"  Servidor local rodando em http://127.0.0.1:{HTTP_PORT}")
    print(f"  Banco: {DB_PATH}")
    print()
    print("  No painel (novopesquisador.html), coloque o IP: 127.0.0.1")
    print("  Pressione Ctrl+C para parar.")
    print("=" * 60)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[INFO] Servidor encerrado.")
