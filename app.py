
import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from flask import Flask, Response, jsonify, render_template_string, request

app = Flask(__name__)

# ==========================================
# LUNA AI - INTERFAZ
# ==========================================

PAGE = r"""
<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#0b0812">
<title>Luna AI</title>
<style>
  :root {
    color-scheme: dark;
    --bg:#080711; --panel:#120e1e; --panel2:#191226;
    --line:rgba(208,159,246,.23); --line-hi:rgba(232,180,255,.55);
    --soft:#a99cb9; --white:#f5eafe; --violet:#c78bf7; --pink:#e9abe9;
  }
  * { box-sizing:border-box; }
  body { margin:0; min-width:320px; color:var(--white); font:14px/1.5 "Segoe UI",system-ui,sans-serif;
    background:#090810; }
  button,textarea,input { font:inherit; }
  button { cursor:pointer; }
  button:disabled { cursor:not-allowed; opacity:.48; }
  button:focus-visible,textarea:focus-visible,input:focus-visible { outline:2px solid var(--violet); outline-offset:3px; }
  .shell { min-height:100vh; min-height:100dvh; display:grid; grid-template-rows:67px minmax(0,1fr);
    isolation:isolate; background:radial-gradient(ellipse at 36% 39%,#241631 0%,#100d1b 40%,#080810 83%); position:relative; overflow:hidden; }
  .shell:before { content:""; pointer-events:none; position:absolute; inset:0; z-index:-1; opacity:.35;
    background-image:radial-gradient(#dfbbff 0.7px,transparent 1px),radial-gradient(#e7baff 0.6px,transparent 1px);
    background-size:101px 107px,163px 151px; background-position:11px 34px,55px 91px; }
  .topbar { display:flex;align-items:center;justify-content:space-between;gap:14px;padding:0 23px;
    border-bottom:1px solid var(--line); background:rgba(9,8,17,.84); box-shadow:0 2px 20px rgba(0,0,0,.15); }
  .identity { display:flex;align-items:center;gap:9px;white-space:nowrap; letter-spacing:2px;
    font-size:17px; font-weight:600; color:#f1dcff; }
  .identity svg { width:27px;height:27px;filter:drop-shadow(0 0 8px rgba(221,152,255,.75)); }
  .identity em { font-style:normal;color:#e2a3ee; }
  .top-center { display:flex; gap:8px; align-items:center; justify-content:center;flex-wrap:wrap; }
  .pill { display:inline-flex; align-items:center;gap:8px; border:1px solid var(--line);
    border-radius:999px; padding:7px 11px; font-size:11px; color:#ddd0e9;background:rgba(27,18,42,.75); white-space:nowrap; }
  .pill b {font-weight:600;color:#e9c2ff;} .online-dot {width:7px;height:7px;border-radius:100%;background:#bbecce;box-shadow:0 0 9px #7feeb1;display:inline-block;}
  .top-actions {display:flex;gap:8px;align-items:center;}
  .icon-button {width:34px;height:34px;display:grid;place-items:center;background:transparent;color:#d2b5e6;
    border:1px solid var(--line);border-radius:10px;font-size:17px;}
  .icon-button:hover {border-color:var(--line-hi);background:rgba(180,121,235,.11)}
  .workspace {display:grid; grid-template-columns:78px minmax(250px,1.05fr) minmax(310px,1fr); min-height:0;}
  .rail { display:flex;flex-direction:column;align-items:center;gap:10px;padding:23px 8px 14px;
    border-right:1px solid var(--line);background:rgba(8,7,15,.51); }
  .rail-btn {display:flex;flex-direction:column;justify-content:center;align-items:center;gap:4px;
    min-height:59px;width:60px;border:1px solid transparent;border-radius:13px;color:#afa1c0;background:transparent;}
  .rail-btn svg {width:21px;height:21px;stroke-width:1.7;}
  .rail-btn span {font-size:10px;line-height:1.1;}
  .rail-btn:hover,.rail-btn.active {border-color:rgba(213,153,251,.44);color:#f1d5ff;
    background:linear-gradient(145deg,rgba(165,96,215,.22),rgba(114,61,185,.05));
    box-shadow:inset 0 0 22px rgba(190,108,232,.07);}
  .rail-btn.muted {opacity:.45;cursor:default;}
  .rail-bottom {margin-top:auto;color:#746583;font-size:10px;text-align:center;}
  .stage {min-width:0;display:flex;align-items:center;justify-content:center;flex-direction:column;padding:24px 16px 20px;position:relative;overflow:hidden;}
  .stage:before {content:"";position:absolute;width:min(650px,100%);aspect-ratio:1;border-radius:50%;
    background:radial-gradient(circle,rgba(184,87,228,.12),transparent 67%);filter:blur(3px);pointer-events:none;}
  .eyebrow {font-size:10px;color:#b9a0cc;letter-spacing:3px;position:relative;margin-bottom:6px;}
  .orb {position:relative;width:min(405px,100%);aspect-ratio:1;display:grid;place-items:center;flex-shrink:0;}
  .halo {position:absolute;inset:2%;border:1px solid rgba(204,147,255,.10);border-radius:50%;}
  .halo.outer {inset:7%;border:1px solid rgba(213,143,255,.28);
    border-top:2px solid rgba(233,181,255,.95);border-right:2px solid transparent;border-bottom:1px dashed rgba(201,136,251,.53);
    transform:rotate(7deg);animation:orbit 26s linear infinite;filter:drop-shadow(0 0 8px rgba(199,132,255,.5));}
  .halo.middle {inset:15%;border:1px dashed rgba(214,163,249,.5);border-left:2px solid #a569de;
    border-bottom:2px solid rgba(205,158,249,.15);animation:orbit 39s linear infinite reverse;}
  .halo.inner {inset:24%;border:1px solid rgba(197,141,255,.27);border-top:2px solid rgba(233,190,255,.84);
    border-right:2px solid transparent;animation:orbit 19s linear infinite;}
  .halo.ticks {inset:10%;border:none;background:repeating-conic-gradient(from 4deg,rgba(217,170,255,.57) 0deg 1deg,transparent 1deg 13deg);
    mask:radial-gradient(circle,transparent 66%,#000 67% 68%,transparent 69%);opacity:.6;animation:orbit 80s linear infinite;}
  .orb-star {position:absolute;width:5px;height:5px;background:#fff0ff;transform:rotate(45deg);box-shadow:0 0 15px 3px rgba(220,166,255,.65)}
  .orb-star.one {top:18%;left:28%;}.orb-star.two {right:14%;top:48%;width:3px;height:3px;}.orb-star.three {left:23%;bottom:22%;width:3px;height:3px;}
  .moon-svg {width:53%;height:53%;overflow:visible;filter:drop-shadow(0 0 14px rgba(211,133,254,.61));animation:breathe 5s ease-in-out infinite;}
  .orbit-curve {position:absolute;inset:13%;width:74%;height:74%;pointer-events:none;opacity:.7;transform:rotate(-17deg);}
  .waveform {display:flex;align-items:center;justify-content:center;gap:4px;height:34px;margin-top:-5px;z-index:1;}
  .waveform i {width:2px;height:5px;background:linear-gradient(#f0d0ff,#b66be8);border-radius:3px;box-shadow:0 0 5px #a560e5;}
  .shell[data-state="listening"] .waveform i,.shell[data-state="speaking"] .waveform i {animation:wave .8s ease-in-out infinite alternate;}
  .waveform i:nth-child(2n){animation-delay:-.32s}.waveform i:nth-child(3n){animation-delay:-.55s}.waveform i:nth-child(5n){animation-delay:-.72s}
  .shell[data-state="thinking"] .halo.outer {animation-duration:5s;}.shell[data-state="speaking"] .moon-svg {animation-duration:1.6s;}
  .core-status {text-align:center;z-index:1;margin-top:22px;min-height:64px;}
  .core-status strong {font-size:17px;font-weight:600;color:#ebd1fb;display:block;}
  .core-status span {font-size:12px;color:#a89ab4;display:block;margin-top:6px;max-width:310px;}
  .voice-trigger {margin-top:15px;border:1px solid rgba(228,170,255,.65);border-radius:999px;
    padding:10px 25px;display:flex;gap:9px;align-items:center;color:#f5dcff;
    background:linear-gradient(115deg,rgba(142,64,201,.2),rgba(225,141,235,.13));z-index:1;
    box-shadow:0 0 24px rgba(140,69,198,.13);}
  .voice-trigger:hover {background:rgba(205,137,253,.25);}
  .voice-trigger svg {width:17px;height:17px;}
  .ambient-line {width:85%;height:1px;background:linear-gradient(90deg,transparent,rgba(208,153,255,.45),transparent);margin-top:25px;}
  .conversation {display:flex;flex-direction:column;min-width:0;min-height:0;border-left:1px solid var(--line);
    background:linear-gradient(145deg,rgba(18,13,31,.84),rgba(9,8,16,.83));}
  .conversation-head {height:64px;flex:none;display:flex;align-items:center;justify-content:space-between;
    gap:12px;padding:0 21px;border-bottom:1px solid var(--line);}
  .conversation-head strong {font-weight:600;font-size:15px;}.conversation-head small {color:#ad9fb8;font-size:11px;}
  .thread {flex:1;min-height:0;overflow-y:auto;display:flex;flex-direction:column;gap:16px;padding:22px 20px 18px;
    scrollbar-color:#5f3e75 transparent;scrollbar-width:thin;}
  .bubble {padding:13px 17px;max-width:91%;border-radius:18px;font-size:14px;line-height:1.58;
    overflow-wrap:anywhere;white-space:pre-wrap;box-shadow:0 8px 30px rgba(0,0,0,.12);}
  .bubble.luna {align-self:flex-start;background:linear-gradient(140deg,rgba(86,47,107,.69),rgba(50,34,71,.66));
    border:1px solid rgba(223,167,255,.39);border-bottom-left-radius:5px;}
  .bubble.user {align-self:flex-end;background:linear-gradient(135deg,#2e2840,#231d34);border:1px solid rgba(189,158,224,.28);border-bottom-right-radius:5px;}
  .bubble.system {align-self:center;background:rgba(116,54,96,.21);border:1px solid rgba(235,145,204,.25);font-size:12px;color:#efd4e6;}
  .bubble-label {display:flex;align-items:center;gap:8px;margin-bottom:7px;font-size:10px;font-weight:600;letter-spacing:.5px;color:#edc0ff;}
  .bubble.user .bubble-label {justify-content:flex-end;color:#bfb1d7;}
  .composer {flex:none;display:flex;align-items:end;gap:8px;padding:16px;border-top:1px solid var(--line);background:rgba(12,9,21,.7);}
  .composer textarea {resize:none;min-height:48px;max-height:130px;flex:1;min-width:0;color:#f8e8ff;
    border:1px solid rgba(212,155,255,.42);border-radius:13px;background:rgba(14,10,24,.96);padding:12px 14px;}
  .composer textarea::placeholder {color:#8e829e;}
  .send {height:48px;padding:0 15px;display:flex;align-items:center;gap:6px;border:0;border-radius:13px;
    background:linear-gradient(135deg,#ae77ee,#e5a5e7);color:#1a1021;font-weight:700;}
  .send:hover {filter:brightness(1.12)}
  .send svg{width:17px;height:17px;}
  .overlay {position:fixed;z-index:30;inset:0;background:rgba(2,2,8,.72);display:grid;place-items:center;padding:20px;backdrop-filter:blur(5px);}
  .overlay[hidden] {display:none}
  .dialog {width:min(420px,100%);border:1px solid #9165b0;border-radius:20px;padding:23px;
    background:linear-gradient(145deg,#21142e,#100d19);box-shadow:0 25px 80px #0008;}
  .dialog h2 {margin:0 0 12px;font-size:19px;}.dialog p {color:#b5a4c4;font-size:12px;}
  .setting {display:flex;align-items:center;gap:12px;padding:13px 0;border-bottom:1px solid var(--line);}
  .setting input {accent-color:#c487ff; width:17px;height:17px;}
  .close-dialog {margin-top:20px;padding:10px 20px;border:1px solid #af7bd2;border-radius:11px;
    background:#422651;color:#f2d9ff;}
  @keyframes orbit {to {transform:rotate(360deg)}}
  @keyframes breathe {50% {opacity:.77;transform:scale(.965)}}
  @keyframes wave {to {height:27px;opacity:.55}}
  @media(max-width:1050px) {.top-center .pill:last-child{display:none}.workspace{grid-template-columns:65px minmax(0,.97fr) minmax(300px,1fr)}.rail-btn{width:50px}.stage{padding:12px}.orb{width:min(330px,100%)}}
  @media(max-width:740px) {.shell{grid-template-rows:58px auto}.topbar{padding:0 13px}.identity{font-size:14px}.top-center{display:none}
    .workspace{grid-template-columns:57px minmax(0,1fr);}.rail{grid-row:1 / 3;padding:14px 3px;}.rail-btn{width:49px;min-height:56px}
    .stage{min-height:290px;padding:17px 10px 10px}.eyebrow{margin:0}.orb{width:min(225px,65vw)}
    .core-status{margin-top:8px;min-height:48px}.core-status strong{font-size:15px}.voice-trigger{margin-top:7px}.ambient-line{margin-top:12px}
    .conversation{grid-column:2;min-height:360px;border-left:0;border-top:1px solid var(--line)}
    .conversation-head{height:50px}.thread{max-height:380px;min-height:195px;padding:15px 12px}.composer{padding:12px}
    .bubble{max-width:95%}}
  @media(prefers-reduced-motion:reduce) {*,*::before,*::after{animation:none!important;transition:none!important}}
</style>
</head>
<body>
<div class="shell" id="shell" data-state="idle">
  <header class="topbar">
    <div class="identity" aria-label="Luna AI">
      <svg viewBox="0 0 40 40" aria-hidden="true"><path d="M20 3a17 17 0 1 0 17 24A16 16 0 0 1 20 3Z" fill="#ddafff"/></svg>
      <span>LUNA <em>AI</em></span>
    </div>
    <div class="top-center"><span class="pill"><span class="online-dot"></span> En línea</span>
      <span class="pill">✧ Gemini <b>principal</b></span><span class="pill">◇ OpenRouter <b>respaldo</b></span>
    </div>
    <div class="top-actions"><button class="icon-button" id="settingsButton" title="Configuración" aria-label="Configuración">⚙</button></div>
  </header>
  <main class="workspace">
    <nav class="rail" aria-label="Menú de Luna">
      <button class="rail-btn active" id="navChat" title="Chat" aria-label="Chat">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 5h16v12H9l-5 4V5Z"/></svg><span>Chat</span>
      </button>
      <button class="rail-btn" id="navVoice" title="Hablar con Luna" aria-label="Hablar con Luna">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><rect x="9" y="3" width="6" height="12" rx="3"/><path d="M5 11a7 7 0 0 0 14 0M12 18v3M9 21h6"/></svg><span>Voz</span>
      </button>
      <button class="rail-btn muted" title="Funciones creativas próximamente" disabled aria-label="Crear: próximamente">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="m12 2 1.8 7.2L21 11l-7.2 1.8L12 20l-1.8-7.2L3 11l7.2-1.8L12 2Z"/></svg><span>Crear</span>
      </button>
      <button class="rail-btn muted" title="Organización próximamente" disabled aria-label="Organizar: próximamente">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M7 3v4M17 3v4M3 10h18"/></svg><span>Agenda</span>
      </button>
      <button class="rail-btn" id="navSettings" title="Ajustes" aria-label="Ajustes">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><circle cx="12" cy="12" r="3"/><path d="M9 2h6l1 3 3 2 3-1v6l-3 1-1 3 2 3-5 3-2-3-3 0-2 3-5-3 2-3-1-3-3-1V6l3 1 3-2 1-3Z"/></svg><span>Ajustes</span>
      </button>
      <div class="rail-bottom">LUNA • 1.0</div>
    </nav>
    <section class="stage" aria-label="Núcleo visual de Luna">
      <div class="eyebrow">NÚCLEO LUNAR</div>
      <div class="orb" aria-hidden="true">
        <div class="halo outer"></div><div class="halo middle"></div><div class="halo inner"></div><div class="halo ticks"></div>
        <svg class="orbit-curve" viewBox="0 0 300 300"><ellipse cx="150" cy="150" rx="145" ry="40" transform="rotate(-23 150 150)" stroke="#c08bfa" stroke-width=".8" fill="none" opacity=".55"/><circle cx="278" cy="106" r="2.5" fill="#ffe5ff"/></svg>
        <svg class="moon-svg" viewBox="0 0 240 240">
          <defs>
            <linearGradient id="moonshade" x1="0%" y1="0%" x2="75%" y2="100%"><stop offset="0" stop-color="#fff4ff"/><stop offset=".35" stop-color="#ddabfc"/><stop offset=".8" stop-color="#bd7dec"/><stop offset="1" stop-color="#7e4ead"/></linearGradient>
            <filter id="moontexture" x="-10%" y="-10%" width="120%" height="120%"><feTurbulence type="fractalNoise" baseFrequency=".07" numOctaves="3" seed="6" result="noise"/><feColorMatrix in="noise" type="saturate" values="0" result="gray"/><feBlend in="SourceGraphic" in2="gray" mode="soft-light"/></filter>
            <mask id="crescentmask"><rect width="240" height="240" fill="black"/><circle cx="120" cy="120" r="87" fill="white"/><circle cx="161" cy="77" r="85" fill="black"/></mask>
          </defs>
          <circle cx="120" cy="120" r="87" fill="url(#moonshade)" mask="url(#crescentmask)" filter="url(#moontexture)"/>
          <circle cx="120" cy="120" r="87" stroke="#f2ceff" stroke-width=".7" fill="none" mask="url(#crescentmask)"/>
        </svg>
        <span class="orb-star one"></span><span class="orb-star two"></span><span class="orb-star three"></span>
      </div>
      <div class="waveform" aria-hidden="true">
        <i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i>
      </div>
      <div class="core-status" role="status" aria-live="polite"><strong id="stateTitle">Luna está lista</strong><span id="stateMessage">Escribe o pulsa el botón para hablar.</span></div>
      <button id="micButton" class="voice-trigger" type="button">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="9" y="3" width="6" height="12" rx="3"/><path d="M5 11a7 7 0 0 0 14 0M12 18v3"/></svg><span id="micButtonText">Hablar con Luna</span>
      </button>
      <div class="ambient-line"></div>
    </section>
    <section class="conversation" aria-label="Chat con Luna">
      <div class="conversation-head"><strong>Conversación</strong><small id="brainInfo">Gemini / OpenRouter</small></div>
      <div class="thread" id="thread" role="log" aria-label="Mensajes de Luna" aria-live="polite">
        <div class="bubble luna"><span class="bubble-label">☾ LUNA</span>Hola, soy Luna. Me alegra verte por aquí. ¿En qué puedo ayudarte?</div>
      </div>
      <form class="composer" id="chatForm">
        <textarea id="userInput" rows="2" maxlength="2000" placeholder="Escribe o habla con Luna..." aria-label="Mensaje para Luna"></textarea>
        <button class="send" id="sendButton" type="submit"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 2 11 13M22 2l-7 20-4-9-9-4Z"/></svg><span>Enviar</span></button>
      </form>
    </section>
  </main>
</div>
<div class="overlay" id="settingsOverlay" hidden>
  <section class="dialog" role="dialog" aria-modal="true" aria-labelledby="settingsTitle">
    <h2 id="settingsTitle">Ajustes de Luna</h2>
    <p>Gemini permanece como cerebro principal y OpenRouter como respaldo automático. Por ahora no hay selección manual de modelo.</p>
    <label class="setting"><input type="checkbox" id="voiceToggle" checked> Leer las respuestas en voz alta</label>
    <label class="setting"><input type="checkbox" id="motionToggle" checked> Animaciones del núcleo</label>
    <p>Si ElevenLabs no está disponible, Luna intentará usar únicamente Microsoft Sabina. Si no existe una voz compatible, responderá por escrito.</p>
    <button class="close-dialog" id="closeSettings">Cerrar ajustes</button>
  </section>
</div>
<script>
(function () {
  "use strict";
  const shell = document.getElementById("shell");
  const form = document.getElementById("chatForm");
  const input = document.getElementById("userInput");
  const thread = document.getElementById("thread");
  const stateTitle = document.getElementById("stateTitle");
  const stateMessage = document.getElementById("stateMessage");
  const brainInfo = document.getElementById("brainInfo");
  const sendButton = document.getElementById("sendButton");
  const micButton = document.getElementById("micButton");
  const micText = document.getElementById("micButtonText");
  const settings = document.getElementById("settingsOverlay");
  const voiceToggle = document.getElementById("voiceToggle");
  const motionToggle = document.getElementById("motionToggle");
  let busy = false;
  let rec = null;
  let elevenUnavailable = false;

  function setState(mode, title, detail) {
    shell.dataset.state = mode;
    stateTitle.textContent = title;
    stateMessage.textContent = detail;
  }
  function addBubble(type, message) {
    const bubble = document.createElement("div");
    bubble.className = "bubble " + type;
    if (type !== "system") {
      const label = document.createElement("span");
      label.className = "bubble-label";
      label.textContent = type === "luna" ? "☾ LUNA" : "TÚ";
      bubble.appendChild(label);
    }
    const content = document.createElement("span");
    content.textContent = message;
    bubble.appendChild(content);
    thread.appendChild(bubble);
    thread.scrollTop = thread.scrollHeight;
  }
  function buttons() {
    sendButton.disabled = busy;
    micButton.disabled = busy;
  }
  function stopRecognition() {
    if (rec) {
      const previous = rec;
      rec = null;
      previous.onresult = null;
      try { previous.stop(); } catch (_) {}
    }
    micText.textContent = "Hablar con Luna";
  }
  function speakWithSabina(text) {
    return new Promise(resolve => {
      if (!("speechSynthesis" in window)) return resolve(false);
      const voices = window.speechSynthesis.getVoices();
      const voice = voices.find(v => v.lang.toLowerCase().startsWith("es") && v.name.toLowerCase().includes("sabina"));
      if (!voice) return resolve(false);
      const speech = new SpeechSynthesisUtterance(text);
      speech.voice = voice;
      speech.lang = voice.lang;
      speech.rate = .95;
      speech.pitch = 1.05;
      speech.onend = () => resolve(true);
      speech.onerror = () => resolve(false);
      window.speechSynthesis.cancel();
      window.speechSynthesis.speak(speech);
    });
  }
  function playAudio(blob) {
    return new Promise((resolve, reject) => {
      const url = URL.createObjectURL(blob);
      const audio = new Audio(url);
      const clean = () => URL.revokeObjectURL(url);
      audio.onended = () => { clean(); resolve(); };
      audio.onerror = () => { clean(); reject(new Error("No se pudo reproducir la voz.")); };
      audio.play().catch(e => { clean(); reject(e); });
    });
  }
  async function voice(text) {
    if (!voiceToggle.checked) return "off";
    if (!elevenUnavailable) {
      try {
        const response = await fetch("/api/speak", {
          method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({text})
        });
        if (response.ok) {
          await playAudio(await response.blob());
          return "played";
        }
        elevenUnavailable = true;
      } catch (_) { elevenUnavailable = true; }
    }
    const spoken = await speakWithSabina(text);
    return spoken ? "played" : "unavailable";
  }
  async function askLuna(raw) {
    const message = String(raw || "").trim();
    if (!message || busy) return;
    busy = true;
    stopRecognition();
    buttons();
    addBubble("user", message);
    input.value = "";
    setState("thinking", "Luna está pensando", "Conectando con su cerebro...");
    try {
      const response = await fetch("/api/chat", {
        method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({message})
      });
      let data;
      try { data = await response.json(); } catch (_) { throw new Error("El servidor devolvió una respuesta inesperada."); }
      if (!response.ok) throw new Error(data.error || "No se pudo obtener respuesta.");
      if (typeof data.reply !== "string" || !data.reply.trim()) throw new Error("Luna no recibió una respuesta de texto.");
      addBubble("luna", data.reply);
      const brain = data.brain || "IA";
      brainInfo.textContent = "Respondió: " + brain;
      setState("speaking", "Luna respondió", "Respuesta generada con " + brain);
      const audioState = await voice(data.reply);
      setState("idle", "Luna está lista",
        audioState === "unavailable"
          ? "Respuesta escrita lista. No se encontró una voz femenina disponible."
          : "Puedes seguir conversando.");
    } catch (error) {
      addBubble("system", "No se pudo completar la solicitud: " + (error.message || "Error desconocido"));
      setState("idle", "Luna está disponible", "Prueba nuevamente cuando quieras.");
    } finally { busy = false; buttons(); }
  }
  form.addEventListener("submit", event => {event.preventDefault(); askLuna(input.value);});
  input.addEventListener("keydown", event => {
    if (event.key === "Enter" && !event.shiftKey) {event.preventDefault(); askLuna(input.value);}
  });
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  function listen() {
    if (busy) return;
    if (rec) { stopRecognition(); setState("idle", "Luna está lista", "Micrófono detenido."); return; }
    if (!SpeechRecognition) {setState("idle","Micrófono no disponible","Utiliza Chrome para dictar.");return;}
    const recognition = new SpeechRecognition();
    rec = recognition;
    recognition.lang = "es-DO";
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    recognition.onstart = () => {micText.textContent="Detener escucha";setState("listening","Luna te escucha","Habla cuando quieras...");};
    recognition.onresult = event => {
      if (rec !== recognition || busy) return;
      const spoken = event.results[event.resultIndex][0].transcript;
      recognition.onresult = null;
      stopRecognition();
      askLuna(spoken);
    };
    recognition.onerror = event => {if(rec === recognition) setState("idle","No pude escucharte","Micrófono: " + event.error);};
    recognition.onend = () => {if(rec === recognition){rec=null;micText.textContent="Hablar con Luna";if(!busy)setState("idle","Luna está lista","Puedes volver a hablar.");}};
    try {recognition.start();} catch (_) {rec=null;setState("idle","Micrófono no disponible","No se pudo iniciar la escucha.");}
  }
  micButton.addEventListener("click",listen);
  document.getElementById("navVoice").addEventListener("click",listen);
  document.getElementById("navChat").addEventListener("click",()=>input.focus());
  function showSettings(){settings.hidden=false;document.getElementById("closeSettings").focus();}
  function hideSettings(){settings.hidden=true;document.getElementById("settingsButton").focus();}
  document.getElementById("settingsButton").addEventListener("click",showSettings);
  document.getElementById("navSettings").addEventListener("click",showSettings);
  document.getElementById("closeSettings").addEventListener("click",hideSettings);
  settings.addEventListener("click",e=>{if(e.target===settings)hideSettings();});
  document.addEventListener("keydown",e=>{if(e.key==="Escape"&&!settings.hidden)hideSettings();});
  motionToggle.addEventListener("change",()=>{
    document.querySelectorAll(".halo,.moon-svg,.waveform i").forEach(el=>{el.style.animationPlayState=motionToggle.checked ? "" : "paused";});
  });
})();
</script>
</body>
</html>
"""


