import sqlite3, os

for db_file in ['dados_experimento_quest.db', 'dados_experimento.db']:
    print(f"\n=== {db_file} (tamanho: {os.path.getsize(db_file)} bytes) ===")
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in c.fetchall()]
    print("  Tabelas:", tables)
    for t in tables:
        c.execute(f"SELECT COUNT(*) FROM {t}")
        cnt = c.fetchone()[0]
        print(f"    {t}: {cnt} registros")
    conn.close()

