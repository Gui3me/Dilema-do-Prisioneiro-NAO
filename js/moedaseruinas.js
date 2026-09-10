(function(){
  "use strict";

  /* ---------- SVG Icons ---------- */
  var svgCooperate = '<svg viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>';
  var svgNeutral   = '<svg viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>';
  var svgBetray    = '<svg viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>';
  var svgCoin      = '<svg viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><path d="M12 8v8"></path><path d="M10 10h4"></path><path d="M10 14h4"></path></svg>';
  var svgRuin      = '<svg viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M3 21h18"></path><path d="M5 21V8l7-5 7 5v13"></path><path d="M9 21v-4"></path><path d="M15 21v-4"></path><path d="M7 11h2"></path><path d="M15 11h2"></path></svg>';
  var svgStar      = '<svg viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>';

  /* ---------- Ambient dust ---------- */
  var ambient = document.getElementById('ambient');
  for(var i = 0; i < 14; i++){
    var m = document.createElement('span');
    m.className = 'mote';
    var size = 4 + Math.random() * 10;
    m.style.width  = size + 'px';
    m.style.height = size + 'px';
    m.style.left   = Math.random() * 100 + '%';
    m.style.top    = 60 + Math.random() * 40 + '%';
    m.style.animationDuration = (10 + Math.random() * 14) + 's';
    m.style.animationDelay    = (Math.random() * 10) + 's';
    ambient.appendChild(m);
  }

  /* ---------- Font Scale ---------- */
  var fontScales = [0.85, 1.0, 1.15, 1.3];
  var fontLabels = ['A--', 'Aa', 'A+', 'A++'];
  var fontIdx    = 1;
  var fontDecBtn = document.getElementById('font-decrease');
  var fontIncBtn = document.getElementById('font-increase');
  var fontLabel  = document.getElementById('font-scale-label');

  function applyFontScale(){
    document.documentElement.style.setProperty('--font-scale', fontScales[fontIdx]);
    fontLabel.textContent = fontLabels[fontIdx];
    fontDecBtn.disabled = fontIdx === 0;
    fontIncBtn.disabled = fontIdx === fontScales.length - 1;
  }
  fontDecBtn.addEventListener('click', function(){ if(fontIdx > 0){ fontIdx--; applyFontScale(); } });
  fontIncBtn.addEventListener('click', function(){ if(fontIdx < fontScales.length - 1){ fontIdx++; applyFontScale(); } });
  applyFontScale();

  /* ---------- Theme ---------- */
  var themeToggleBtn = document.getElementById('theme-toggle');
  var themeIcon      = document.getElementById('theme-icon');
  var svgMoon = '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>';
  var svgSun  = '<circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>';

  function applyTheme(isDark){
    var bgFrame = document.getElementById('bg-frame');
    if(isDark){
      document.documentElement.setAttribute('data-theme', 'dark');
      if(bgFrame) bgFrame.src = 'Assets/BackgroundDark/frame_001.jpg';
      themeIcon.innerHTML = svgSun;
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.removeAttribute('data-theme');
      if(bgFrame) bgFrame.src = 'Assets/Background/frame_001.jpg';
      themeIcon.innerHTML = svgMoon;
      localStorage.setItem('theme', 'light');
    }
  }

  function setTheme(isDark){
    var overlay = document.getElementById('theme-transition-overlay');
    var sun = document.getElementById('anim-sun');
    var moon = document.getElementById('anim-moon');
    
    // Cor da cortina: preto para dark, branco para light
    overlay.style.background = isDark ? '#1A1815' : '#F7F4EE';
    
    // Cores dos ícones
    sun.style.color = isDark ? '#F9E596' : '#D6A848';
    moon.style.color = isDark ? '#F7F4EE' : '#332F2A';

    // Remove animações antigas para resetar posições instantaneamente
    sun.style.transition = 'none';
    moon.style.transition = 'none';
    
    // Posições iniciais: o ativo atual começa no centro (0) e vai descer (150%).
    // O que vai entrar começa em cima (-150%) e vai descer pro centro (0).
    if (isDark) {
      // Claro -> Escuro: Sol se põe (desce), Lua desce de cima
      sun.style.transform = 'translateY(0)';
      moon.style.transform = 'translateY(-150%)';
    } else {
      // Escuro -> Claro: Lua se põe (desce), Sol desce de cima
      moon.style.transform = 'translateY(0)';
      sun.style.transform = 'translateY(-150%)';
    }
    
    // Fade in da cortina
    overlay.classList.add('visible');

    // Espera a cortina ficar visível (280ms) e então inicia as animações dos SVGs
    setTimeout(function(){
      // Adiciona curva de aceleração suave para o movimento
      var ease = 'transform 0.6s cubic-bezier(0.34, 1.56, 0.64, 1)';
      sun.style.transition = ease;
      moon.style.transition = ease;
      
      if (isDark) {
        sun.style.transform = 'translateY(150%)'; // Sol vai para baixo
        moon.style.transform = 'translateY(0)'; // Lua vem pro centro
      } else {
        moon.style.transform = 'translateY(150%)'; // Lua vai para baixo
        sun.style.transform = 'translateY(0)'; // Sol vem pro centro
      }
    }, 280);

    // Após terminar a animação dos ícones, aplica o tema real por trás e faz fade out da cortina
    // Cortina: 280ms + SVGs: 600ms = 880ms. Esperamos ~900ms.
    setTimeout(function(){
      applyTheme(isDark);
      overlay.classList.remove('visible');
    }, 950);
  }

  themeToggleBtn.addEventListener('click', function(){
    setTheme(!document.documentElement.hasAttribute('data-theme'));
  });
  var subtitlesEnabled = localStorage.getItem('subtitles') === 'true';
  var subtitleToggleBtn = document.getElementById('subtitles-toggle');
  
  function updateSubtitleBtn() {
    if (subtitleToggleBtn) {
      if (subtitlesEnabled) {
        subtitleToggleBtn.style.color = 'var(--gold-deep)';
        subtitleToggleBtn.style.background = 'var(--gold-soft)';
      } else {
        subtitleToggleBtn.style.color = '';
        subtitleToggleBtn.style.background = '';
      }
    }
  }
  
  if (subtitleToggleBtn) {
    subtitleToggleBtn.addEventListener('click', function() {
      subtitlesEnabled = !subtitlesEnabled;
      localStorage.setItem('subtitles', subtitlesEnabled);
      updateSubtitleBtn();
    });
    updateSubtitleBtn();
  }

  var savedTheme = localStorage.getItem('theme');
  if(savedTheme === 'dark' || (!savedTheme && window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches)){
    setTheme(true);
  } else {
    setTheme(false);
  }

  /* ---------- NAO API ---------- */
  var storedIp = localStorage.getItem('nao_ip') || '10.43.151.105';
  var NAO_API  = 'http://' + storedIp + ':5050';

  /* ---------- Screen navigation ---------- */
  var screens = Array.prototype.slice.call(document.querySelectorAll('.screen'));
  function showScreen(id){
    screens.forEach(function(s){ s.classList.remove('active'); });
    document.getElementById(id).classList.add('active');
    var panel = document.getElementById('rules-panel');
    if(panel){ panel.classList.toggle('visible', id === 'screen-game'); }
  }

  document.getElementById('btn-jogar').addEventListener('click',    function(){ showScreen('screen-story'); });
  document.getElementById('btn-continuar').addEventListener('click', function(){ showScreen('screen-rules'); });
  document.getElementById('btn-comecar').addEventListener('click',   function(){ startGame(); });

  /* ---------- Game state ---------- */
  var MAX_ROUNDS = 5;
  var state = { round: 1, youCoins: 0, naoCoins: 0, gameFim: false };

  var youCoinsEl     = document.getElementById('you-coins');
  var naoCoinsEl     = document.getElementById('nao-coins');
  var youCoinCountEl = document.getElementById('you-coin-count');
  var naoCoinCountEl = document.getElementById('nao-coin-count');
  var promptText     = document.getElementById('prompt-text');
  var btnCooperate   = document.getElementById('btn-cooperate');
  var btnBetray      = document.getElementById('btn-betray');
  var treasureFill   = document.getElementById('treasure-fill');

  function updateTreasureBar(stonesLeft){
    treasureFill.style.width = ((stonesLeft / MAX_ROUNDS) * 100) + '%';
  }

  var _jogoStartTime = null;
  function startGame(){
    _jogoStartTime = Date.now();
    state = { round: 1, youCoins: 0, naoCoins: 0, gameFim: false };
    updateTreasureBar(MAX_ROUNDS);
    updateCoinDisplay(true);
    resetRoundUI();
    showScreen('screen-game');
  }

  function resetRoundUI(){
    promptText.textContent = 'FAÇA SUA ESCOLHA';
    promptText.classList.remove('waiting');
    btnCooperate.disabled = false;
    btnBetray.disabled    = false;
    btnCooperate.classList.remove('selected');
    btnBetray.classList.remove('selected');
  }

  function updateCoinDisplay(instant){
    youCoinsEl.textContent = state.youCoins;
    naoCoinsEl.textContent = state.naoCoins;
    if(!instant){
      youCoinCountEl.classList.remove('pop'); void youCoinCountEl.offsetWidth; youCoinCountEl.classList.add('pop');
      naoCoinCountEl.classList.remove('pop'); void naoCoinCountEl.offsetWidth; naoCoinCountEl.classList.add('pop');
    }
  }

  btnCooperate.addEventListener('click', function(){ handleChoice(0); });
  btnBetray.addEventListener('click',    function(){ handleChoice(1); });

  var _enviando = false;
  function handleChoice(escolha){
    if(_enviando) return;
    _enviando = true;
    btnCooperate.disabled = true;
    btnBetray.disabled    = true;
    (escolha === 0 ? btnCooperate : btnBetray).classList.add('selected');
    promptText.textContent = 'Aguardando decisão do NAO…';
    promptText.classList.add('waiting');

    fetch(NAO_API + '/jogada', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ escolha: escolha })
    })
    .then(function(r){
      if(!r.ok) return r.json().then(function(err){ throw new Error(err.erro || 'HTTP ' + r.status); });
      return r.json();
    })
    .then(function(data){
      _enviando = false;
      resolveRound(data);
    })
    .catch(function(err){
      _enviando = false;
      console.warn('[JOGADA] Erro:', err.message);
      promptText.textContent = '⚠ Erro: ' + err.message + ' — Tente novamente';
      promptText.classList.remove('waiting');
      btnCooperate.disabled = false;
      btnBetray.disabled    = false;
      btnCooperate.classList.remove('selected');
      btnBetray.classList.remove('selected');
    });
  }

  function resolveRound(data){
    var s  = data.ultimo_resultado;
    var dj = data.ultimo_delta_jogador;
    var dn = data.ultimo_delta_nao;
    var fala = data.ultima_fala || '';

    state.youCoins = data.moedas_jogador;
    state.naoCoins = data.moedas_nao;
    state.round    = data.rodada;
    state.gameFim  = data.fase === 'fim';

    var title, desc, iconClass, iconGlyph;
    if(s === 0){
      title = 'NAO cooperou com você!';
      desc  = 'Ambos dividiram o tesouro igualmente. Cada um ganhou duas moedas.';
      iconClass = 'mi-cooperate'; iconGlyph = svgCooperate;
    } else if(s === 1){
      title = 'Você trapaceou o NAO!';
      desc  = 'Enquanto o NAO dividia, você ficou com a maior parte do tesouro.';
      iconClass = 'mi-cooperate'; iconGlyph = svgCoin;
    } else if(s === 2){
      title = 'NAO traiu você!';
      desc  = 'Enquanto você dividia, o NAO ficou com a maior parte do tesouro.';
      iconClass = 'mi-betray'; iconGlyph = svgBetray;
    } else {
      title = 'NAO também trapaceou!';
      desc  = 'Ambos tentaram levar tudo. Ninguém ganhou moedas desta vez.';
      iconClass = 'mi-neutral'; iconGlyph = svgNeutral;
    }

    showModal(title, desc, iconClass, iconGlyph, dj, dn, fala);
  }

  /* ---------- Modal ---------- */
  var modalOverlay = document.getElementById('modal-overlay');
  var modalIcon    = document.getElementById('modal-icon');
  var modalTitle   = document.getElementById('modal-title');
  var modalDesc    = document.getElementById('modal-desc');
  var modalCoins   = document.getElementById('modal-coins');
  var modalOk      = document.getElementById('modal-ok');
  var modalCountdownInterval;

  function fmtDelta(n){ return (n > 0 ? '+' : '') + n; }

  function showModal(title, desc, iconClass, iconGlyph, youDelta, naoDelta, fala){
    modalIcon.className    = 'modal-icon ' + iconClass;
    modalIcon.innerHTML    = iconGlyph;
    modalTitle.textContent = title;
    modalDesc.textContent  = desc;
    modalCoins.innerHTML   =
      '<span>Você <b>' + fmtDelta(youDelta) + '</b></span>' +
      '<span>NAO <b>'  + fmtDelta(naoDelta) + '</b></span>';
      
    var subtitleEl = document.getElementById('modal-subtitle');
    if (subtitleEl) {
      if (subtitlesEnabled && fala && fala.trim() !== '') {
        subtitleEl.style.display = 'block';
        subtitleEl.innerHTML = '<strong>NAO diz:</strong> ' + fala;
      } else {
        subtitleEl.style.display = 'none';
        subtitleEl.innerHTML = '';
      }
    }

    // Countdown 8s para aguardar o NAO falar
    modalOk.disabled = true;
    var waitSecs = 8;
    modalOk.textContent = 'Aguarde o NAO (' + waitSecs + 's)';
    clearInterval(modalCountdownInterval);
    modalCountdownInterval = setInterval(function(){
      waitSecs--;
      if(waitSecs <= 0){
        clearInterval(modalCountdownInterval);
        modalOk.textContent = 'Continuar';
        modalOk.disabled = false;
      } else {
        modalOk.textContent = 'Aguarde o NAO (' + waitSecs + 's)';
      }
    }, 1000);

    modalOverlay.classList.add('open');
  }

  modalOk.addEventListener('click', function(){
    modalOverlay.classList.remove('open');
    updateCoinDisplay(false);

    setTimeout(function(){
      if(state.gameFim){
        updateTreasureBar(0);
        triggerCollapseAnimation(function(){ endGame(); });
      } else {
        updateTreasureBar(MAX_ROUNDS - state.round + 1);
        resetRoundUI();
      }
    }, 350);
  });

  /* ---------- Collapse Animation (image frames + SVG fallback) ---------- */
  function triggerCollapseAnimation(callback){
    var bgFrame   = document.getElementById('bg-frame');
    var svgOverlay = document.getElementById('castle-collapse-overlay');
    var frame     = 1;
    var maxFrames = 50;
    var bgFolder = document.documentElement.hasAttribute('data-theme') ? 'Assets/BackgroundDark' : 'Assets/Background';

    // Test if image frames exist
    var testImg = new Image();
    testImg.onload = function(){
      // Frames available — play image animation (v21 style)
      svgOverlay.style.display = 'none';
      var interval = setInterval(function(){
        frame++;
        bgFrame.src = bgFolder + '/frame_' + String(frame).padStart(3,'0') + '.jpg';
        if(frame >= maxFrames){
          clearInterval(interval);
          setTimeout(callback, 500);
        }
      }, 1000 / 24);
    };
    testImg.onerror = function(){
      // Fallback: SVG collapse animation
      svgOverlay.style.display = '';
      triggerSVGCollapse(callback);
    };
    testImg.src = bgFolder + '/frame_002.jpg';
  }

  function triggerSVGCollapse(callback){
    var overlay = document.getElementById('castle-collapse-overlay');
    // Hide static bg
    var bgContainer = document.querySelector('.bg-anim-container');
    if(bgContainer){ bgContainer.style.opacity='0'; bgContainer.style.transition='opacity 0.4s ease'; }

    overlay.classList.add('show');

    var pieces = overlay.querySelectorAll('.castle-piece');
    var delays = [0, 180, 180, 100, 100];
    pieces.forEach(function(piece, idx){
      setTimeout(function(){ piece.classList.add('crumble'); }, delays[idx] || 0);
    });

    var dusts = overlay.querySelectorAll('.castle-dust');
    dusts.forEach(function(d, idx){
      setTimeout(function(){
        d.style.animationName = 'none';
        void d.offsetWidth;
        d.style.animation = 'dust-expand 1.4s ease-out ' + (0.4 + idx*0.1) + 's forwards';
      }, 400);
    });

    document.getElementById('app').style.animation = 'screen-shake 0.5s ease 0.3s';

    setTimeout(function(){
      overlay.style.opacity = '0';
      overlay.style.transition = 'opacity 0.8s ease';
      setTimeout(function(){
        overlay.classList.remove('show');
        overlay.style.transition = '';
        overlay.style.opacity = '';
        if(bgContainer){ bgContainer.style.opacity=''; bgContainer.style.transition=''; }
        pieces.forEach(function(p){ p.classList.remove('crumble'); });
        if(callback) callback();
      }, 900);
    }, 1800);
  }

  // Screen shake keyframe
  var shakeStyle = document.createElement('style');
  shakeStyle.textContent = '@keyframes screen-shake{' +
    '0%{transform:translate(0,0);}15%{transform:translate(-6px,3px);}' +
    '30%{transform:translate(6px,-3px);}45%{transform:translate(-4px,2px);}' +
    '60%{transform:translate(4px,-2px);}75%{transform:translate(-2px,1px);}' +
    '100%{transform:translate(0,0);}}';
  document.head.appendChild(shakeStyle);

  /* ---------- End Screen ---------- */
  var endCard = document.getElementById('end-card');

  function endGame(){
    var you = state.youCoins, nao = state.naoCoins;
    var badgeClass, glyph, title, desc;

    if(you < nao){
      badgeClass='lose'; glyph=svgRuin;
      title='O castelo desabou…';
      desc='Vocês escaparam, mas o NAO conseguiu mais moedas. Desta vez, você perdeu.';
    } else if(you > nao){
      badgeClass='mal'; glyph=svgCoin;
      title='O castelo desabou…';
      desc='Vocês escaparam e você conseguiu mais moedas. Você venceu — mas a que custo?';
    } else {
      badgeClass='bom'; glyph=svgStar;
      title='O castelo desabou…';
      desc='Vocês escaparam e dividiram o tesouro com justiça. Parabéns!';
    }

    endCard.innerHTML =
      '<div class="end-badge ' + badgeClass + '">' + glyph + '</div>' +
      '<h2 class="title-lg">' + title + '</h2>' +
      '<p class="body-text" style="text-align:center;">' + desc + '</p>' +
      '<div class="final-tally">' +
        '<div class="fp"><div class="lbl">NAO</div><div class="val"><span class="coin-icon"></span>' + nao + '</div></div>' +
        '<div class="fp"><div class="lbl">Você</div><div class="val">' + you + '<span class="coin-icon"></span></div></div>' +
      '</div>' +
      '<div class="cta-row"><button class="btn btn-primary" id="btn-restart">Chamar o pesquisador</button></div>';

    // Save game time to localStorage
    if(_jogoStartTime) {
      var tempoJogoSeg = Math.round((Date.now() - _jogoStartTime) / 1000);
      localStorage.setItem('tempo_jogo_segundos', tempoJogoSeg);
      _jogoStartTime = null;
    }
    showScreen('screen-end');

    document.getElementById('btn-restart').addEventListener('click', function(){
      var overlay = document.getElementById('researcher-overlay');
      var fillBar = document.getElementById('researcher-progress-fill');

      fillBar.style.transition = 'none';
      fillBar.style.width = '0%';
      overlay.classList.add('active');

      setTimeout(function(){
        fillBar.style.transition = 'width 2.3s linear';
        fillBar.style.width = '100%';
      }, 60);

      function dismissResearcher(){
        overlay.classList.remove('active');
        fetch(NAO_API + '/reiniciar', { method: 'POST' }).catch(function(){});
        setTimeout(function(){
          fillBar.style.transition = 'none';
          fillBar.style.width = '0%';
          
          var bgFrame = document.getElementById('bg-frame');
          if (bgFrame) {
            var bgFolder = document.documentElement.hasAttribute('data-theme') ? 'Assets/BackgroundDark' : 'Assets/Background';
            bgFrame.src = bgFolder + '/frame_001.jpg';
          }
          
          showScreen('screen-splash');
        }, 480);
        overlay.removeEventListener('click', dismissResearcher);
        document.removeEventListener('keydown', escHandler);
      }
      function escHandler(e){ if(e.key === 'Escape') dismissResearcher(); }
      overlay.addEventListener('click', dismissResearcher);
      document.addEventListener('keydown', escHandler);
    });
  }

  /* ---------- Emergency interrupt polling (a cada 2s) ---------- */
  setInterval(function(){
    fetch(NAO_API + '/estado')
    .then(function(r){ return r.json(); })
    .then(function(data){
      var splash = document.getElementById('screen-splash');
      var overlay = document.getElementById('researcher-overlay');
      var isLoadingResearcher = overlay && overlay.classList.contains('active');
      if(data.fase === 'aguardando_personalidade' && !splash.classList.contains('active') && !isLoadingResearcher){
        var bgFrame = document.getElementById('bg-frame');
        if (bgFrame) {
          var bgFolder = document.documentElement.hasAttribute('data-theme') ? 'Assets/BackgroundDark' : 'Assets/Background';
          bgFrame.src = bgFolder + '/frame_001.jpg';
        }
        showScreen('screen-splash');
        _enviando = false;
        alert('A sessão foi interrompida pelo pesquisador.');
      }
    }).catch(function(){});
  }, 2000);

  /* ---------- Atalho secreto: Shift+E → ver animação de fim ---------- */
  document.addEventListener('keydown', function(e){
    if(e.key === 'E' && e.shiftKey){
      var modal = document.getElementById('modal-overlay');
      if(modal.classList.contains('open')){
        clearInterval(modalCountdownInterval);
        modal.classList.remove('open');
      }
      state.gameFim = true;
      updateTreasureBar(0);
      triggerCollapseAnimation(function(){ endGame(); });
    }
  });

})();
