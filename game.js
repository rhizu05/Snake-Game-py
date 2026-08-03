(function () {
  'use strict';

  // === Konfigurasi & konstanta (paritas main.py) ===
  var WIDTH = 800;
  var HEIGHT = 600;
  var BORDER = 10;
  var BLOCK = 20;
  var INITIAL_SPEED = 10;

  var COLOR_WHITE = '#ffffff';
  var COLOR_BLACK = '#000000';
  var COLOR_RED = '#d53250';
  var COLOR_GREEN = '#00ff00';
  var COLOR_YELLOW = '#dfb152';
  var COLOR_BG = '#15690a';

  var canvas = document.getElementById('game');
  var ctx = canvas.getContext('2d');

  // === Gambar latar belakang ===
  var bgStart = new Image();
  bgStart.src = 'resource/images/bg-start.png';
  var bgOver = new Image();
  bgOver.src = 'resource/images/bg-over.png';
  var loadingImg = new Image();
  loadingImg.src = 'resource/images/loading.png';
  var logoImg = new Image();
  logoImg.src = 'resource/images/logo-putih-ITG.png';

  // === Audio (WebAudio, lazy setelah interaksi pengguna) ===
  var audioCtx = null;
  var sfx = {};

  function ensureAudio() {
    if (audioCtx) return;
    try {
      audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      loadSound('food', 'resource/audio/eat_food.ogg');
      loadSound('trap', 'resource/audio/eat_trap.ogg');
      loadSound('over', 'resource/audio/gameover.ogg');
    } catch (e) {
      audioCtx = null;
    }
  }

  function loadSound(key, url) {
    if (!audioCtx) return;
    fetch(url)
      .then(function (res) { return res.arrayBuffer(); })
      .then(function (buf) { return audioCtx.decodeAudioData(buf); })
      .then(function (decoded) { sfx[key] = decoded; })
      .catch(function () { /* abaikan, game tetap jalan tanpa suara */ });
  }

  function playSound(key) {
    if (!audioCtx || !sfx[key]) return;
    try {
      var src = audioCtx.createBufferSource();
      src.buffer = sfx[key];
      src.connect(audioCtx.destination);
      src.start(0);
    } catch (e) { /* abaikan */ }
  }

  // === State mesin ===
  var state = 'menu'; // menu | loading | playing | gameover

  // === Tombol (koordinat paritas main.py) ===
  var MENU_START = { x: 217, y: 388, w: 100, h: 35 };
  var MENU_EXIT = { x: 491, y: 388, w: 100, h: 35 };
  var OVER_AGAIN = { x: 193, y: 392, w: 100, h: 35 };
  var OVER_EXIT = { x: 515, y: 392, w: 100, h: 35 };

  function hit(b, mx, my) {
    return mx >= b.x && mx <= b.x + b.w && my >= b.y && my <= b.y + b.h;
  }

  function drawButton(msg, b) {
    ctx.fillStyle = COLOR_YELLOW;
    ctx.fillRect(b.x, b.y, b.w, b.h);
    ctx.fillStyle = COLOR_BLACK;
    ctx.font = '20px Arial, sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(msg, b.x + b.w / 2, b.y + b.h / 2 + 1);
  }

  function drawBackground(img, fallbackColor) {
    if (img.complete && img.naturalWidth > 0) {
      ctx.drawImage(img, 0, 0, WIDTH, HEIGHT);
    } else {
      ctx.fillStyle = fallbackColor;
      ctx.fillRect(0, 0, WIDTH, HEIGHT);
    }
  }

  // === Loading ===
  var MAX_LOAD = 523;
  var LOAD_DELAY = 50;  // ms per iterasi (paritas time.sleep(0.05))
  var LOAD_PAUSE = 500; // ms jeda setelah selesai
  var loadWidth = 0;
  var loadingDone = false;
  var loadingPauseTimer = 0;

  function startLoading() {
    state = 'loading';
    loadWidth = 0;
    loadingDone = false;
    loadingPauseTimer = 0;
  }

  // === Game ===
  var snake = [];
  var direction = null;
  var x1, y1, x1c, y1c;
  var lengthOfSnake;
  var food = [];
  var traps = [];
  var level, score, speed;
  var acc = 0;

  function rnd(lo, hi) {
    return Math.floor(Math.random() * (hi - lo)) + lo;
  }

  function resetFoodAndTraps() {
    food = [];
    traps = [];
    for (var i = 0; i < 3; i++) {
      var fx = Math.round(rnd(30, 750) / 20) * 20;
      var fy = Math.round(rnd(30, 550) / 20) * 20;
      food.push([fx, fy]);
    }
    for (var j = 0; j < 15; j++) {
      var tx = Math.round(rnd(30, 750) / 20) * 20;
      var ty = Math.round(rnd(30, 550) / 20) * 20;
      traps.push([tx, ty]);
    }
  }

  function startGameLoop() {
    state = 'playing';
    x1 = WIDTH / 2;
    y1 = HEIGHT / 2;
    x1c = 0;
    y1c = 0;
    snake = [];
    lengthOfSnake = 1;
    direction = null;
    level = 1;
    score = 0;
    speed = INITIAL_SPEED;
    acc = 0;
    resetFoodAndTraps();
  }

  function step() {
    x1 += x1c;
    y1 += y1c;
    var head = [x1, y1];
    snake.push(head);
    if (snake.length > lengthOfSnake) snake.shift();

    // Tabrak dinding
    if (x1 < BORDER || x1 >= WIDTH - BLOCK - BORDER || y1 < BORDER || y1 >= HEIGHT - BLOCK - BORDER) {
      playSound('over');
      state = 'gameover';
      return;
    }

    // Tabrak badan sendiri
    for (var i = 0; i < snake.length - 1; i++) {
      if (snake[i][0] === head[0] && snake[i][1] === head[1]) {
        playSound('over');
        state = 'gameover';
        return;
      }
    }

    // Makan makanan (push ke stack)
    for (var j = 0; j < food.length; j++) {
      if (x1 === food[j][0] && y1 === food[j][1]) {
        lengthOfSnake += 1;
        score += 1;
        playSound('food');
        resetFoodAndTraps();
        if (score % 5 === 0) {
          level += 1;
          speed += 3;
        }
        break;
      }
    }

    // Makan jebakan (pop dari stack)
    for (var k = 0; k < traps.length; k++) {
      if (x1 === traps[k][0] && y1 === traps[k][1]) {
        lengthOfSnake -= 1;
        if (lengthOfSnake < 1) {
          playSound('over');
          state = 'gameover';
          return;
        } else {
          snake.shift();
          playSound('trap');
        }
        resetFoodAndTraps();
        break;
      }
    }
  }

  // === Render ===
  function drawMenu() {
    drawBackground(bgStart, COLOR_BG);
    if (logoImg.complete && logoImg.naturalWidth > 0) {
      ctx.drawImage(logoImg, 0, 0, 100, 100);
    }
    drawButton('Start', MENU_START);
    drawButton('Exit', MENU_EXIT);
  }

  function drawLoading() {
    ctx.fillStyle = COLOR_BG;
    ctx.fillRect(0, 0, WIDTH, HEIGHT);
    if (loadingImg.complete && loadingImg.naturalWidth > 0) {
      ctx.drawImage(loadingImg, WIDTH / 2 - 261, HEIGHT / 2 - 56.5);
    }
    ctx.fillStyle = COLOR_GREEN;
    ctx.fillRect(WIDTH / 2 - 261, HEIGHT / 2 - 56.5, loadWidth, 113);

    var percent = Math.round((loadWidth / MAX_LOAD) * 100);
    ctx.fillStyle = COLOR_WHITE;
    ctx.font = '25px Arial, sans-serif';
    ctx.textAlign = 'left';
    ctx.textBaseline = 'top';
    ctx.fillText(percent + '%', WIDTH / 2 - 20, HEIGHT / 2 + 70);
  }

  function drawGame() {
    ctx.fillStyle = COLOR_BG;
    ctx.fillRect(0, 0, WIDTH, HEIGHT);

    // Bingkai
    ctx.strokeStyle = COLOR_BLACK;
    ctx.lineWidth = BORDER;
    ctx.strokeRect(BORDER / 2, BORDER / 2, WIDTH - BORDER, HEIGHT - BORDER);

    // Makanan
    for (var i = 0; i < food.length; i++) {
      ctx.fillStyle = COLOR_GREEN;
      ctx.fillRect(food[i][0], food[i][1], BLOCK, BLOCK);
    }

    // Jebakan
    for (var j = 0; j < traps.length; j++) {
      ctx.fillStyle = COLOR_RED;
      ctx.fillRect(traps[j][0], traps[j][1], BLOCK, BLOCK);
    }

    // Ular
    for (var k = 0; k < snake.length; k++) {
      ctx.fillStyle = COLOR_BLACK;
      ctx.fillRect(snake[k][0], snake[k][1], BLOCK, BLOCK);
    }

    ctx.fillStyle = COLOR_WHITE;
    ctx.font = '20px Arial, sans-serif';
    ctx.textAlign = 'left';
    ctx.textBaseline = 'top';
    ctx.fillText('Your Score: ' + score, 20, 10);
    ctx.textAlign = 'right';
    ctx.fillText('Level ' + level, WIDTH - 110, 10);
  }

  function drawGameOver() {
    drawBackground(bgOver, COLOR_BG);
    drawButton('Try Again', OVER_AGAIN);
    drawButton('Exit', OVER_EXIT);
  }

  function render() {
    if (state === 'menu') {
      drawMenu();
    } else if (state === 'loading') {
      drawLoading();
    } else if (state === 'playing') {
      drawGame();
    } else if (state === 'gameover') {
      drawGameOver();
    }
  }

  // === Input ===
  window.addEventListener('keydown', function (e) {
    ensureAudio();
    if (state !== 'playing') return;
    if (e.keyCode >= 37 && e.keyCode <= 40) e.preventDefault();

    if (e.keyCode === 37 && direction !== 'RIGHT') { x1c = -BLOCK; y1c = 0; direction = 'LEFT'; }
    else if (e.keyCode === 39 && direction !== 'LEFT') { x1c = BLOCK; y1c = 0; direction = 'RIGHT'; }
    else if (e.keyCode === 38 && direction !== 'DOWN') { y1c = -BLOCK; x1c = 0; direction = 'UP'; }
    else if (e.keyCode === 40 && direction !== 'UP') { y1c = BLOCK; x1c = 0; direction = 'DOWN'; }
  });

  canvas.addEventListener('click', function (e) {
    ensureAudio();
    var rect = canvas.getBoundingClientRect();
    var mx = (e.clientX - rect.left) * (WIDTH / rect.width);
    var my = (e.clientY - rect.top) * (HEIGHT / rect.height);

    if (state === 'menu') {
      if (hit(MENU_START, mx, my)) startLoading();
    } else if (state === 'gameover') {
      if (hit(OVER_AGAIN, mx, my)) startLoading();
      else if (hit(OVER_EXIT, mx, my)) state = 'menu';
    }
  });

  // === Main loop ===
  var last = performance.now();

  function frame(now) {
    var dt = now - last;
    last = now;

    if (state === 'playing') {
      acc += dt;
      var interval = 1000 / speed;
      while (acc >= interval) {
        acc -= interval;
        step();
        if (state !== 'playing') break;
      }
    } else if (state === 'loading') {
      if (!loadingDone) {
        loadWidth += (dt / LOAD_DELAY) * 10;
        if (loadWidth >= MAX_LOAD) {
          loadWidth = MAX_LOAD;
          loadingDone = true;
          loadingPauseTimer = 0;
        }
      } else {
        loadingPauseTimer += dt;
        if (loadingPauseTimer >= LOAD_PAUSE) {
          startGameLoop();
        }
      }
    }

    render();
    requestAnimationFrame(frame);
  }

  requestAnimationFrame(frame);
})();