# ==========================================
# PÁGINA PRINCIPAL
# ==========================================

@app.get("/")
def home():
    return render_template_string(PAGE)


# ==========================================
# CEREBRO PRINCIPAL: GEMINI
# RESPALDO: OPENROUTER GRATIS
# ==========================================

@app.post("/api/chat")
def chat():

    data = request.get_json(silent=True) or {}

    message = str(data.get("message", "")).strip()

    if not message or len(message) > 2000:
        return jsonify(
            error="Escribe un mensaje de hasta 2000 caracteres."
        ), 400

    # Fecha y hora de República Dominicana

    now = datetime.now(
        ZoneInfo("America/Santo_Domingo")
    )

    weekdays = [
        "lunes", "martes", "miércoles",
        "jueves", "viernes", "sábado", "domingo"
    ]

    months = [
        "enero", "febrero", "marzo", "abril",
        "mayo", "junio", "julio", "agosto",
        "septiembre", "octubre", "noviembre", "diciembre"
    ]

    fecha = (
        f"{weekdays[now.weekday()]} "
        f"{now.day} de {months[now.month - 1]} "
        f"de {now.year}"
    )

    hora = now.strftime("%H:%M")

    instrucciones = (
        "Eres Luna, una asistente personal femenina, "
        "amable, inteligente, tierna y comprensiva. "
        "Habla naturalmente en español. "
        "Responde de forma clara y normalmente breve. "
        "No repitas innecesariamente las respuestas. "
        "Tu personalidad es cercana y conversacional. "
        "No inventes información que desconozcas. "
        f"La fecha actual en República Dominicana es {fecha}. "
        f"La hora local es {hora}. "
        "Utiliza esa fecha para responder preguntas temporales."
    )

    # ======================================
    # INTENTAR GEMINI PRIMERO
    # ======================================

    gemini_key = os.environ.get(
        "GEMINI_API_KEY", ""
    ).strip()

    if gemini_key:

        gemini_url = (
            "https://generativelanguage.googleapis.com/v1beta/"
            "models/gemini-3.1-flash-lite:generateContent"
        )

        gemini_payload = {
            "systemInstruction": {
                "parts": [
                    {"text": instrucciones}
                ]
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": message}
                    ]
                }
            ],
            "generationConfig": {
                "maxOutputTokens": 512
            }
        }

        gemini_request = Request(
            gemini_url,
            data=json.dumps(
                gemini_payload
            ).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": gemini_key
            },
            method="POST"
        )

        try:
            with urlopen(
                gemini_request,
                timeout=25
            ) as response:
                result = json.load(response)

            candidates = result.get("candidates") or []

            parts = (
                candidates[0]
                .get("content", {})
                .get("parts", [])
                if candidates else []
            )

            answer = "".join(
                part.get("text", "")
                for part in parts
                if isinstance(part, dict)
                and not part.get("thought")
            ).strip()

            if answer:
                return jsonify(
                    reply=answer,
                    brain="Gemini"
                )

            app.logger.warning(
                "Gemini devolvió una respuesta vacía."
            )

        except HTTPError as error:

            app.logger.warning(
                "Gemini devolvió HTTP %s.",
                error.code
            )

            # Errores que admiten respaldo
            if error.code not in (
                429, 500, 502, 503, 504
            ):
                return jsonify(
                    error=f"Gemini devolvió HTTP {error.code}."
                ), 502

        except (URLError, TimeoutError):
            app.logger.warning(
                "No fue posible conectar con Gemini."
            )

        except (ValueError, KeyError, TypeError):
            app.logger.warning(
                "Gemini devolvió datos inesperados."
            )

    # ======================================
    # RESPALDO: OPENROUTER
    # ======================================

    app.logger.info(
        "Intentando responder mediante OpenRouter."
    )

    router_key = os.environ.get(
        "OPENROUTER_API_KEY", ""
    ).strip()

    if not router_key:
        return jsonify(
            error=(
                "Gemini no está disponible y falta "
                "OPENROUTER_API_KEY en Render."
            )
        ), 503

    router_url = (
        "https://openrouter.ai/api/v1/chat/completions"
    )

    router_payload = {
        "model": "openrouter/free",
        "messages": [
            {
                "role": "system",
                "content": instrucciones
            },
            {
                "role": "user",
                "content": message
            }
        ],
        "max_tokens": 512
    }

    router_request = Request(
        router_url,
        data=json.dumps(
            router_payload
        ).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {router_key}",
            "X-Title": "Luna AI"
        },
        method="POST"
    )

    try:
        with urlopen(
            router_request,
            timeout=40
        ) as response:
            result = json.load(response)

        choices = result.get("choices") or []

        if not choices:
            return jsonify(
                error="OpenRouter no devolvió respuestas."
            ), 502

        content = (
            choices[0]
            .get("message", {})
            .get("content", "")
        )

        if isinstance(content, str):
            answer = content.strip()

        elif isinstance(content, list):
            answer = "".join(
                item.get("text", "")
                for item in content
                if isinstance(item, dict)
            ).strip()

        else:
            answer = ""

        if not answer:
            return jsonify(
                error="OpenRouter devolvió una respuesta vacía."
            ), 502

        return jsonify(
            reply=answer,
            brain="OpenRouter",
            model=result.get(
                "model",
                "openrouter/free"
            )
        )

    except HTTPError as error:

        app.logger.error(
            "OpenRouter devolvió HTTP %s.",
            error.code
        )

        return jsonify(
            error=(
                f"OpenRouter devolvió HTTP {error.code}. "
                "Revisa los límites y permisos de la clave."
            )
        ), 502

    except (URLError, TimeoutError):
        return jsonify(
            error="No se pudo conectar con OpenRouter."
        ), 502

    except (ValueError, KeyError, TypeError):
        return jsonify(
            error="OpenRouter devolvió datos inesperados."
        ), 502


