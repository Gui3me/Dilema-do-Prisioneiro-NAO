(function(){
  "use strict";

  /* ---------- Font scale control ---------- */
  var FC_MIN = 0.85, FC_MAX = 1.3, FC_STEP = 0.1;
  var fontScale = parseFloat(localStorage.getItem('font_scale')) || 1;
  var fcDecrease = document.getElementById('font-decrease');
  var fcIncrease = document.getElementById('font-increase');
  var fcLabel = document.getElementById('font-scale-label');

  function applyFontScale(){
    fontScale = Math.round(fontScale * 100) / 100;
    document.documentElement.style.setProperty('--font-scale', fontScale);
    fcLabel.textContent = Math.round(fontScale * 100) + '%';
    fcDecrease.disabled = fontScale <= FC_MIN;
    fcIncrease.disabled = fontScale >= FC_MAX;
  }
  fcDecrease.addEventListener('click', function(){
    fontScale = Math.max(FC_MIN, fontScale - FC_STEP);
    localStorage.setItem('font_scale', fontScale);
    applyFontScale();
  });
  fcIncrease.addEventListener('click', function(){
    fontScale = Math.min(FC_MAX, fontScale + FC_STEP);
    localStorage.setItem('font_scale', fontScale);
    applyFontScale();
  });
  applyFontScale();

  /* ---------- NAO API Config ---------- */
  var storedIp = localStorage.getItem('nao_ip') || '10.43.151.105';
  var NAO_API = 'http://' + storedIp + ':5050';

  var connDot = document.getElementById('conn-status-dot');
  var connCaption = document.getElementById('conn-status-caption');

  function setConnState(state){
    connDot.className = 'conn-dot ' + state;
    connCaption.className = 'conn-caption ' + state;
    if(state === 'ok') connCaption.textContent = 'Conectado ao rob\u00f4';
    else if(state === 'fail') connCaption.textContent = 'Sem resposta do rob\u00f4';
    else connCaption.textContent = 'Verificando conex\u00e3o\u2026';
  }

  var ipInput = document.getElementById('api-ip-input');
  if(ipInput) {
    ipInput.value = storedIp;
    ipInput.addEventListener('change', function(){
      var newIp = this.value.trim();
      if(newIp) {
        localStorage.setItem('nao_ip', newIp);
        NAO_API = 'http://' + newIp + ':5050';
        setConnState('pending');
        checkGameState();
      }
    });
  }

  /* ---------- Dashboard & Tabs ---------- */
  var dashTabs = Array.prototype.slice.call(document.querySelectorAll('.dash-tab'));
  var dashNavItems = Array.prototype.slice.call(document.querySelectorAll('.dash-nav-item'));
  var apiWarn = document.getElementById('game-active-warn');
  var apiStatus = document.getElementById('api-status');
  var pBtns = Array.prototype.slice.call(document.querySelectorAll('.personality-btn'));
  var topbarTitle = document.getElementById('topbar-title');

  function activateTab(item){
    dashNavItems.forEach(function(nav){ nav.classList.remove('active'); });
    dashTabs.forEach(function(tab){ tab.classList.remove('active'); });
    item.classList.add('active');
    document.getElementById(item.getAttribute('data-tab')).classList.add('active');
    var label = item.textContent.trim();
    if(label) topbarTitle.textContent = label;
  }

  dashNavItems.forEach(function(item){
    item.addEventListener('click', function(){ activateTab(item); });
    item.addEventListener('keydown', function(e){
      if(e.key === 'Enter' || e.key === ' '){ e.preventDefault(); activateTab(item); }
    });
  });

  // Session panel elements
  var sessionPanel = document.getElementById('session-info-panel');
  var sessionInfoId = document.getElementById('session-info-id');
  var sessionInfoHash = document.getElementById('session-info-hash');
  var sessionInfoRodada = document.getElementById('session-info-rodada');


  function fetchResultados() {
    fetch(NAO_API + '/resultados')
      .then(function(r){ return r.json(); })
      .then(function(data){
        if(data.erro) return;

        document.getElementById('stat-sessoes').textContent = data.estatisticas.total_sessoes;
        document.getElementById('stat-vit-jog').textContent = data.estatisticas.vitorias_jogador;
        document.getElementById('stat-vit-nao').textContent = data.estatisticas.vitorias_nao;
        document.getElementById('stat-empates').textContent = data.estatisticas.empates;

        var jogCoop = data.estatisticas.jogador_cooperou;
        var jogTraiu = data.estatisticas.jogador_traiu;
        var totalJog = jogCoop + jogTraiu;
        var jogPct = totalJog > 0 ? Math.round((jogCoop / totalJog) * 100) : 0;
        document.getElementById('val-jog-coop').textContent = jogCoop;
        document.getElementById('val-jog-traiu').textContent = jogTraiu;
        document.getElementById('label-jog-pct').textContent = jogPct + '% cooperou';
        document.getElementById('bar-jog-coop').style.width = jogPct + '%';

        var naoCoop = data.estatisticas.nao_cooperou;
        var naoTraiu = data.estatisticas.nao_traiu;
        var totalNao = naoCoop + naoTraiu;
        var naoPct = totalNao > 0 ? Math.round((naoCoop / totalNao) * 100) : 0;
        document.getElementById('val-nao-coop').textContent = naoCoop;
        document.getElementById('val-nao-traiu').textContent = naoTraiu;
        document.getElementById('label-nao-pct').textContent = naoPct + '% cooperou';
        document.getElementById('bar-nao-coop').style.width = naoPct + '%';

        var tbody = document.getElementById('sessoes-tbody');
        if(!data.sessoes || data.sessoes.length === 0) {
          tbody.innerHTML = '<tr class="empty-row"><td colspan="6">Nenhuma sess\u00e3o registrada.</td></tr>';
        } else {
          tbody.innerHTML = '';
          var personalidades = ['Amig\u00e1vel', 'Competitivo', 'Neutro', 'Melanc\u00f3lico'];
          data.sessoes.forEach(function(s) {
            var tr = document.createElement('tr');
            var pName = personalidades[s.personalidade] || 'Desconhecida';
            var wStr = '<span class="badge badge-neutral">Em andamento</span>';
            if (s.winner === 'interrompida') {
              wStr = '<span class="badge badge-bad">Interrompida</span>';
            } else if (s.winner) {
              var wLabel = s.winner.charAt(0).toUpperCase() + s.winner.slice(1);
              var wClass = /jogador|participante/i.test(s.winner) ? 'badge-good' : (/nao/i.test(s.winner) ? 'badge-bad' : 'badge-neutral');
              wStr = '<span class="badge ' + wClass + '">' + wLabel + '</span>';
            }
            var hashStr = s.hash_participante || '\u2014';
            tr.innerHTML =
              '<td class="cell-id">' + s.id + '</td>' +
              '<td class="cell-hash">' + hashStr + '</td>' +
              '<td class="cell-muted">' + s.start_time.split('.')[0] + '</td>' +
              '<td>' + pName + '</td>' +
              '<td>' + wStr + '</td>' +
              '<td style="text-align:right;">' +
                 '<button class="btn-view-sessao" data-id="'+s.id+'">Ver dados</button>' +
              '</td>';
            tbody.appendChild(tr);
          });

          document.querySelectorAll('.btn-view-sessao').forEach(function(btn){
            btn.addEventListener('click', function(){
              var sid = this.getAttribute('data-id');
              document.getElementById('sessao-details-id').textContent = sid;
              fetch(NAO_API + '/sessao/' + sid)
                .then(function(res){ return res.json(); })
                .then(function(sessData){
                  if(sessData.erro) return;
                  var dtbody = document.getElementById('sessao-rodadas-tbody');
                  if(!sessData.rodadas || sessData.rodadas.length === 0){
                    dtbody.innerHTML = '<tr class="empty-row"><td colspan="5">Sem rodadas</td></tr>';
                    document.getElementById('sd-moedas-jog').textContent = '0';
                    document.getElementById('sd-moedas-nao').textContent = '0';
                  } else {
                    dtbody.innerHTML = '';
                    var lastR = sessData.rodadas[sessData.rodadas.length - 1];
                    document.getElementById('sd-moedas-jog').textContent = lastR.moedas_jogador;
                    document.getElementById('sd-moedas-nao').textContent = lastR.moedas_nao;
                    sessData.rodadas.forEach(function(r){
                      var dtr = document.createElement('tr');
                      var escJog = r.escolha_jogador === 0 ? 'Cooperou' : 'Traiu';
                      var escNao = r.escolha_nao === 0 ? 'Cooperou' : 'Traiu';
                      var resStr = '';
                      if(r.resultado === 0) resStr = '<span class="badge badge-good">Ambos cooperaram</span>';
                      else if(r.resultado === 1) resStr = '<span class="badge badge-neutral">Voc\u00ea traiu</span>';
                      else if(r.resultado === 2) resStr = '<span class="badge badge-neutral">NAO traiu</span>';
                      else resStr = '<span class="badge badge-bad">Ambos tra\u00edram</span>';
                      dtr.innerHTML =
                        '<td class="cell-id">' + r.rodada + '</td>' +
                        '<td>' + escJog + '</td>' +
                        '<td>' + escNao + '</td>' +
                        '<td>' + resStr + '</td>' +
                        '<td class="cell-muted">' + r.moedas_jogador + ' \u00d7 ' + r.moedas_nao + '</td>';
                      dtbody.appendChild(dtr);
                    });
                  }
                  document.getElementById('sessao-details-container').style.display = 'block';
                });
            });
          });
        }
      })
      .catch(function(){});
  }

  document.getElementById('close-sessao-details').addEventListener('click', function(){
    document.getElementById('sessao-details-container').style.display = 'none';
  });

  /* ---------- Hash generation ---------- */
  function generateParticipantHash() {
    var raw = Date.now().toString(36) + Math.random().toString(36).substr(2, 8);
    var hash = 0;
    for (var i = 0; i < raw.length; i++) {
      var chr = raw.charCodeAt(i);
      hash = ((hash << 5) - hash) + chr;
      hash |= 0;
    }
    var ts = Date.now().toString(16);
    var hashHex = Math.abs(hash).toString(16);
    return (ts + hashHex).substr(0, 12).toUpperCase();
  }

  /* ---------- Personality selection -- opens modal ---------- */
  var qModalOverlay = document.getElementById('q-modal-overlay');
  var pendingPersonality = null;

  pBtns.forEach(function(btn){
    btn.addEventListener('click', function(){
      pendingPersonality = parseInt(btn.getAttribute('data-p'), 10);
      openQModal();
    });
  });

  function openQModal(){
    if(!qModalOverlay) return;
    qModalOverlay.style.display = 'flex';
    var listContainer = document.getElementById('q-modal-list');
    if(!listContainer) return;

    listContainer.innerHTML = '<div style="font-size:.85rem; color:var(--ink-soft);">Buscando question\u00e1rios aguardando...</div>';

    fetch(NAO_API + '/questionario/lista')
      .then(function(r){ return r.json(); })
      .then(function(data){
         var aguardando = data.questionarios ? data.questionarios.filter(function(q){ return q.status === 'aguardando'; }) : [];
         listContainer.innerHTML = '';
         if(aguardando.length === 0){
            listContainer.innerHTML = '<div style="font-size:.85rem; color:var(--ink-faint); padding:12px; background:var(--surface-soft); border-radius:8px; text-align:center;">Nenhum question\u00e1rio em espera.<br>O participante j\u00e1 enviou?</div>';
         } else {
            aguardando.forEach(function(q){
               var btn = document.createElement('button');
               btn.className = 'btn btn-primary';
               btn.style.justifyContent = 'center';
               btn.style.fontSize = '0.9rem';
               btn.style.padding = '12px 18px';
               btn.innerHTML = '<svg width=18 height=18 viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:8px;"><rect x="1" y="4" width="22" height="16" rx="2" ry="2"/><line x1="1" y1="10" x2="23" y2="10"/></svg> Iniciar jogo para Q' + q.id;
               btn.onclick = function(){
                  confirmAndStart(q.id);
               };
               listContainer.appendChild(btn);
            });
         }
      })
      .catch(function(){
         listContainer.innerHTML = '<div style="color:var(--bad);">Erro ao carregar lista de question\u00e1rios.</div>';
      });
  }

  function closeQModal(){
    if(qModalOverlay) qModalOverlay.style.display = 'none';
    pendingPersonality = null;
  }

  function confirmAndStart(qid){
    var p = pendingPersonality;       // salva antes de closeQModal() zerar
    var hashPart = generateParticipantHash();
    fetch(NAO_API + '/questionario/liberar-jogo', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({questionario_id: qid})
    }).catch(function(){});
    closeQModal();
    launchGame(p, hashPart, qid);
  }

  var qModalClose = document.getElementById('q-modal-close');
  if(qModalClose) qModalClose.addEventListener('click', closeQModal);
  if(qModalOverlay) qModalOverlay.addEventListener('click', function(e){
    if(e.target === qModalOverlay) closeQModal();
  });

  var btnSemQ = document.getElementById('q-modal-btn-sem-q');
  if(btnSemQ) btnSemQ.addEventListener('click', function(){
    if(pendingPersonality === null) return;
    var p = pendingPersonality;       // salva antes de closeQModal() zerar
    var hashPart = generateParticipantHash();
    closeQModal();
    launchGame(p, hashPart, null);
    fetch(NAO_API + '/questionario/nao-participante', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({session_id: null})
    }).catch(function(){});
  });

  /* ---------- Launch game ---------- */
  function launchGame(p, hashPart, questionarioId){
    pBtns.forEach(function(b){ b.classList.remove('selected'); b.disabled = true; });
    var activeBtn = document.querySelector('.personality-btn[data-p="'+p+'"]');
    if(activeBtn) activeBtn.classList.add('selected');
    apiStatus.textContent = 'Conectando ao NAO...';

    var payload = { personalidade: p, hash_participante: hashPart };
    if(questionarioId !== null) payload.questionario_id = questionarioId;

    fetch(NAO_API + '/personalidade', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    .then(function(r){
      if(!r.ok) throw new Error('HTTP ' + r.status);
      return r.json();
    })
    .then(function(data){
      apiStatus.textContent = 'Sess\u00e3o iniciada! Hash: ' + hashPart;
      setTimeout(function(){ apiStatus.textContent = ''; }, 4000);
      pBtns.forEach(function(b){ b.disabled = false; });
      sessionPanel.classList.add('show');
      sessionInfoId.textContent = data.session_id || '\u2014';
      sessionInfoHash.textContent = data.hash_participante || hashPart;
      sessionInfoRodada.textContent = '1/5';
      if(data.session_id) localStorage.setItem('last_session_id', data.session_id);
      if(questionarioId)  localStorage.setItem('last_questionario_id', questionarioId);
    })
    .catch(function(err){
      apiStatus.textContent = 'N\u00e3o foi poss\u00edvel conectar ao NAO (' + err.message + ')';
      pBtns.forEach(function(b){ b.disabled = false; });
      if(activeBtn) activeBtn.classList.remove('selected');
    });
  }

  /* ---------- Helper: formata segundos em MM:SS ---------- */
  function secsToMMSS(secs) {
    if (secs === null || secs === undefined || secs === '' || isNaN(Number(secs))) return '—';
    var s = Math.round(Number(secs));
    var m = Math.floor(s / 60);
    var r = s % 60;
    return (m < 10 ? '0' : '') + m + ':' + (r < 10 ? '0' : '') + r;
  }

  /* ---------- Botão de exportação CSV ---------- */
  var btnExportCsv = document.getElementById('btn-export-csv');
  if (btnExportCsv) {
    btnExportCsv.addEventListener('click', function () {
      var storedIp = localStorage.getItem('nao_ip') || '10.43.151.105';
      window.open('http://' + storedIp + ':5050/exportar/csv', '_blank');
    });
  }

  /* ---------- Modal de detalhes de questionário ---------- */
  var qDetalheOverlay = document.getElementById('q-detalhe-overlay');
  var qDetalheContent = document.getElementById('q-detalhe-content');
  var qDetalheClose   = document.getElementById('q-detalhe-close');

  function openDetalheModal(qid) {
    if (!qDetalheOverlay) return;
    qDetalheOverlay.style.display = 'flex';
    if (qDetalheContent) qDetalheContent.innerHTML = 'Carregando...';

    fetch(NAO_API + '/questionario/detalhe/' + qid)
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (data.erro) {
          qDetalheContent.innerHTML = '<p style="color:var(--bad);">Erro: ' + data.erro + '</p>';
          return;
        }
        var pre  = data.pre  || {};
        var pos  = data.pos  || null;
        var sess = data.sessao || null;
        var personalidades = ['Amigável', 'Competitivo', 'Neutro', 'Melancólico'];

        var html = '<div style="font-size:.68rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--gold-deep);margin-bottom:4px;">Questionário Q' + qid + '</div>';
        html += '<h2 style="font-family:\'Fraunces\',serif;font-size:1.25rem;font-weight:600;margin:0 0 20px;">Detalhes do Participante</h2>';

        // Dados do participante
        html += '<h3 style="font-size:.9rem;font-weight:700;color:var(--ink-soft);margin:0 0 10px;border-bottom:1px solid var(--border);padding-bottom:6px;">Perfil</h3>';
        html += '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:20px;">';
        html += '<div><div style="font-size:.7rem;color:var(--ink-faint);">Gênero</div><div style="font-weight:600;">' + (pre.genero || '—') + '</div></div>';
        html += '<div><div style="font-size:.7rem;color:var(--ink-faint);">Idade</div><div style="font-weight:600;">' + (pre.idade || '—') + '</div></div>';
        html += '<div><div style="font-size:.7rem;color:var(--ink-faint);">Escolaridade</div><div style="font-weight:600;">' + (pre.escolaridade || '—') + '</div></div>';
        html += '<div><div style="font-size:.7rem;color:var(--ink-faint);">Freq. jogos</div><div style="font-weight:600;">' + (pre.freq_jogos !== undefined ? pre.freq_jogos : '—') + '</div></div>';
        html += '<div><div style="font-size:.7rem;color:var(--ink-faint);">Contato robôs</div><div style="font-weight:600;">' + (pre.contato_robos !== undefined ? pre.contato_robos : '—') + '</div></div>';
        html += '<div><div style="font-size:.7rem;color:var(--ink-faint);">Conhec. dilema</div><div style="font-weight:600;">' + (pre.conhecimento_dilema !== undefined ? pre.conhecimento_dilema : '—') + '</div></div>';
        html += '</div>';

        // Tempos
        html += '<h3 style="font-size:.9rem;font-weight:700;color:var(--ink-soft);margin:0 0 10px;border-bottom:1px solid var(--border);padding-bottom:6px;">Tempos</h3>';
        html += '<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:20px;">';
        html += '<div><div style="font-size:.7rem;color:var(--ink-faint);">Pré</div><div style="font-weight:600;font-size:1.1rem;">' + secsToMMSS(pre.tempo_pre_segundos) + '</div></div>';
        var tempoJogo  = pos ? pos.tempo_jogo_segundos  : null;
        var tempoPos   = pos ? pos.tempo_pos_segundos   : null;
        var tempoTotal = pos ? pos.tempo_total_segundos  : null;
        html += '<div><div style="font-size:.7rem;color:var(--ink-faint);">Jogo</div><div style="font-weight:600;font-size:1.1rem;">' + secsToMMSS(tempoJogo) + '</div></div>';
        html += '<div><div style="font-size:.7rem;color:var(--ink-faint);">Pós</div><div style="font-weight:600;font-size:1.1rem;">' + secsToMMSS(tempoPos) + '</div></div>';
        html += '<div><div style="font-size:.7rem;color:var(--ink-faint);">Total</div><div style="font-weight:600;font-size:1.1rem;">' + secsToMMSS(tempoTotal) + '</div></div>';
        html += '</div>';

        // GodSpeed Pré
        html += '<h3 style="font-size:.9rem;font-weight:700;color:var(--ink-soft);margin:0 0 10px;border-bottom:1px solid var(--border);padding-bottom:6px;">GodSpeed Pré (GS1–GS24)</h3>';
        html += '<div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:20px;">';
        for (var i = 1; i <= 24; i++) {
          var val = pre['godspeed_' + i];
          html += '<div style="min-width:48px;text-align:center;background:var(--surface-soft);border-radius:6px;padding:6px 8px;">';
          html += '<div style="font-size:.65rem;color:var(--ink-faint);">GS' + i + '</div>';
          html += '<div style="font-weight:700;">' + (val !== null && val !== undefined ? val : '—') + '</div>';
          html += '</div>';
        }
        html += '</div>';

        // Sessão
        if (sess) {
          html += '<h3 style="font-size:.9rem;font-weight:700;color:var(--ink-soft);margin:0 0 10px;border-bottom:1px solid var(--border);padding-bottom:6px;">Sessão</h3>';
          html += '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:20px;">';
          html += '<div><div style="font-size:.7rem;color:var(--ink-faint);">Personalidade</div><div style="font-weight:600;">' + (personalidades[sess.personalidade] || sess.personalidade || '—') + '</div></div>';
          html += '<div><div style="font-size:.7rem;color:var(--ink-faint);">Vencedor</div><div style="font-weight:600;">' + (sess.winner || '—') + '</div></div>';
          html += '<div><div style="font-size:.7rem;color:var(--ink-faint);">Início</div><div style="font-weight:600;">' + (sess.start_time ? sess.start_time.split('.')[0] : '—') + '</div></div>';
          html += '</div>';
        }

        // Pós-questionário
        if (!pos) {
          html += '<div style="background:var(--surface-soft);border-radius:8px;padding:16px;text-align:center;color:var(--ink-faint);font-size:.87rem;">Pós-questionário não respondido</div>';
        } else {
          html += '<h3 style="font-size:.9rem;font-weight:700;color:var(--ink-soft);margin:0 0 10px;border-bottom:1px solid var(--border);padding-bottom:6px;">Pós-questionário — Escala Likert</h3>';
          html += '<div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:20px;">';
          var likertCols = ['A1','A2','A3','A4','A5','B1','B2','B3','C1','C2','C3','C4','C5'];
          likertCols.forEach(function (col) {
            html += '<div style="min-width:48px;text-align:center;background:var(--surface-soft);border-radius:6px;padding:6px 8px;">';
            html += '<div style="font-size:.65rem;color:var(--ink-faint);">' + col + '</div>';
            html += '<div style="font-weight:700;">' + (pos[col] !== null && pos[col] !== undefined ? pos[col] : '—') + '</div>';
            html += '</div>';
          });
          html += '</div>';

          html += '<h3 style="font-size:.9rem;font-weight:700;color:var(--ink-soft);margin:0 0 10px;border-bottom:1px solid var(--border);padding-bottom:6px;">GodSpeed Pós (GS1–GS24)</h3>';
          html += '<div style="display:flex;flex-wrap:wrap;gap:6px;">';
          for (var j = 1; j <= 24; j++) {
            var valPos = pos['godspeed_pos_' + j];
            html += '<div style="min-width:48px;text-align:center;background:var(--surface-soft);border-radius:6px;padding:6px 8px;">';
            html += '<div style="font-size:.65rem;color:var(--ink-faint);">GS' + j + '</div>';
            html += '<div style="font-weight:700;">' + (valPos !== null && valPos !== undefined ? valPos : '—') + '</div>';
            html += '</div>';
          }
          html += '</div>';
        }

        if (qDetalheContent) qDetalheContent.innerHTML = html;
      })
      .catch(function (err) {
        if (qDetalheContent) qDetalheContent.innerHTML = '<p style="color:var(--bad);">Erro ao carregar detalhes.</p>';
      });
  }

  function closeDetalheModal() {
    if (qDetalheOverlay) qDetalheOverlay.style.display = 'none';
  }

  if (qDetalheClose)   qDetalheClose.addEventListener('click', closeDetalheModal);
  if (qDetalheOverlay) qDetalheOverlay.addEventListener('click', function (e) {
    if (e.target === qDetalheOverlay) closeDetalheModal();
  });

  /* ---------- Questionnaire Stats Tab ---------- */
  function secsToMMSS(s) {
    if (s === null || s === undefined || isNaN(s)) return '—';
    var m = Math.floor(s / 60);
    var sec = Math.floor(s % 60);
    return m + "m " + (sec < 10 ? "0" : "") + sec + "s";
  }

  function fetchQStats(){
    fetch(NAO_API + '/questionario/stats')
      .then(function(r){ return r.json(); })
      .then(function(data){
        var posTotal = data.pos ? data.pos.total : 0;
        var posIds   = data.pos ? data.pos.ids : [];
        var preIds   = data.pre ? data.pre.ids : [];
        var completedIds = posIds.filter(function(id){ return preIds.indexOf(id) !== -1; });
        var onlyPreIds   = preIds.filter(function(id){ return posIds.indexOf(id) === -1; });
        var desistentesTotal = data.desistentes ? data.desistentes.total : 0;
        var desistentesIds   = data.desistentes ? data.desistentes.ids   : [];
        var naoPartTotal     = data.nao_participantes ? data.nao_participantes.total : 0;
        var naoPartSids      = data.nao_participantes ? data.nao_participantes.session_ids : [];

        var elTotalComp = document.getElementById('qs-total-completo');
        var elIdsComp   = document.getElementById('qs-ids-completo');
        var elTotalPre  = document.getElementById('qs-total-pre');
        var elIdsPre    = document.getElementById('qs-ids-pre');
        var elTotalDes  = document.getElementById('qs-total-desistiu');
        var elIdsDes    = document.getElementById('qs-ids-desistiu');
        var elTotalNP   = document.getElementById('qs-total-nao-part');
        var elIdsNP     = document.getElementById('qs-ids-nao-part');

        if(elTotalComp) elTotalComp.textContent = completedIds.length;
        if(elIdsComp)   elIdsComp.textContent   = completedIds.length > 0 ? 'Q' + completedIds.join(', Q') : '\u2014';
        if(elTotalPre)  elTotalPre.textContent  = onlyPreIds.length;
        if(elIdsPre)    elIdsPre.textContent    = onlyPreIds.length > 0 ? 'Q' + onlyPreIds.join(', Q') : '\u2014';
        if(elTotalDes)  elTotalDes.textContent  = desistentesTotal;
        if(elIdsDes)    elIdsDes.textContent    = desistentesTotal > 0 ? 'Q' + desistentesIds.join(', Q') : '\u2014';
        if(elTotalNP)   elTotalNP.textContent   = naoPartTotal;
        if(elIdsNP)     elIdsNP.textContent     = naoPartTotal > 0 ? 'Sess. ' + naoPartSids.join(', ') : '\u2014';

        // Médias de tempo
        var elMediaPre   = document.getElementById('qs-media-pre');
        var elMediaJogo  = document.getElementById('qs-media-jogo');
        var elMediaPos   = document.getElementById('qs-media-pos');
        var elMediaTotal = document.getElementById('qs-media-total');
        if (elMediaPre)   elMediaPre.textContent   = data.media_tempo_pre   !== null && data.media_tempo_pre   !== undefined ? secsToMMSS(data.media_tempo_pre)   : '\u2014';
        if (elMediaJogo)  elMediaJogo.textContent  = data.media_tempo_jogo  !== null && data.media_tempo_jogo  !== undefined ? secsToMMSS(data.media_tempo_jogo)  : '\u2014';
        if (elMediaPos)   elMediaPos.textContent   = data.media_tempo_pos   !== null && data.media_tempo_pos   !== undefined ? secsToMMSS(data.media_tempo_pos)   : '\u2014';
        if (elMediaTotal) elMediaTotal.textContent = data.media_tempo_total !== null && data.media_tempo_total !== undefined ? secsToMMSS(data.media_tempo_total) : '\u2014';
      })
      .catch(function(){});

    fetch(NAO_API + '/questionario/lista')
      .then(function(r){ return r.json(); })
      .then(function(data){
        var tbody = document.getElementById('qs-lista-tbody');
        if(!tbody) return;
        if(!data.questionarios || data.questionarios.length === 0){
          tbody.innerHTML = '<tr class="empty-row"><td colspan="5">Nenhum question\u00e1rio registrado.</td></tr>';
          return;
        }
        tbody.innerHTML = '';
        var statusMap = {
          'aguardando':'<span class="badge badge-neutral">Aguardando</span>',
          'em_jogo':'<span class="badge badge-good">Em jogo</span>',
          'jogo_concluido':'<span class="badge badge-neutral">Jogo conclu\u00eddo</span>',
          'completo':'<span class="badge badge-good">Completo</span>',
          'desistiu':'<span class="badge badge-bad">Desistiu</span>'
        };
        data.questionarios.forEach(function(q){
          var tr = document.createElement('tr');
          var statusBadge = statusMap[q.status] || '<span class="badge badge-neutral">'+q.status+'</span>';
          tr.innerHTML =
            '<td class="cell-id">Q' + q.id + '</td>' +
            '<td class="cell-muted">' + (q.timestamp ? q.timestamp.split('.')[0] : '\u2014') + '</td>' +
            '<td>' + statusBadge + '</td>' +
            '<td>' + (q.session_id ? ('#' + q.session_id) : '\u2014') + '</td>' +
            '<td><button class="btn-view-q" data-qid="' + q.id + '" style="font-size:.78rem;padding:4px 10px;border-radius:6px;background:var(--surface-soft);border:1px solid var(--border);cursor:pointer;color:var(--ink);">Ver</button></td>';
          tbody.appendChild(tr);
        });

        // Bindar botoes de detalhe
        Array.prototype.slice.call(document.querySelectorAll('.btn-view-q')).forEach(function(btn){
          btn.addEventListener('click', function(){
            var qid = this.getAttribute('data-qid');
            openDetalheModal(qid);
          });
        });
      })
      .catch(function(){});
  }

  /* ---------- Post-game questionnaire prompt ---------- */
  var lastGameFase = null;
  var posPromptShown = false;

  function checkPostQ(data){
    if(data.fase === 'fim' && lastGameFase !== 'fim'){
      var qid = localStorage.getItem('last_questionario_id');
      if(qid){
        var panel = document.getElementById('pos-prompt-panel');
        var label = document.getElementById('pos-prompt-id');
        if(panel && !posPromptShown){
          posPromptShown = true;
          if(label) label.textContent = 'Q' + qid;
          panel.style.display = 'block';
          var qTab = document.querySelector('.dash-nav-item[data-tab="tab-questionarios"]');
          if(qTab) activateTab(qTab);
        }
      }
    }
    if(data.fase === 'aguardando_personalidade'){
      posPromptShown = false;
    }
    lastGameFase = data.fase;
  }

  var btnAbrirPos = document.getElementById('btn-abrir-pos');
  if(btnAbrirPos) {
    btnAbrirPos.addEventListener('click', function(){
      var qid = localStorage.getItem('last_questionario_id');
      document.getElementById('pos-prompt-panel').style.display = 'none';
      // Abre o pos-questionario com QID pre-preenchido em nova aba para o participante
      var url = 'posquestionario.html' + (qid ? '?questionario_id=' + qid : '');
      window.open(url, '_blank');
      localStorage.removeItem('last_questionario_id');
      localStorage.removeItem('last_session_id');
    });
  }

  var btnPularPos = document.getElementById('btn-pular-pos');
  if(btnPularPos) btnPularPos.addEventListener('click', function(){
    var qid = localStorage.getItem('last_questionario_id');
    document.getElementById('pos-prompt-panel').style.display = 'none';
    // Marca como desistente no backend (invalida o pre e incrementa desistencias)
    if(qid) {
      fetch(NAO_API + '/questionario/desistir', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({questionario_id: parseInt(qid, 10)})
      }).catch(function(){});
    }
    localStorage.removeItem('last_questionario_id');
    localStorage.removeItem('last_session_id');
  });

  /* ---------- checkGameState ---------- */
  function checkGameState() {
    fetch(NAO_API + '/estado')
      .then(function(r){ return r.json(); })
      .then(function(data){
        setConnState('ok');
        checkPostQ(data);
        var isPlaying = (data.fase === 'aguardando_jogada' || data.fase === 'processando') && data.rodada > 0;
        if(isPlaying){
          apiWarn.style.display = 'flex';
          pBtns.forEach(function(b){ b.disabled = true; });
          sessionPanel.classList.add('show');
          sessionInfoId.textContent = data.session_id || '\u2014';
          sessionInfoHash.textContent = data.hash_participante || '\u2014';
          sessionInfoRodada.textContent = data.rodada + '/' + 5;
        } else {
          apiWarn.style.display = 'none';
          pBtns.forEach(function(b){ b.disabled = false; });
          if(data.fase !== 'fim') sessionPanel.classList.remove('show');
          if(data.personalidade !== null && !document.querySelector('.personality-btn.selected')) {
            pBtns.forEach(function(b){ b.classList.remove('selected'); });
            var activeBtn = document.querySelector('.personality-btn[data-p="' + data.personalidade + '"]');
            if(activeBtn) activeBtn.classList.add('selected');
          }
        }
      })
      .catch(function(){
        setConnState('fail');
      });
  }

  // Poll state every 3 seconds
  setInterval(function(){
    checkGameState();
    if(document.getElementById('tab-results').classList.contains('active')) {
      fetchResultados();
    }
    if(document.getElementById('tab-questionarios') && document.getElementById('tab-questionarios').classList.contains('active')) {
      fetchQStats();
    }
  }, 3000);
  checkGameState();
  fetchResultados();
  fetchQStats();

  // Emergency button
  var btnEmergencia = document.getElementById('btn-emergencia');
  if(btnEmergencia){
    btnEmergencia.addEventListener('click', function(){
      if(confirm('Tem certeza que deseja interromper a partida imediatamente?')) {
        fetch(NAO_API + '/reiniciar', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({interrompida: true}) }).then(function(){
          sessionPanel.classList.remove('show');
          apiStatus.textContent = 'Sess\u00e3o interrompida de emerg\u00eancia!';
          pBtns.forEach(function(b){ b.classList.remove('selected'); b.disabled = false; });
        });
      }
    });
  }

})();
