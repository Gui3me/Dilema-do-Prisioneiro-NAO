(function(){
  var urlParams = new URLSearchParams(window.location.search);
  var storedIp = localStorage.getItem('nao_ip') || '10.43.151.105';
  var NAO_API = 'http://' + storedIp + ':5050';

  var questionarioId = urlParams.get('questionario_id') || localStorage.getItem('questionario_id');
  var sessionId = null;
  var qidFromUrl = !!urlParams.get('questionario_id'); // veio do pesquisador via link

  var TOTAL_SECTIONS = 2;
  var currentSection = 0;

  var progressWrap = document.getElementById('progress-wrap');
  var progressLabel = document.getElementById('progress-label');
  var progressFrac  = document.getElementById('progress-frac');
  var progressFill  = document.getElementById('progress-fill');

  function updateProgress() {
    if(currentSection < 1) {
      if(progressWrap) progressWrap.style.display = 'none';
      return;
    }
    if(progressWrap) progressWrap.style.display = 'block';
    var pct = Math.round(((currentSection - 1) / (TOTAL_SECTIONS - 1)) * 100);
    if(pct > 100) {
      progressWrap.style.display = 'none';
    } else {
      if(progressLabel) progressLabel.textContent = 'Seção ' + currentSection + ' de ' + TOTAL_SECTIONS;
      if(progressFrac) progressFrac.textContent = pct + '%';
      if(progressFill) progressFill.style.width = pct + '%';
    }
  }

  function showSection(idStr) {
    document.querySelectorAll('.q-section').forEach(function(sec){ sec.classList.remove('active'); });
    var s = document.getElementById(idStr);
    if(s) s.classList.add('active');

    if(idStr === 'sec-pos-1') currentSection = 1;
    else if(idStr === 'sec-pos-2') currentSection = 2;
    else currentSection = 0;

    updateProgress();
    window.scrollTo(0,0);
  }

  // Pre-fill input if QID exists
  var inputQid = document.getElementById('input-qid');
  if(inputQid && questionarioId) {
    inputQid.value = questionarioId;
  }

  // Se o QID veio via URL (pesquisador abriu o link), pula identificação
  // e vai direto para a oferta buscando o status no backend
  if(qidFromUrl && questionarioId) {
    var qid = parseInt(questionarioId, 10);
    // Mostra loading na tela de identificação
    var identSection = document.getElementById('sec-ident');
    if(identSection) {
      identSection.innerHTML = '<div style="padding:40px;text-align:center;color:var(--ink-soft);font-size:.9rem;">Carregando...</div>';
    }
    fetch(NAO_API + '/questionario/lista')
      .then(function(r){ return r.json(); })
      .then(function(data){
        var q = null;
        if(data.questionarios) {
          for(var i=0; i<data.questionarios.length; i++) {
            if(data.questionarios[i].id === qid) { q = data.questionarios[i]; break; }
          }
        }
        if(q && (q.status === 'jogo_concluido' || q.status === 'aguardando' || q.status === 'em_jogo')) {
          questionarioId = qid;
          sessionId = q.session_id;
          var offerLabel = document.getElementById('offer-participant-label');
          if(offerLabel) offerLabel.textContent = 'Q' + questionarioId;
          showSection('sec-offer');
        } else {
          // Mostra identificação normal em caso de status inesperado
          if(identSection) identSection.innerHTML = '';
          showSection('sec-ident');
        }
      })
      .catch(function(){
        // Em caso de falha, mostra tela de identificação normal
        showSection('sec-ident');
      });
  }

  // Fetch API to check QID status (tela de identificação manual)
  var btnBuscar = document.getElementById('btn-buscar-qid');
  if(btnBuscar) {
    btnBuscar.addEventListener('click', function(){
      var qid = parseInt(inputQid.value, 10);
      var valIdent = document.getElementById('val-ident');
      if(!qid || isNaN(qid)) {
        valIdent.textContent = 'Insira um código válido.';
        valIdent.style.display = 'flex';
        return;
      }
      
      btnBuscar.disabled = true;
      btnBuscar.textContent = 'Buscando...';
      
      fetch(NAO_API + '/questionario/lista')
        .then(r => r.json())
        .then(data => {
           btnBuscar.disabled = false;
           btnBuscar.textContent = 'Continuar';
           
           var q = null;
           if(data.questionarios) {
             for(var i=0; i<data.questionarios.length; i++) {
               if(data.questionarios[i].id === qid) { q = data.questionarios[i]; break; }
             }
           }
           
           if(!q) {
             valIdent.textContent = 'Código Q' + qid + ' não encontrado.';
             valIdent.style.display = 'flex';
             return;
           }
           if(q.status === 'aguardando') {
             valIdent.textContent = 'Este participante ainda não iniciou o jogo.';
             valIdent.style.display = 'flex';
             return;
           }
           if(q.status === 'em_jogo') {
             valIdent.textContent = 'O jogo deste participante ainda está em andamento.';
             valIdent.style.display = 'flex';
             return;
           }
           if(q.status === 'completo') {
             valIdent.textContent = 'Este participante já respondeu o pós-questionário.';
             valIdent.style.display = 'flex';
             return;
           }
           if(q.status === 'desistiu') {
             valIdent.textContent = 'Este participante optou por não responder.';
             valIdent.style.display = 'flex';
             return;
           }
           
           // If 'jogo_concluido':
           questionarioId = qid;
           sessionId = q.session_id;
           valIdent.style.display = 'none';
           
           var offerLabel = document.getElementById('offer-participant-label');
           if(offerLabel) offerLabel.textContent = 'Q' + questionarioId;
           
           showSection('sec-offer');
        })
        .catch(err => {
           btnBuscar.disabled = false;
           btnBuscar.textContent = 'Continuar';
           valIdent.textContent = 'Erro ao conectar com o servidor.';
           valIdent.style.display = 'flex';
        });
    });
  }

  // Offer screen
  var btnAccept = document.getElementById('btn-accept-pos');
  if(btnAccept) {
    btnAccept.addEventListener('click', function(){
      showSection('sec-pos-1');
    });
  }

  var btnDecline = document.getElementById('btn-decline-pos');
  if(btnDecline) {
    btnDecline.addEventListener('click', function(){
      if(confirm('Tem certeza que não deseja responder o pós-questionário?')) {
        fetch(NAO_API + '/questionario/desistir', {
          method: 'POST', headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({questionario_id: questionarioId})
        }).catch(function(){});
        localStorage.removeItem('questionario_id');
        showSection('sec-declined');
      }
    });
  }

  // Likert generation
  var likertItems = [
    {id: 'mudancas_nao', txt: 'Percebi mudanças claras na forma como o NAO se comportou e falou ao longo das rodadas.'},
    {id: 'nao_amigavel', txt: 'Em algum momento, achei que o NAO estava sendo amigável e parceiro.'},
    {id: 'nao_competitivo', txt: 'Em algum momento, o NAO me pareceu competitivo, querendo ganhar de mim.'},
    {id: 'nao_vitimizacao', txt: 'Senti que o NAO demonstrou tristeza ou decepção quando eu não cooperei com ele.'},
    {id: 'nao_neutro', txt: 'Achei que o NAO foi indiferente e neutro, não demonstrando emoção nas jogadas.'}
  ];
  var likertGroup = document.getElementById('pos-likert-group');
  if(likertGroup){
    likertItems.forEach(function(item){
      var html = '<div class=likert-item><div class=likert-stat>'+item.txt+'</div><div class=likert-opts>';
      for(var i=1; i<=5; i++){
        html += '<label class=likert-opt><input type=radio name='+item.id+' value='+i+'><div class=likert-bubble></div></label>';
      }
      html += '</div></div>';
      likertGroup.innerHTML += html;
    });
  }

  var btnPos1Next = document.getElementById('btn-pos-1-next');
  if(btnPos1Next) {
    btnPos1Next.addEventListener('click', function(){
      var isValid = true;
      likertItems.forEach(function(item){
        if(!document.querySelector('input[name='+item.id+']:checked')) isValid = false;
      });
      if(isValid) {
        document.getElementById('val-pos-1').style.display = 'none';
        showSection('sec-pos-2');
      } else {
        document.getElementById('val-pos-1').style.display = 'flex';
      }
    });
  }

  var btnPos2Back = document.getElementById('btn-pos-2-back');
  if(btnPos2Back) { btnPos2Back.addEventListener('click', function(){ showSection('sec-pos-1'); }); }

  var gsPairs = [['Falso', 'Genuíno'],['Artificial', 'Natural'],['Mecânico', 'Orgânico'],['Inanimado', 'Vivo'],['Rígido', 'Elegante']];
  var gsPosTbody = document.getElementById('gs-pos-tbody');
  if(gsPosTbody){
    gsPairs.forEach(function(p, i){
      var n = i+1;
      var html = '<tr><td class=th-left><div class=gs-label>'+p[0]+'</div></td>';
      ['A','2','3','4','E'].forEach(function(val, j){
        html += '<td><label class=gs-opt><input type=radio name=gs_pos_'+n+' value='+(j+1)+'><div class=gs-bubble></div></label></td>';
      });
      html += '<td class=th-right><div class=gs-label>'+p[1]+'</div></td></tr>';
      gsPosTbody.innerHTML += html;
    });
  }

  var btnPos2Submit = document.getElementById('btn-pos-2-submit');
  if(btnPos2Submit) {
    btnPos2Submit.addEventListener('click', function(){
      var isValid = true;
      for(var i=1; i<=5; i++){
        if(!document.querySelector('input[name=gs_pos_'+i+']:checked')) isValid = false;
      }
      if(!isValid) {
        document.getElementById('val-pos-2').style.display = 'flex';
        return;
      }
      document.getElementById('val-pos-2').style.display = 'none';
      btnPos2Submit.disabled = true;
      btnPos2Submit.textContent = 'Enviando...';

      var payload = { questionario_id: questionarioId, session_id: sessionId };
      likertItems.forEach(function(item){
        payload[item.id] = parseInt(document.querySelector('input[name='+item.id+']:checked').value, 10);
      });
      for(var i=1; i<=5; i++){
        payload['godspeed_pos_'+i] = parseInt(document.querySelector('input[name=gs_pos_'+i+']:checked').value, 10);
      }

      fetch(NAO_API + '/questionario/pos', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      .then(r => { if(!r.ok) throw new Error(); return r.json(); })
      .then(data => {
        localStorage.removeItem('questionario_id');
        showSection('sec-done');
      })
      .catch(err => {
        alert('Erro ao enviar questionário. Verifique o servidor.');
        btnPos2Submit.disabled = false;
        btnPos2Submit.textContent = 'Enviar Respostas';
      });
    });
  }

})();