# ==========================================
# VOZ DE LUNA: ELEVENLABS
# ==========================================

@app.post("/api/speak")
def speak():

    data = request.get_json(silent=True) or {}
    text = str(data.get("text", "")).strip()

    if not text:
        return jsonify(
            error="No hay texto para convertir a voz."
        ), 400

    api_key = os.environ.get(
        "ELEVENLABS_API_KEY", ""
    ).strip()

    voice_id = os.environ.get(
        "ELEVENLABS_VOICE_ID", ""
    ).strip()

    if not api_key or not voice_id:
        return jsonify(
            error="Falta configurar ElevenLabs."
        ), 503

    url = (
        "https://api.elevenlabs.io/v1/text-to-speech/"
        f"{quote(voice_id, safe='')}"
        "?output_format=mp3_44100_128"
    )

    payload = {
        "text": text[:2000],
        "model_id": "eleven_multilingual_v2"
    }

    api_request = Request(
        url,
        data=json.dumps(
            payload
        ).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
            "xi-api-key": api_key
        },
        method="POST"
    )

    try:
        with urlopen(
            api_request,
            timeout=30
        ) as response:
            audio = response.read()

        return Response(
            audio,
            mimetype="audio/mpeg"
        )

    except HTTPError as error:

        raw = error.read().decode(
            "utf-8",
            errors="replace"
        )

        try:
            error_data = json.loads(raw)
        except json.JSONDecodeError:
            error_data = {}

        if not isinstance(error_data, dict):
            error_data = {}

        detail = error_data.get("detail", {})

        if isinstance(detail, dict):
            error_code = (
                detail.get("status")
                or detail.get("code")
                or "desconocido"
            )

            error_message = (
                detail.get("message")
                or "Sin detalles"
            )

        elif isinstance(detail, str):
            error_code = "desconocido"
            error_message = detail

        else:
            error_code = "desconocido"
            error_message = "Sin detalles"

        app.logger.error(
            "ElevenLabs HTTP %s | %s | %s",
            error.code,
            error_code,
            str(error_message)[:200]
        )

        return jsonify(
            error=f"ElevenLabs: {error_code}"
        ), 502

    except (URLError, TimeoutError):
        return jsonify(
            error="No se pudo conectar con ElevenLabs."
        ), 502


# ==========================================
# INICIAR LUNA AI
# ==========================================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "5000"))
    )
