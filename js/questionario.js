(function(){
  var urlParams = new URLSearchParams(window.location.search);
  var storedIp = urlParams.get('ip') || localStorage.getItem('nao_ip') || '10.43.151.105';
  localStorage.setItem('nao_ip', storedIp);
  var NAO_API = 'http://' + storedIp + ':5050';

  var currentSection = 1;
  var TOTAL_SECTIONS = 5;
  var participantId = null;

  var progressLabel = document.getElementById('progress-label');
  var progressFrac  = document.getElementById('progress-frac');
  var progressFill  = document.getElementById('progress-fill');

  function updateProgress() {
    var pct = Math.round(((currentSection - 1) / (TOTAL_SECTIONS - 1)) * 100);
    if(progressLabel) progressLabel.textContent = 'Se\u00e7\u00e3o ' + currentSection + ' de ' + TOTAL_SECTIONS;
    if(progressFrac) progressFrac.textContent = pct + '%';
    if(progressFill) progressFill.style.width = pct + '%';
    if(currentSection === TOTAL_SECTIONS) {
      var wrap = document.getElementById('progress-wrap');
      if(wrap) wrap.style.display = 'none';
    }
  }

  function showSection(num) {
    document.querySelectorAll('.q-section').forEach(function(sec){ sec.classList.remove('active'); });
    var s = document.getElementById('sec-' + num);
    if(s) s.classList.add('active');
    currentSection = num;
    updateProgress();
    window.scrollTo(0,0);
  }

  for(let i=1; i<=4; i++) {
    var btnNext = document.getElementById('btn-'+i+'-next');
    var btnBack = document.getElementById('btn-'+i+'-back');
    if(btnNext) {
      btnNext.addEventListener('click', (function(idx){
        return function(){
          if(validateSection(idx)) {
            var val = document.getElementById('val-'+idx);
            if(val) val.style.display = 'none';
            showSection(idx+1);
          } else {
            var val = document.getElementById('val-'+idx);
            if(val) val.style.display = 'flex';
          }
        };
      })(i));
    }
    if(btnBack) {
      btnBack.addEventListener('click', (function(idx){
        return function(){ showSection(idx-1); };
      })(i));
    }
  }

  // Escala de botoes visuais 1-5 (horizontal)
  function createScale(containerId, name) {
    var cont = document.getElementById(containerId);
    if(!cont) return;
    var html = '';
    for(var i=1; i<=5; i++){
      html += '<button type="button" class="scale-btn" data-name="' + name + '" data-value="' + i + '">' + i + '</button>';
    }
    cont.innerHTML = html;
    cont.querySelectorAll('.scale-btn').forEach(function(btn){
      btn.addEventListener('click', function(){
        var n = btn.getAttribute('data-name');
        cont.querySelectorAll('.scale-btn[data-name="' + n + '"]').forEach(function(b){ b.classList.remove('selected'); });
        btn.classList.add('selected');
      });
    });
  }
  createScale('scale-jogos', 'freq_jogos');
  createScale('scale-robos', 'contato_robos');
  createScale('scale-dilema', 'conhecimento_dilema');

  // GodSpeed table pre
  var gsPairs = [['Falso', 'Genu\u00edno'],['Artificial', 'Natural'],['Mec\u00e2nico', 'Org\u00e2nico'],['Inanimado', 'Vivo'],['R\u00edgido', 'Elegante']];
  var gsTbody = document.getElementById('gs-tbody');
  if(gsTbody){
    gsPairs.forEach(function(p, i){
      var n = i+1;
      var html = '<tr><td class="th-left"><div class="gs-label">' + p[0] + '</div></td>';
      ['A','2','3','4','E'].forEach(function(val, j){
        html += '<td><label class="gs-opt"><input type="radio" name="gs_pre_' + n + '" value="' + (j+1) + '"><div class="gs-bubble"></div></label></td>';
      });
      html += '<td class="th-right"><div class="gs-label">' + p[1] + '</div></td></tr>';
      gsTbody.innerHTML += html;
    });
  }

  function getScaleValue(name) {
    var btn = document.querySelector('.scale-btn[data-name="' + name + '"].selected');
    return btn ? parseInt(btn.getAttribute('data-value'), 10) : null;
  }

  function validateSection(num) {
    if(num === 1) {
      var consent = document.querySelector('input[name="consentimento"]:checked');
      if(!consent) return false;
      if(consent.value === 'no') {
        if(confirm('Tem certeza que n\u00e3o deseja participar da pesquisa? O jogo ser\u00e1 liberado sem coleta de dados.')) {
          fetch(NAO_API + '/questionario/nao-participante', {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({session_id: null})
          }).catch(function(){});
          document.body.innerHTML = '<div style="padding:40px;text-align:center;font-family:sans-serif;"><h3>Obrigado!</h3><p>O pesquisador iniciar\u00e1 o jogo em instantes.</p></div>';
        }
        return false;
      }
      return true;
    }
    if(num === 2) {
      if(!document.querySelector('input[name="genero"]:checked') ||
         !document.querySelector('input[name="idade"]:checked') ||
         !document.querySelector('input[name="escolaridade"]:checked')) return false;
      return true;
    }
    if(num === 3) {
      if(getScaleValue('freq_jogos') === null ||
         getScaleValue('contato_robos') === null ||
         getScaleValue('conhecimento_dilema') === null) return false;
      return true;
    }
    if(num === 4) {
      for(var i=1; i<=5; i++) {
        if(!document.querySelector('input[name="gs_pre_'+i+'"]:checked')) return false;
      }
      return true;
    }
    return true;
  }

  var btnSubmit = document.getElementById('btn-4-submit');
  if(btnSubmit) {
    btnSubmit.addEventListener('click', function(){
      if(!validateSection(4)) {
        var val = document.getElementById('val-4');
        if(val) val.style.display = 'flex';
        return;
      }
      btnSubmit.disabled = true;
      btnSubmit.textContent = 'Enviando...';

      var payload = {
        genero: document.querySelector('input[name="genero"]:checked').value,
        idade: document.querySelector('input[name="idade"]:checked').value,
        escolaridade: document.querySelector('input[name="escolaridade"]:checked').value,
        freq_jogos: getScaleValue('freq_jogos'),
        contato_robos: getScaleValue('contato_robos'),
        conhecimento_dilema: getScaleValue('conhecimento_dilema')
      };
      for(var i=1; i<=5; i++) payload['godspeed_'+i] = parseInt(document.querySelector('input[name="gs_pre_'+i+'"]:checked').value, 10);

      var settled = false;
      var timeout = setTimeout(function(){
        if(settled) return;
        settled = true;
        usarFallbackOffline(payload);
      }, 8000);

      fetch(NAO_API + '/questionario/pre', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      .then(function(r){
        if(settled) return null;
        if(!r.ok) throw new Error('Network error');
        return r.json();
      })
      .then(function(data){
        if(settled || !data) return;
        settled = true;
        clearTimeout(timeout);
        participantId = data.questionario_id;
        localStorage.setItem('questionario_id', participantId);
        document.getElementById('waiting-id-display').textContent = 'Q' + participantId;
        showSection(5);
      })
      .catch(function(){
        if(settled) return;
        settled = true;
        clearTimeout(timeout);
        usarFallbackOffline(payload);
      });
    });
  }

  function usarFallbackOffline(payload) {
    var localId = 'L' + Date.now().toString().slice(-5);
    participantId = localId;
    localStorage.setItem('questionario_id', localId);
    localStorage.setItem('pre_payload_offline', JSON.stringify(payload));
    var display = document.getElementById('waiting-id-display');
    if(display) display.textContent = localId;
    var badge = document.getElementById('waiting-id-badge');
    if(badge) {
      var note = document.createElement('div');
      note.style.cssText = 'font-size:.7rem;color:#8C2B26;margin-top:8px;font-weight:600;';
      note.textContent = 'Sem conex\u00e3o com backend - dado salvo localmente';
      badge.appendChild(note);
    }
    showSection(5);
  }

  var btnNovoPre = document.getElementById('btn-novo-pre');
  if(btnNovoPre) { btnNovoPre.addEventListener('click', function() { window.location.reload(); }); }

  var btnIrPos = document.getElementById('btn-ir-pos');
  if(btnIrPos) { btnIrPos.addEventListener('click', function() { window.location.href = 'posquestionario.html'; }); }

})();
