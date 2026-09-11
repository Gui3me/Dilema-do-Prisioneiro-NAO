import urllib.request, json

resp = urllib.request.urlopen('http://127.0.0.1:5050/resultados')
data = json.loads(resp.read())
print('Sessoes:', len(data['sessoes']), '| Total:', data['estatisticas']['total_sessoes'])

resp2 = urllib.request.urlopen('http://127.0.0.1:5050/questionario/lista')
data2 = json.loads(resp2.read())
print('Questionarios:', len(data2['questionarios']))

resp3 = urllib.request.urlopen('http://127.0.0.1:5050/questionario/stats')
data3 = json.loads(resp3.read())
print('Stats:', data3)

print('\nTudo OK! Servidor funcionando corretamente.')
