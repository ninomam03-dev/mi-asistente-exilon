# Luna AI — Cyber Celestial UI
# Apariencia nueva. Chat, voz, dictado y cerebros conservados.

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
    --motion-play: running;
    --bg:#060812; --panel:#0f1322; --panel2:#15182d;
    --line:rgba(103,232,249,.16); --line-hi:rgba(232,102,255,.42);
    --soft:#96a4c7; --white:#f5f7ff; --violet:#d186ff; --pink:#ff87d7;
    --cyan:#69f0ff; --blue:#58b4ff; --magenta:#ff53c8; --ink:#05070e;
  }
  * { box-sizing:border-box; }
  body { margin:0; min-width:320px; color:var(--white); font:14px/1.5 "Segoe UI",system-ui,sans-serif;
    background:radial-gradient(circle at top,#12162b 0,#090b15 38%,#05060c 100%); }
  button,textarea,input { font:inherit; }
  button { cursor:pointer; }
  button:disabled { cursor:not-allowed; opacity:.48; }
  button:focus-visible,textarea:focus-visible,input:focus-visible { outline:2px solid var(--violet); outline-offset:3px; }
  .shell { height:100vh; height:100dvh; min-height:0; display:grid; grid-template-rows:67px minmax(0,1fr);
    isolation:isolate; background:
      radial-gradient(circle at 25% 20%,rgba(255,83,200,.13),transparent 20%),
      radial-gradient(circle at 75% 18%,rgba(105,240,255,.12),transparent 22%),
      radial-gradient(circle at 50% 45%,rgba(104,76,255,.11),transparent 30%),
      linear-gradient(180deg,#090b16 0%,#05060d 100%);
    position:relative; overflow:hidden; }
  .shell:before { content:""; pointer-events:none; position:absolute; inset:0; z-index:-1; opacity:.30;
    background-image:
      radial-gradient(rgba(255,255,255,.6) 0.7px,transparent 1px),
      radial-gradient(rgba(148,224,255,.45) 0.6px,transparent 1px);
    background-size:101px 107px,163px 151px; background-position:11px 34px,55px 91px; }
  .shell:after { content:""; pointer-events:none; position:absolute; inset:0; z-index:-1; opacity:.14;
    background:repeating-linear-gradient(180deg,transparent 0 3px,rgba(105,240,255,.06) 3px 4px);
    mix-blend-mode:screen; animation:scan 12s linear infinite; animation-play-state:var(--motion-play); }
  .topbar { display:flex;align-items:center;justify-content:space-between;gap:14px;padding:0 23px;
    border-bottom:1px solid rgba(105,240,255,.14); background:linear-gradient(180deg,rgba(7,10,19,.92),rgba(8,10,18,.66));
    box-shadow:0 2px 20px rgba(0,0,0,.25),0 0 24px rgba(105,240,255,.05); backdrop-filter:blur(10px); }
  .identity { display:flex;align-items:center;gap:9px;white-space:nowrap; letter-spacing:3px;
    font-size:17px; font-weight:700; color:#f1f6ff; text-shadow:0 0 10px rgba(105,240,255,.12); }
  .identity svg { width:27px;height:27px;filter:drop-shadow(0 0 8px rgba(105,240,255,.45)) drop-shadow(0 0 16px rgba(255,83,200,.18)); }
  .identity em { font-style:normal;color:var(--cyan); animation:flicker 4.8s infinite; animation-play-state:var(--motion-play); }
  .top-center { display:flex; gap:8px; align-items:center; justify-content:center;flex-wrap:wrap; }
  .pill { display:inline-flex; align-items:center;gap:8px; border:1px solid rgba(105,240,255,.18);
    border-radius:999px; padding:7px 11px; font-size:11px; color:#d8e7ff;background:rgba(18,25,42,.68); white-space:nowrap;
    box-shadow:inset 0 0 15px rgba(105,240,255,.03), 0 0 20px rgba(255,83,200,.03); }
  .pill b {font-weight:700;color:#ffd0f8;} .online-dot {width:7px;height:7px;border-radius:100%;background:#8dffcb;box-shadow:0 0 9px #7feeb1;display:inline-block;}
  .top-actions {display:flex;gap:8px;align-items:center;}
  .icon-button {width:34px;height:34px;display:grid;place-items:center;background:rgba(16,20,35,.45);color:#d8d9ff;
    border:1px solid rgba(105,240,255,.15);border-radius:10px;font-size:17px;box-shadow:0 0 18px rgba(105,240,255,.03)}
  .icon-button:hover {border-color:var(--line-hi);background:rgba(180,121,235,.11);box-shadow:0 0 18px rgba(255,83,200,.12)}
  .workspace {display:grid; grid-template-columns:78px minmax(250px,1.05fr) minmax(310px,1fr); min-height:0; height:100%; overflow:hidden;}
  .rail { display:flex;flex-direction:column;align-items:center;gap:10px;padding:23px 8px 14px;
    border-right:1px solid rgba(105,240,255,.10);background:linear-gradient(180deg,rgba(5,8,16,.72),rgba(8,9,17,.5)); backdrop-filter:blur(8px); }
  .rail-btn {display:flex;flex-direction:column;justify-content:center;align-items:center;gap:4px;
    min-height:59px;width:60px;border:1px solid transparent;border-radius:13px;color:#afa1c0;background:transparent;}
  .rail-btn svg {width:21px;height:21px;stroke-width:1.7;}
  .rail-btn span {font-size:10px;line-height:1.1;}
  .rail-btn:hover,.rail-btn.active {border-color:rgba(105,240,255,.28);color:#f8deff;
    background:linear-gradient(145deg,rgba(255,83,200,.14),rgba(58,121,255,.08));
    box-shadow:inset 0 0 22px rgba(190,108,232,.10), 0 0 16px rgba(105,240,255,.08);}
  .rail-btn.muted {opacity:.45;cursor:default;}
  .rail-bottom {margin-top:auto;color:#746583;font-size:10px;text-align:center;}
  .stage {min-width:0;min-height:0;display:flex;align-items:center;justify-content:center;flex-direction:column;padding:15px 16px 14px;position:relative;overflow:hidden;}
  .stage:before {content:"";position:absolute;width:min(650px,100%);aspect-ratio:1;border-radius:50%;
    background:radial-gradient(circle,rgba(255,83,200,.12),transparent 45%), radial-gradient(circle at 40% 60%,rgba(105,240,255,.16),transparent 56%);filter:blur(3px);pointer-events:none;}
  .stage:after {content:"";position:absolute;inset:auto 7% 6% 7%;height:180px;pointer-events:none;opacity:.28;
    background:linear-gradient(180deg,transparent 0%,rgba(105,240,255,.18) 100%);
    clip-path:polygon(0 100%,50% 0,100% 100%);
    filter:blur(28px);}
  .eyebrow {font-size:10px;color:#9bc2ff;letter-spacing:4px;position:relative;margin-bottom:6px;text-shadow:0 0 8px rgba(105,240,255,.18);}
  .orb {position:relative;width:min(405px,100%,46vh);aspect-ratio:1;display:grid;place-items:center;flex-shrink:0; filter:drop-shadow(0 0 24px rgba(105,240,255,.12)) drop-shadow(0 0 30px rgba(255,83,200,.10));}
  .halo {position:absolute;inset:2%;border:1px solid rgba(204,147,255,.10);border-radius:50%;}
  .orb::before {content:"";position:absolute;inset:4%;border-radius:50%;
    background:radial-gradient(circle,rgba(255,255,255,.06) 0,rgba(105,240,255,.05) 26%,rgba(255,83,200,.04) 42%,transparent 70%);
    filter:blur(18px);animation:pulseGlow 4.5s ease-in-out infinite; animation-play-state:var(--motion-play);}
  .orb::after {content:"";position:absolute;inset:0;border-radius:50%;
    background:conic-gradient(from 0deg,transparent 0deg 36deg,rgba(105,240,255,.55) 42deg 48deg,transparent 54deg 130deg,rgba(255,83,200,.6) 134deg 138deg,transparent 142deg 270deg,rgba(105,240,255,.32) 276deg 282deg,transparent 286deg 360deg);
    mask:radial-gradient(circle,transparent 72%,#000 73% 74%,transparent 75%);
    animation:orbit 14s linear infinite; animation-play-state:var(--motion-play); opacity:.75;}
  .halo.outer {inset:7%;border:1px solid rgba(105,240,255,.24);
    border-top:2px solid rgba(105,240,255,.95);border-right:2px solid transparent;border-bottom:1px dashed rgba(255,83,200,.58);
    transform:rotate(7deg);animation:orbit 18s linear infinite; animation-play-state:var(--motion-play);filter:drop-shadow(0 0 8px rgba(105,240,255,.5));}
  .halo.middle {inset:15%;border:1px dashed rgba(214,163,249,.45);border-left:2px solid var(--magenta);
    border-bottom:2px solid rgba(105,240,255,.18);animation:orbit 30s linear infinite reverse; animation-play-state:var(--motion-play);}
  .halo.inner {inset:24%;border:1px solid rgba(197,141,255,.22);border-top:2px solid rgba(255,190,255,.84);
    border-right:2px solid transparent;animation:orbit 12s linear infinite; animation-play-state:var(--motion-play);}
  .halo.ticks {inset:10%;border:none;background:repeating-conic-gradient(from 4deg,rgba(105,240,255,.70) 0deg 1deg,transparent 1deg 13deg);
    mask:radial-gradient(circle,transparent 66%,#000 67% 68%,transparent 69%);opacity:.45;animation:orbit 60s linear infinite; animation-play-state:var(--motion-play);}
  .orb-star {position:absolute;width:5px;height:5px;background:#fff0ff;transform:rotate(45deg);box-shadow:0 0 15px 3px rgba(220,166,255,.65)}
  .orb-star.one {top:18%;left:28%;}.orb-star.two {right:14%;top:48%;width:3px;height:3px;}.orb-star.three {left:23%;bottom:22%;width:3px;height:3px;}
  .moon-svg {width:53%;height:53%;overflow:visible;filter:drop-shadow(0 0 14px rgba(255,83,200,.42)) drop-shadow(0 0 24px rgba(105,240,255,.25));animation:breathe 3.8s ease-in-out infinite; animation-play-state:var(--motion-play);}
  .orbit-curve {position:absolute;inset:13%;width:74%;height:74%;pointer-events:none;opacity:.8;transform:rotate(-17deg);animation:orbit 22s linear infinite reverse; animation-play-state:var(--motion-play);}
  .waveform {display:flex;align-items:center;justify-content:center;gap:4px;height:34px;margin-top:-5px;z-index:1;filter:drop-shadow(0 0 8px rgba(105,240,255,.16));}
  .waveform i {width:2px;height:5px;background:linear-gradient(var(--cyan),var(--magenta));border-radius:3px;box-shadow:0 0 7px rgba(105,240,255,.55);}
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
  .conversation {display:flex;flex-direction:column;min-width:0;min-height:0;max-height:100%;overflow:hidden;border-left:1px solid var(--line);
    background:linear-gradient(145deg,rgba(18,13,31,.84),rgba(9,8,16,.83));}
  .conversation-head {height:64px;flex:none;display:flex;align-items:center;justify-content:space-between;
    gap:12px;padding:0 21px;border-bottom:1px solid var(--line);}
  .conversation-head strong {font-weight:600;font-size:15px;}.conversation-head small {color:#ad9fb8;font-size:11px;}
  .thread {flex:1 1 0;min-height:0;overflow-y:auto;overscroll-behavior:contain;display:flex;flex-direction:column;gap:16px;padding:22px 20px 18px;
    scrollbar-color:#5f3e75 transparent;scrollbar-width:thin;}
  .bubble {padding:13px 17px;max-width:91%;border-radius:18px;font-size:14px;line-height:1.58;
    overflow-wrap:anywhere;white-space:pre-wrap;box-shadow:0 8px 30px rgba(0,0,0,.12);}
  .bubble.luna {align-self:flex-start;background:linear-gradient(140deg,rgba(86,47,107,.69),rgba(50,34,71,.66));
    border:1px solid rgba(223,167,255,.39);border-bottom-left-radius:5px;}
  .bubble.user {align-self:flex-end;background:linear-gradient(135deg,#2e2840,#231d34);border:1px solid rgba(189,158,224,.28);border-bottom-right-radius:5px;}
  .bubble.system {align-self:center;background:rgba(116,54,96,.21);border:1px solid rgba(235,145,204,.25);font-size:12px;color:#efd4e6;}
  .bubble-label {display:flex;align-items:center;gap:8px;margin-bottom:7px;font-size:10px;font-weight:600;letter-spacing:.5px;color:#edc0ff;}
  .bubble.user .bubble-label {justify-content:flex-end;color:#bfb1d7;}
  .composer {flex:none;display:flex;align-items:end;gap:8px;padding:13px 16px;border-top:1px solid var(--line);background:rgba(12,9,21,.88);z-index:2;}
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
  @keyframes breathe {50% {opacity:.8;transform:scale(.96)}}
  @keyframes wave {to {height:27px;opacity:.55}}
  @keyframes pulseGlow {50% {transform:scale(1.04); opacity:.86}}
  @keyframes sweep {to {transform:translateX(520%)}}
  @keyframes scan {from {transform:translateY(-8%)} to {transform:translateY(8%)}}
  @keyframes flicker {0%,19%,21%,63%,65%,100% {opacity:1} 20%,64% {opacity:.6}}
  @keyframes messageIn {from {transform:translateY(8px); opacity:0} to {transform:translateY(0); opacity:1}}
  @media(max-width:1050px) {.top-center .pill:last-child{display:none}.workspace{grid-template-columns:65px minmax(0,.97fr) minmax(300px,1fr)}.rail-btn{width:50px}.stage{padding:12px}.orb{width:min(330px,100%)}}
  @media(max-width:740px) {.shell{grid-template-rows:58px minmax(0,1fr)}.topbar{padding:0 13px}.identity{font-size:14px}.top-center{display:none}
    .workspace{grid-template-columns:57px minmax(0,1fr);grid-template-rows:minmax(148px,.48fr) minmax(0,1fr);height:100%;overflow:hidden}
    .rail{grid-row:1 / 3;padding:14px 3px;}.rail-btn{width:49px;min-height:56px}
    .stage{min-height:0;padding:7px 10px;overflow:hidden}.eyebrow{display:none}.orb{width:min(156px,45vw,20vh)}
    .waveform{height:18px}.core-status{margin-top:3px;min-height:34px}.core-status strong{font-size:13px}.core-status span{font-size:10px}
    .voice-trigger{margin-top:4px;padding:7px 13px;font-size:11px}.ambient-line{display:none}
    .conversation{grid-column:2;grid-row:2;min-height:0;max-height:100%;border-left:0;border-top:1px solid var(--line)}
    .conversation-head{height:44px}.thread{max-height:none;min-height:0;padding:12px}.composer{padding:9px}
    .bubble{max-width:95%}}
  @media(max-height:600px) and (min-width:741px) {
    .stage{padding:4px 9px}.orb{width:min(235px,100%,38vh)}.core-status{margin-top:3px;min-height:40px}
    .ambient-line{display:none}.voice-trigger{margin-top:5px;padding:8px 13px}.eyebrow{display:none}
  }
  /* Animaciones controladas por el ajuste de Luna, no anuladas globalmente por el sistema. */

  /* ==========================================================
     LUNA AI: ANIMACIONES VIVAS (ligeras, CSS/SVG + audio real)
     Los estados idle / listening / thinking / speaking controlan todo.
     ========================================================== */
  .shell {--activity:0;}
  .stage{isolation:isolate;}
  .stage>*{position:relative;z-index:2;}
  .stage::before{animation:breathSky 5s ease-in-out infinite;animation-play-state:var(--motion-play);}
  .starfield{position:absolute;inset:0;overflow:hidden;z-index:0;pointer-events:none;}
  .starfield .spark{position:absolute;width:2px;height:2px;border-radius:50%;background:#e5faff;
    box-shadow:0 0 7px 1px rgba(118,221,255,.75);animation:starTwinkle 3s ease-in-out infinite;animation-play-state:var(--motion-play);}
  .starfield .spark.magenta{background:#ffd4f8;box-shadow:0 0 8px 1px rgba(255,90,214,.7);}
  .constellation-sky{position:absolute;inset:4% 4% auto 4%;width:92%;height:91%;z-index:1;opacity:.7;
    pointer-events:none;filter:drop-shadow(0 0 4px rgba(105,240,255,.3));}
  .constellation-sky .constellation{stroke:#8adeff;stroke-width:1.15;fill:none;stroke-linecap:round;stroke-linejoin:round;
    animation:constellationCycle 36s ease-in-out infinite;animation-play-state:var(--motion-play);opacity:0;}
  .constellation-sky .constellation:nth-child(2){stroke:#f3a3e7;animation-delay:-24s;}
  .constellation-sky .constellation:nth-child(3){stroke:#d3a5ff;animation-delay:-12s;}
  .constellation-sky .point{fill:#fcf4ff;stroke:none;filter:drop-shadow(0 0 4px #aefbff);}
  .constellation-sky .path{stroke-dasharray:3 4;}
  .stage .eyebrow{color:#b5eaff;animation:techShimmer 4.5s ease-in-out infinite;animation-play-state:var(--motion-play);}
  .orb{transition:filter .3s ease;will-change:transform;animation:floatCore 5.5s ease-in-out infinite;animation-play-state:var(--motion-play);}
  .orb::before{opacity:.9;animation:coreGlow 3s ease-in-out infinite;animation-play-state:var(--motion-play);}
  .orb::after{opacity:1;animation-duration:8s;}
  .halo.outer{animation-duration:12s;border-top-width:3px;box-shadow:0 0 19px rgba(95,240,255,.20),inset 0 0 15px rgba(95,240,255,.05);}
  .halo.middle{animation-duration:18s;box-shadow:0 0 14px rgba(255,83,200,.10);}
  .halo.inner{animation-duration:8s;}
  .halo.ticks{animation-duration:27s;opacity:.72;}
  .orb-star{animation:beacon 2.2s ease-in-out infinite;animation-play-state:var(--motion-play);}
  .orb-star.two{animation-delay:-.7s;}.orb-star.three{animation-delay:-1.4s;}
  .moon-svg{animation:moonAlive 3.2s ease-in-out infinite;animation-play-state:var(--motion-play);}
  .orbit-curve{animation-duration:14s;}
  .waveform{height:72px;gap:5px;width:min(360px,92%);margin-top:-8px;
    transition:filter .2s ease;filter:drop-shadow(0 0 9px rgba(105,240,255,.4));}
  .waveform i{display:block;flex:1 1 0;max-width:5px;min-width:2px;height:100%;border-radius:999px;
    transform-origin:center center;transform:scaleY(.16);opacity:.65;
    background:linear-gradient(180deg,#b8fbff 0%,#78dbff 28%,#c181fa 65%,#ff68cc 100%);
    box-shadow:0 0 7px rgba(105,240,255,.5);animation:idlePulse 1.8s ease-in-out infinite alternate;
    animation-play-state:var(--motion-play);will-change:transform;}
  .waveform i:nth-child(2n){animation-delay:-.43s;}.waveform i:nth-child(3n){animation-delay:-1.12s;}
  .waveform i:nth-child(5n){animation-delay:-.85s;}.waveform i:nth-child(7n){animation-delay:-.16s;}
  .shell[data-state="listening"] .waveform{filter:drop-shadow(0 0 16px rgba(93,239,255,.9));}
  .shell[data-state="listening"] .waveform i{opacity:1;animation:listenPulse .52s ease-in-out infinite alternate;animation-play-state:var(--motion-play);}
  .shell[data-state="listening"] .orb{filter:drop-shadow(0 0 26px rgba(105,240,255,.4)) drop-shadow(0 0 42px rgba(255,83,200,.24));}
  .shell[data-state="listening"] .halo.outer{animation-duration:5s;}
  .shell[data-state="listening"] .moon-svg{animation-duration:1.6s;}
  .shell[data-state="thinking"] .waveform i{opacity:.85;animation:thinkPulse .66s ease-in-out infinite alternate;animation-play-state:var(--motion-play);}
  .shell[data-state="thinking"] .halo.outer{animation-duration:2.5s;}
  .shell[data-state="thinking"] .halo.inner{animation-duration:3s;}
  .shell[data-state="thinking"] .orb::before{animation-duration:1.4s;}
  .shell[data-state="speaking"] .waveform{filter:drop-shadow(0 0 15px rgba(255,83,200,.7));}
  .shell[data-state="speaking"] .waveform i{opacity:1;animation:speechPulse .42s ease-in-out infinite alternate;animation-play-state:var(--motion-play);}
  .shell[data-state="speaking"] .moon-svg{animation-duration:1.15s;}
  /* El analizador Web Audio reemplaza la simulación solamente durante captura real. */
  .shell[data-mic-live="true"][data-state="listening"] .waveform i{animation:none!important;}
  .shell[data-mic-live="true"][data-state="listening"] .waveform i{transition:transform .06s linear;}
  .voice-trigger{position:relative;overflow:hidden;transition:background .2s,border-color .2s,box-shadow .2s;
    border-color:rgba(105,240,255,.65);box-shadow:0 0 22px rgba(105,240,255,.15),inset 0 0 15px rgba(255,83,200,.10);}
  .voice-trigger::after{content:"";position:absolute;inset:0;transform:translateX(-130%);pointer-events:none;
    background:linear-gradient(90deg,transparent,rgba(191,248,255,.24),transparent);
    animation:glide 3.3s ease-in-out infinite;animation-play-state:var(--motion-play);}
  .shell[data-state="listening"] .voice-trigger{box-shadow:0 0 24px rgba(105,240,255,.28),0 0 46px rgba(255,83,200,.13);}
  .core-status strong{text-shadow:0 0 9px rgba(201,125,255,.20);}
  .bubble{animation:messageEntry .32s ease both;}
  .online-dot{animation:beacon 2.6s ease-in-out infinite;animation-play-state:var(--motion-play);}
  .ambient-line{height:2px;overflow:hidden;position:relative;opacity:.95;
    background:linear-gradient(90deg,transparent,rgba(105,240,255,.6),rgba(255,83,200,.9),transparent);}
  .ambient-line::after{content:"";position:absolute;top:0;left:0;height:100%;width:30%;
    background:linear-gradient(90deg,transparent,#fff,transparent);animation:glide 3.1s linear infinite;animation-play-state:var(--motion-play);}
  .motion-off *, .motion-off *::before, .motion-off *::after {animation:none!important;transition:none!important;}
  .motion-off .waveform i{transform:scaleY(.17)!important;}
  @keyframes floatCore {0%,100%{transform:translateY(-5px)}50%{transform:translateY(8px)}}
  @keyframes moonAlive {0%,100%{transform:scale(.98);opacity:.90;filter:drop-shadow(0 0 7px rgba(255,83,200,.45))}
    50%{transform:scale(1.05);opacity:1;filter:drop-shadow(0 0 21px rgba(105,240,255,.62))}}
  @keyframes breathSky {0%,100%{transform:scale(.98);opacity:.65}50%{transform:scale(1.07);opacity:1}}
  @keyframes coreGlow {0%,100%{transform:scale(.92);opacity:.5}50%{transform:scale(1.12);opacity:1}}
  @keyframes idlePulse {0%{transform:scaleY(.09)}100%{transform:scaleY(.26)}}
  @keyframes listenPulse {0%{transform:scaleY(.14)}100%{transform:scaleY(.89)}}
  @keyframes speechPulse {0%{transform:scaleY(.20)}100%{transform:scaleY(1)}}
  @keyframes thinkPulse {0%{transform:scaleY(.20)}100%{transform:scaleY(.64)}}
  @keyframes constellationCycle {0%,7%{opacity:0}12%,29%{opacity:.8}35%,100%{opacity:0}}
  @keyframes starTwinkle {0%,100%{opacity:.17;transform:scale(.7)}50%{opacity:.9;transform:scale(1.5)}}
  @keyframes techShimmer {0%,100%{opacity:.6}50%{opacity:1}}
  @keyframes beacon {0%,100%{opacity:.5;filter:brightness(1)}50%{opacity:1;filter:brightness(1.7)}}
  @keyframes glide {to{transform:translateX(390%)}}
  @keyframes messageEntry {from{opacity:0;transform:translateY(9px)}to{opacity:1;transform:translateY(0)}}
  @media(max-width:740px){.waveform{height:37px;margin-top:-12px;gap:3px}.waveform i{max-width:3px}.constellation-sky{opacity:.4}}
  @media(max-height:610px) and (min-width:741px){.waveform{height:43px}.orb{width:min(320px,100%,43vh)}}


/* LUNA 5.0 | Cyber Celestial — temas, efectos y optimizaciones */
:root {
  --l-primary:#bd46ff;--l-secondary:#ff52cd;--l-accent:#8a4cff;
  --l-primary-rgb:189,70,255;--l-secondary-rgb:255,82,205;
  --l-base:#070611;--l-panel:#110b20;--l-panel2:#1c1230;
  --l-text:#fbf4ff;--l-muted:#b8a5cd;--l-border:rgba(210,130,255,.27);
  --l-moon1:#fff2ff;--l-moon2:#e9a9ff;--l-moon3:#9227de;
}
html{color-scheme:dark}
body {color:var(--l-text);background:var(--l-base)}
.shell {
 background:
   radial-gradient(ellipse at 29% 22%,rgba(var(--l-primary-rgb),.20),transparent 33%),
   radial-gradient(ellipse at 83% 79%,rgba(var(--l-secondary-rgb),.10),transparent 44%),
   radial-gradient(ellipse at 50% 68%,rgba(var(--l-primary-rgb),.09),transparent 58%),
   var(--l-base);
 color:var(--l-text);
}
.shell:before {
 opacity:.5;
 background-image:radial-gradient(var(--l-moon1) .8px,transparent 1px),radial-gradient(var(--l-primary) .8px,transparent 1px);
}
.shell:after {background:repeating-linear-gradient(180deg,transparent 0 3px,rgba(var(--l-primary-rgb),.05) 3px 4px)}
.topbar {
 border-bottom:1px solid var(--l-border);
 background:linear-gradient(180deg,color-mix(in srgb,var(--l-panel) 92%,transparent),color-mix(in srgb,var(--l-panel) 70%,transparent));
 box-shadow:0 2px 28px rgba(var(--l-primary-rgb),.07),inset 0 -1px rgba(var(--l-primary-rgb),.08);
}
.identity{color:var(--l-text);text-shadow:0 0 18px rgba(var(--l-primary-rgb),.18)}
.identity em{color:var(--l-primary)}
.identity svg{filter:drop-shadow(0 0 10px var(--l-primary))}
.identity svg path{fill:var(--l-primary)}
.pill,.icon-button {
 background:color-mix(in srgb,var(--l-panel2) 70%,transparent);
 color:var(--l-text);border-color:var(--l-border);
 box-shadow:inset 0 0 12px rgba(var(--l-primary-rgb),.07);
}
.pill b{color:var(--l-primary)}
.icon-button:hover,.icon-button:focus-visible{border-color:var(--l-primary);background:rgba(var(--l-primary-rgb),.15)}
.rail {
 background:linear-gradient(180deg,color-mix(in srgb,var(--l-base) 92%,transparent),color-mix(in srgb,var(--l-panel) 73%,transparent));
 border-right:1px solid var(--l-border);
}
.rail-btn{color:var(--l-muted)}
.rail-btn.active,.rail-btn:hover{
 background:linear-gradient(130deg,rgba(var(--l-primary-rgb),.22),rgba(var(--l-secondary-rgb),.08));
 color:var(--l-text);border-color:var(--l-border);box-shadow:inset 0 0 20px rgba(var(--l-primary-rgb),.12),0 0 12px rgba(var(--l-primary-rgb),.08);
}
.rail-bottom{color:var(--l-muted)}
.stage:before{
 background:radial-gradient(circle,rgba(var(--l-primary-rgb),.22) 0,rgba(var(--l-secondary-rgb),.08) 34%,transparent 68%);
 animation:breathingFog 10s ease-in-out infinite;animation-play-state:var(--motion-play);
}
.stage:after{background:linear-gradient(180deg,transparent,rgba(var(--l-primary-rgb),.22))}
.eyebrow{color:var(--l-primary);text-shadow:0 0 10px var(--l-primary);font-size:11px;font-weight:600;letter-spacing:4px}
.orb{filter:drop-shadow(0 0 28px rgba(var(--l-primary-rgb),.20)) drop-shadow(0 0 42px rgba(var(--l-secondary-rgb),.12))}
.orb::before{background:radial-gradient(circle,rgba(var(--l-primary-rgb),.18),rgba(var(--l-secondary-rgb),.11) 28%,transparent 66%)}
.orb::after{
 background:conic-gradient(from 0deg,transparent 0 31deg,var(--l-primary) 40deg 46deg,transparent 51deg 128deg,var(--l-secondary) 133deg 141deg,transparent 146deg 271deg,var(--l-primary) 282deg 289deg,transparent 293deg 360deg);
}
.halo.outer{border-color:rgba(var(--l-primary-rgb),.25);border-top:3px solid var(--l-primary);border-bottom:1px dashed var(--l-secondary);filter:drop-shadow(0 0 11px var(--l-primary))}
.halo.middle{border-color:rgba(var(--l-primary-rgb),.45);border-left:3px solid var(--l-secondary)}
.halo.inner{border-color:rgba(var(--l-primary-rgb),.26);border-top:3px solid var(--l-primary)}
.halo.ticks{background:repeating-conic-gradient(from 4deg,var(--l-primary) 0deg 1deg,transparent 1deg 11deg)}
.moon-svg{filter:drop-shadow(0 0 15px rgba(var(--l-primary-rgb),.72)) drop-shadow(0 0 35px rgba(var(--l-secondary-rgb),.3))}
#moonshade stop:nth-child(1){stop-color:var(--l-moon1)}
#moonshade stop:nth-child(2){stop-color:var(--l-moon2)}
#moonshade stop:nth-child(3){stop-color:var(--l-primary)}
#moonshade stop:nth-child(4){stop-color:var(--l-moon3)}
.orbit-curve ellipse{stroke:var(--l-primary)}
.orbit-curve circle{fill:var(--l-secondary)}
.orb-star{background:var(--l-moon1);box-shadow:0 0 19px 4px rgba(var(--l-primary-rgb),.8)}
.constellation-sky .path{stroke:var(--l-primary)}
.constellation-sky .point{fill:var(--l-moon1);filter:drop-shadow(0 0 6px var(--l-primary))}
.spark{background:var(--l-primary);box-shadow:0 0 9px var(--l-primary)}
.spark.magenta{background:var(--l-secondary);box-shadow:0 0 10px var(--l-secondary)}
.waveform{filter:drop-shadow(0 0 12px rgba(var(--l-primary-rgb),.3))}
.waveform i{
 background:linear-gradient(180deg,var(--l-moon1),var(--l-primary),var(--l-secondary));
 box-shadow:0 0 12px rgba(var(--l-primary-rgb),.46);
}
.shell[data-state="listening"] .waveform{filter:drop-shadow(0 0 16px var(--l-primary))}
.shell[data-state="speaking"] .waveform{filter:drop-shadow(0 0 15px var(--l-secondary))}
.shell[data-state="listening"] .orb{filter:drop-shadow(0 0 38px var(--l-primary))}
.core-status strong{color:var(--l-text);text-shadow:0 0 14px rgba(var(--l-primary-rgb),.40)}
.core-status span{color:var(--l-muted)}
.voice-trigger{border-color:var(--l-primary);color:var(--l-text);
 background:linear-gradient(130deg,rgba(var(--l-primary-rgb),.21),rgba(var(--l-secondary-rgb),.09));
 box-shadow:0 0 22px rgba(var(--l-primary-rgb),.25),inset 0 0 15px rgba(var(--l-primary-rgb),.08)}
.voice-trigger:hover{background:rgba(var(--l-primary-rgb),.25);border-color:var(--l-moon1)}
.ambient-line{background:linear-gradient(90deg,transparent,var(--l-primary),var(--l-secondary),transparent);box-shadow:0 0 10px rgba(var(--l-primary-rgb),.45)}
.conversation{border-color:var(--l-border);
 background:linear-gradient(160deg,color-mix(in srgb,var(--l-panel) 95%,transparent),color-mix(in srgb,var(--l-base) 92%,transparent));
}
.conversation-head{border-bottom:1px solid var(--l-border);color:var(--l-text)}
.conversation-head small{color:var(--l-muted)}
.thread{background-image:linear-gradient(rgba(var(--l-primary-rgb),.045) 1px,transparent 1px),linear-gradient(90deg,rgba(var(--l-primary-rgb),.045) 1px,transparent 1px);background-size:32px 32px;}
.bubble.luna{background:linear-gradient(145deg,color-mix(in srgb,var(--l-panel2) 94%,transparent),color-mix(in srgb,var(--l-panel) 94%,transparent));border:1px solid var(--l-border);color:var(--l-text)}
.bubble.user{background:linear-gradient(135deg,rgba(var(--l-primary-rgb),.19),rgba(var(--l-secondary-rgb),.13));border:1px solid var(--l-border);color:var(--l-text)}
.bubble.system{background:color-mix(in srgb,var(--l-panel2) 86%,transparent);border-color:var(--l-border);color:var(--l-text)}
.bubble-label{color:var(--l-primary)}
.composer{border-top:1px solid var(--l-border);background:var(--l-panel)}
.composer textarea{background:var(--l-base);border:1px solid var(--l-border);color:var(--l-text);box-shadow:inset 0 0 12px rgba(var(--l-primary-rgb),.03)}
.composer textarea:focus{outline:1px solid var(--l-primary);box-shadow:0 0 15px rgba(var(--l-primary-rgb),.15)}
.composer textarea::placeholder{color:var(--l-muted)}
.send{background:linear-gradient(130deg,var(--l-primary),var(--l-secondary));color:#fff;box-shadow:0 0 25px rgba(var(--l-primary-rgb),.22)}
.overlay{background:rgba(3,3,10,.80)}
.dialog{width:min(690px,100%);max-height:min(88vh,770px);overflow:auto;border:1px solid var(--l-border);background:linear-gradient(165deg,var(--l-panel2),var(--l-panel));color:var(--l-text);box-shadow:0 28px 80px rgba(0,0,0,.65),0 0 35px rgba(var(--l-primary-rgb),.09)}
.dialog h2{font-size:22px;letter-spacing:.4px}
.dialog p{color:var(--l-muted)}
.dialog .subhead{font-size:10px;letter-spacing:3px;text-transform:uppercase;color:var(--l-primary);font-weight:700;margin:22px 0 11px}
.setting{border-bottom:1px solid var(--l-border);font-size:13px;justify-content:space-between}
.setting input[type=checkbox]{accent-color:var(--l-primary)}
.close-dialog{border-color:var(--l-primary);color:var(--l-text);background:rgba(var(--l-primary-rgb),.22)}
.theme-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}
.theme-tile{min-width:0;min-height:90px;display:flex;flex-direction:column;align-items:flex-start;justify-content:space-between;text-align:left;gap:9px;
 border:1px solid var(--l-border);border-radius:15px;color:var(--l-text);padding:11px;background:var(--l-panel);transition:transform .2s,border-color .2s,box-shadow .2s}
.theme-tile:hover{transform:translateY(-2px);border-color:var(--l-primary)}
.theme-tile[aria-pressed="true"]{border-color:var(--l-primary);box-shadow:0 0 0 1px var(--l-primary),0 0 18px rgba(var(--l-primary-rgb),.18)}
.theme-swatches{height:25px;width:100%;display:flex;align-items:center;gap:7px}
.theme-dot{width:22px;height:22px;border-radius:50%;border:1px solid rgba(255,255,255,.5);box-shadow:0 0 15px currentColor}
.theme-tile small{font-size:11px;font-weight:600;color:inherit}
.custom-row{display:flex;gap:12px;align-items:center;justify-content:space-between;margin-top:12px;padding:12px;border:1px solid var(--l-border);border-radius:13px}
.custom-row label{font-size:12px}
.custom-row input[type=color]{width:42px;height:32px;padding:2px;border:1px solid var(--l-border);background:var(--l-panel);border-radius:8px;cursor:pointer}
.custom-btn{border:1px solid var(--l-border);border-radius:11px;background:rgba(var(--l-primary-rgb),.18);color:var(--l-text);padding:8px 10px;font-size:11px}
.brain-select{border:1px solid var(--l-border);border-radius:10px;color:var(--l-text);background:var(--l-base);padding:7px;width:min(220px,100%)}
.dialog-note{font-size:11px;line-height:1.5;margin:8px 0}
.tech-chip{position:absolute;z-index:1;bottom:11%;left:6%;color:var(--l-muted);font-size:9px;letter-spacing:2px;opacity:.6;pointer-events:none}
.tech-chip.right{left:auto;right:6%}
.cosmic-ring{position:absolute;inset:1%;border-radius:50%;pointer-events:none;
 background:conic-gradient(from 0deg,transparent 0deg 42deg,rgba(var(--l-primary-rgb),.14) 43deg 61deg,transparent 62deg 185deg,rgba(var(--l-secondary-rgb),.17) 188deg 198deg,transparent 199deg 360deg);
 mask:radial-gradient(circle,transparent 64%,#000 65% 66%,transparent 67%);
 animation:orbit 32s linear infinite reverse;animation-play-state:var(--motion-play)
}
.cosmic-mist{position:absolute;inset:7%;border-radius:50%;pointer-events:none;
 background:conic-gradient(from -12deg,transparent 0deg 70deg,rgba(var(--l-primary-rgb),.28) 101deg,transparent 145deg 230deg,rgba(var(--l-secondary-rgb),.24) 254deg,transparent 311deg 360deg);
 filter:blur(28px);opacity:.7;animation:cosmicSpin 25s linear infinite;animation-play-state:var(--motion-play)
}
.stage-corners{position:absolute;inset:18px;z-index:0;pointer-events:none;opacity:.4;
 background:linear-gradient(var(--l-primary),var(--l-primary)) top left/27px 1px no-repeat,
 linear-gradient(var(--l-primary),var(--l-primary)) top left/1px 27px no-repeat,
 linear-gradient(var(--l-secondary),var(--l-secondary)) bottom right/27px 1px no-repeat,
 linear-gradient(var(--l-secondary),var(--l-secondary)) bottom right/1px 27px no-repeat;}
@keyframes cosmicSpin{to{transform:rotate(360deg)}}
@keyframes breathingFog{50%{transform:scale(1.13);opacity:.55}}
@media(max-width:750px){.theme-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.tech-chip{display:none}.dialog{padding:15px}}
@media(max-width:430px){.custom-row{gap:7px;flex-wrap:wrap}.theme-grid{gap:7px}.theme-tile{min-height:76px;padding:9px}.dialog{max-height:90vh}}
/* Tema blanco auténtico; no solo neón blanco sobre fondo negro. */
html.theme-light{color-scheme:light}
html.theme-light .identity{color:#1c2033}
html.theme-light .pill,html.theme-light .icon-button{color:#303347}
html.theme-light .rail-btn.active,html.theme-light .rail-btn:hover{color:#242439}
html.theme-light .online-dot{background:#149b6e}
html.theme-light .voice-trigger{color:#24243a}
html.theme-light .topbar{background:rgba(255,255,255,.91)}
html.theme-light .bubble.luna{background:rgba(255,255,255,.88)}
html.theme-light .bubble.user{background:rgba(216,222,244,.90)}
html.theme-light .theme-tile{background:#eef0f8}
html.theme-light .theme-tile small{color:#31364a}
html.theme-light .close-dialog,html.theme-light .custom-btn{color:#27273b}
html.theme-light .send{color:#1f1e2f}
html.theme-light .stage:before{opacity:.25}
html.eco .shell:after, html.eco .cosmic-mist,html.eco .stage:after{display:none}
html.eco .orb,html.eco .moon-svg,html.eco .stage:before{filter:none}
html.eco .spark:nth-child(n+22){display:none}
html.eco .halo.outer{animation-duration:25s}
html.sky-off .starfield,html.sky-off .constellation-sky{display:none}

/* ═══════════════════════════════════════════════════════════════════
   LUNA CELESTIAL — DISEÑO DE ALTA FIDELIDAD
   Solamente apariencia. No modifica los endpoints ni el dictado.
   El arte holográfico de la luna se incluye dentro de este archivo.
   ═══════════════════════════════════════════════════════════════════ */
:root { --l-hue:0deg; --l-primary:#bd46ff; --l-secondary:#ff52cd; --l-primary-rgb:189,70,255; }
html,body {height:100%; background:#07020f;}
.shell {
  height:100dvh; min-height:0; overflow:hidden;
  display:grid; grid-template-rows:76px minmax(0,1fr);
  border:1px solid rgba(var(--l-primary-rgb),.45);
  border-radius:27px;
  margin:0; isolation:isolate;
  box-shadow: inset 0 0 28px rgba(var(--l-primary-rgb),.10),0 0 36px rgba(var(--l-primary-rgb),.10);
  background:
    radial-gradient(ellipse 52% 37% at 35% 47%,rgba(var(--l-primary-rgb),.13),transparent 79%),
    radial-gradient(ellipse 42% 66% at 3% 11%,rgba(var(--l-secondary-rgb),.21),transparent 74%),
    radial-gradient(ellipse 47% 45% at 100% 90%,rgba(var(--l-primary-rgb),.17),transparent 79%),
    linear-gradient(118deg,var(--l-base),#090416 48%,var(--l-base));
}
.shell::before {
  z-index:-1;opacity:.65;
  background-image:
   radial-gradient(circle,rgba(255,255,255,.93) .9px,transparent 1.5px),
   radial-gradient(circle,rgba(var(--l-primary-rgb),.65) 1px,transparent 2px),
   linear-gradient(112deg,transparent 34%,rgba(var(--l-primary-rgb),.055) 50%,transparent 66%);
  background-size:89px 112px,147px 151px,100% 100%;
  animation:galaxyDrift 36s linear infinite; animation-play-state:var(--motion-play)
}
.shell::after {
  z-index:-1; inset:-5% -10%; opacity:.52;
  background:
   radial-gradient(ellipse 35% 4% at 27% 5%,rgba(var(--l-primary-rgb),.7),transparent 75%),
   radial-gradient(ellipse 38% 6% at 89% 98%,rgba(var(--l-secondary-rgb),.5),transparent 75%),
   conic-gradient(from 170deg at 43% 50%,transparent 0 65deg,rgba(var(--l-primary-rgb),.08) 74deg,transparent 83deg 230deg,rgba(var(--l-secondary-rgb),.06) 245deg,transparent 258deg);
  mix-blend-mode:screen; filter:blur(14px);
  animation:nebulaBreath 15s ease-in-out infinite; animation-play-state:var(--motion-play)
}
.topbar {
  position:relative;z-index:9;border:0;margin:12px 17px 0;min-height:56px;
  padding:0 21px 0 19px; border-radius:27px 27px 16px 16px;
  background:linear-gradient(90deg,rgba(30,9,47,.85),rgba(9,7,20,.82) 54%,rgba(25,10,42,.79));
  border:1px solid rgba(var(--l-primary-rgb),.46);
  box-shadow:0 0 24px rgba(var(--l-primary-rgb),.21),inset 0 1px 0 rgba(255,255,255,.15),0 0 4px var(--l-primary);
  backdrop-filter:blur(14px);
}
.topbar::before {
  content:"";position:absolute;height:2px;left:5%;right:5%;bottom:-1px;
  background:linear-gradient(90deg,transparent,var(--l-primary),transparent,var(--l-secondary),transparent);
  box-shadow:0 0 15px var(--l-primary);opacity:.85;pointer-events:none;
}
.topbar::after {
  content:"☾  ◐  ☽"; position:absolute;top:-16px;left:50%;transform:translateX(-50%);
  color:var(--l-moon1);font-size:17px;letter-spacing:4px;text-shadow:0 0 9px var(--l-primary),0 0 23px var(--l-secondary);
  padding:0 15px;background:color-mix(in srgb,var(--l-base) 89%,transparent);
  pointer-events:none;
}
.identity {font-size:19px;letter-spacing:5px;font-weight:500;color:var(--l-text);}
.identity svg {height:35px;width:35px;filter:drop-shadow(0 0 7px var(--l-primary)) drop-shadow(0 0 18px var(--l-secondary));}
.identity em {font-weight:300;color:var(--l-moon1);}
.pill {border-color:rgba(var(--l-primary-rgb),.27);background:rgba(var(--l-primary-rgb),.07);box-shadow:0 0 12px rgba(var(--l-primary-rgb),.05);}
.top-center{font-size:11px}.top-actions{gap:10px}.icon-button{background:rgba(var(--l-primary-rgb),.08);border-color:rgba(var(--l-primary-rgb),.25);color:var(--l-text)}
.icon-button:hover{border-color:var(--l-primary);box-shadow:0 0 14px rgba(var(--l-primary-rgb),.48)}
.workspace{
  position:relative;height:100%;min-height:0;min-width:0;
  display:grid;grid-template-columns:83px minmax(340px,1.42fr) minmax(310px,1.04fr);
  grid-template-rows:minmax(0,1fr);gap:14px;
  padding:16px 22px 104px 20px;overflow:hidden;
}
.workspace:has(.overlay:not([hidden])) {
  grid-template-columns:83px minmax(350px,1.43fr) minmax(270px,1fr) minmax(270px,.9fr);
}
.rail{
  min-height:0;z-index:5;border-radius:32px 19px 30px 30px;
  border:1px solid rgba(var(--l-primary-rgb),.42);
  background:linear-gradient(180deg,rgba(var(--l-primary-rgb),.12),rgba(19,9,34,.84) 27%,rgba(11,7,24,.81));
  box-shadow:inset 0 0 25px rgba(var(--l-primary-rgb),.08),0 0 21px rgba(var(--l-primary-rgb),.17);
  padding:22px 5px 20px;gap:15px;
}
.rail::after {content:"✦";font-size:30px;line-height:1;color:var(--l-primary);text-shadow:0 0 12px var(--l-primary);margin-top:auto}
.rail-bottom{margin-top:4px!important;font-size:8px;letter-spacing:.7px;color:var(--l-muted)}
.rail-btn {min-height:66px;width:62px;color:var(--l-muted);border-radius:17px;}
.rail-btn svg {width:24px;height:24px;filter:drop-shadow(0 0 3px rgba(var(--l-primary-rgb),.23));}
.rail-btn span {font-size:11px;}
.rail-btn:hover,.rail-btn.active{
  color:var(--l-text);border:1px solid var(--l-primary);background:linear-gradient(145deg,rgba(var(--l-primary-rgb),.35),rgba(var(--l-secondary-rgb),.12));
  box-shadow:inset 0 0 24px rgba(var(--l-primary-rgb),.20),0 0 15px rgba(var(--l-primary-rgb),.52),0 0 30px rgba(var(--l-primary-rgb),.18);
}
.stage {position:relative;min-height:0;min-width:0;padding:4px 10px 10px;justify-content:center;overflow:hidden;isolation:isolate}
.stage::before {inset:4% -2%;width:auto;aspect-ratio:auto;
  background:radial-gradient(circle at 50% 45%,rgba(var(--l-primary-rgb),.24),transparent 50%),
             radial-gradient(ellipse at 8% 33%,rgba(var(--l-secondary-rgb),.19),transparent 37%);
  animation:nebulaBreath 8s ease-in-out infinite;animation-play-state:var(--motion-play);
}
.stage::after {inset:auto -5% 1%;height:30%;opacity:.85;
 background:radial-gradient(ellipse at center,rgba(var(--l-primary-rgb),.25),transparent 64%);clip-path:none;filter:blur(24px)}
.eyebrow {font-size:10px;letter-spacing:5px;color:var(--l-moon1);text-shadow:0 0 12px var(--l-primary);margin:2px 0 -3px;opacity:.8}
.orb {width:min(550px,100%,55vh);max-height:none;filter:none!important;overflow:visible;}
.orb::before {inset:4%;background:radial-gradient(circle,rgba(var(--l-primary-rgb),.2),transparent 62%);filter:blur(26px);}
.orb::after {opacity:.63!important;}
.luna-art {
  position:absolute;inset:-1.5%;z-index:4;border-radius:50%;pointer-events:none;
  background-image: url("data:image/webp;base64,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");
  background-position:center;background-size:100% 100%;
  filter:hue-rotate(var(--l-hue)) saturate(1.15) drop-shadow(0 0 22px rgba(var(--l-primary-rgb),.45));
  transform:translateZ(0);animation:lunarArtPulse 5s ease-in-out infinite;
  animation-play-state:var(--motion-play);
}
.moon-svg {opacity:0!important;pointer-events:none;}
.orb .halo {z-index:5;pointer-events:none;opacity:.52}
.halo.outer {inset:0%;border-color:rgba(var(--l-primary-rgb),.37);border-top:1px solid var(--l-primary);border-bottom-color:var(--l-secondary);filter:drop-shadow(0 0 9px var(--l-primary));}
.halo.middle {inset:9%;border-color:rgba(var(--l-primary-rgb),.2);border-left:2px solid var(--l-secondary);}
.halo.inner {inset:17%;border-color:rgba(var(--l-primary-rgb),.25);border-right:1px solid var(--l-primary)}
.halo.ticks {inset:2%;opacity:.35}
.cosmic-ring,.cosmic-mist{z-index:1}.orbit-curve{z-index:6;opacity:.3}.orb-star{z-index:8}
.waveform {position:relative;z-index:7;height:54px;width:min(300px,72%);margin-top:-5%;}
.waveform i {max-width:4px;background:linear-gradient(var(--l-moon1),var(--l-primary),var(--l-secondary));box-shadow:0 0 8px var(--l-primary);}
.core-status {position:relative;z-index:5;min-height:52px;margin-top:2px}
.core-status strong {font-size:14px;letter-spacing:1.5px;text-transform:uppercase;text-shadow:0 0 12px var(--l-primary)}
.core-status span {font-size:11px;margin-top:2px}
.voice-trigger {position:relative;z-index:9;margin-top:8px;border-radius:50%;width:66px;height:66px;padding:0;justify-content:center;
 border:2px solid var(--l-primary);background:radial-gradient(circle,rgba(var(--l-primary-rgb),.35),rgba(var(--l-primary-rgb),.14));
 color:var(--l-text);box-shadow:0 0 0 8px rgba(var(--l-primary-rgb),.10),0 0 18px var(--l-primary),inset 0 0 18px rgba(var(--l-primary-rgb),.32);
 animation:micBreath 3s ease-in-out infinite;animation-play-state:var(--motion-play)}
.voice-trigger svg{width:26px;height:26px}
.voice-trigger span {position:absolute;left:calc(100% + 18px);top:50%;transform:translateY(-50%);width:137px;
 font-size:11px;font-weight:600;white-space:normal;text-align:left;text-shadow:0 0 11px var(--l-primary)}
.shell[data-state="listening"] .voice-trigger {animation:micListen .9s ease-in-out infinite}
.ambient-line {height:2px;width:min(310px,70%);margin-top:18px;background:linear-gradient(90deg,transparent,var(--l-primary),var(--l-secondary),transparent);box-shadow:0 0 16px var(--l-primary);}
.starfield{z-index:-1}.constellation-sky{z-index:1;opacity:.67}
.conversation{
  position:relative;z-index:5;display:flex;min-height:0;overflow:hidden;
  border:1px solid rgba(var(--l-primary-rgb),.44);border-radius:34px;
  background:linear-gradient(155deg,rgba(26,9,43,.88),rgba(13,7,28,.83) 38%,rgba(22,9,39,.86));
  box-shadow:inset 0 0 32px rgba(var(--l-primary-rgb),.065),0 0 27px rgba(var(--l-primary-rgb),.18);
  backdrop-filter:blur(10px);
}
.conversation::before {content:"";position:absolute;inset:0;z-index:0;pointer-events:none;border-radius:inherit;
 background:radial-gradient(ellipse 95% 20% at 50% 100%,rgba(var(--l-primary-rgb),.19),transparent 85%);
 border-bottom:2px solid rgba(var(--l-primary-rgb),.8);
 box-shadow:inset 0 -10px 20px rgba(var(--l-primary-rgb),.09);}
.conversation-head {height:64px;z-index:2;position:relative;background:linear-gradient(90deg,rgba(var(--l-primary-rgb),.07),transparent);border-bottom:1px solid rgba(var(--l-primary-rgb),.12);}
.conversation-head strong {font-size:13px;letter-spacing:2px;font-weight:600;color:var(--l-moon1);text-shadow:0 0 10px rgba(var(--l-primary-rgb),.3)}
.conversation-head small {color:var(--l-muted);font-size:10px}
.thread {position:relative;z-index:1;gap:15px;padding:21px 17px 17px;min-height:0;overflow:auto;background:none!important;}
.bubble {max-width:96%;padding:13px 16px;border-radius:19px;font-size:13px;line-height:1.55;
 backdrop-filter:blur(10px);animation:messageEntry .4s ease;animation-play-state:var(--motion-play)}
.bubble.luna {background:linear-gradient(145deg,rgba(var(--l-primary-rgb),.24),rgba(17,9,33,.86));border:1px solid rgba(var(--l-primary-rgb),.54);
 box-shadow:0 0 18px rgba(var(--l-primary-rgb),.10),inset 0 0 18px rgba(var(--l-primary-rgb),.07);}
.bubble.user {background:linear-gradient(130deg,rgba(var(--l-primary-rgb),.28),rgba(var(--l-secondary-rgb),.19));border:1px solid rgba(var(--l-primary-rgb),.43);
 box-shadow:0 0 18px rgba(var(--l-primary-rgb),.07)}
.bubble-label {font-size:9px;letter-spacing:2px;color:var(--l-moon1);margin-bottom:8px}
.composer {position:absolute;z-index:20;left:121px;right:24px;bottom:17px;min-height:69px;
 border:1px solid rgba(var(--l-primary-rgb),.7);border-radius:22px;padding:8px 10px 8px 14px;
 background:linear-gradient(130deg,rgba(var(--l-primary-rgb),.11),rgba(21,9,36,.94) 18%,rgba(14,8,26,.97));
 box-shadow:0 0 18px rgba(var(--l-primary-rgb),.40),inset 0 0 16px rgba(var(--l-primary-rgb),.07);
 align-items:center;}
.composer::before{content:"+";display:grid;place-items:center;width:37px;height:37px;flex:none;border:1px solid rgba(var(--l-primary-rgb),.65);
 border-radius:11px;color:var(--l-moon1);font-size:24px;font-weight:300;background:rgba(var(--l-primary-rgb),.1);pointer-events:none}
.composer textarea {min-height:46px;max-height:80px;resize:none;line-height:1.5;border:none!important;outline:none!important;
 background:transparent!important;color:var(--l-text);box-shadow:none!important;padding:12px 10px;font-size:13px}
.composer textarea:focus{box-shadow:none!important}
.send {height:45px;width:55px;padding:0;justify-content:center;border:1px solid rgba(255,255,255,.25);border-radius:13px;
 background:radial-gradient(circle at 30% 20%,var(--l-secondary),var(--l-primary));color:#fff;
 box-shadow:0 0 16px rgba(var(--l-primary-rgb),.72),inset 0 0 12px rgba(255,255,255,.19);}
.send span{display:none}.send svg {height:23px;width:23px}
.overlay {position:relative;grid-column:4;grid-row:1;display:flex;align-items:stretch;justify-content:stretch;
 min-width:0;min-height:0;inset:auto;padding:0;margin:0;backdrop-filter:none;background:transparent;z-index:8;overflow:hidden;}
.overlay[hidden]{display:none!important}
.dialog {position:relative;display:flex;flex-direction:column;width:100%;height:100%;min-height:0;max-height:none;overflow:hidden;
 margin:0;padding:14px 12px 16px;border-radius:29px;
 border:1px solid rgba(var(--l-primary-rgb),.72);
 background:linear-gradient(155deg,rgba(33,10,46,.95),rgba(16,8,33,.97));
 box-shadow:inset 0 0 25px rgba(var(--l-primary-rgb),.10),0 0 22px rgba(var(--l-primary-rgb),.26),inset 0 -4px 14px rgba(var(--l-secondary-rgb),.10);}
.settings-heading {display:flex;align-items:center;gap:8px;flex:0 0 auto;padding:4px 4px 10px;border-bottom:1px solid rgba(var(--l-primary-rgb),.25);}
.settings-heading h2 {font-size:15px;letter-spacing:.3px;margin:0;flex:1;color:var(--l-text);}
.settings-close {flex:0 0 auto;margin:0;padding:4px 9px;border:0;background:transparent;color:var(--l-muted);font-size:22px;line-height:1;cursor:pointer;}
.settings-tabs{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:5px;margin:10px 0 14px;flex:none}
.settings-tab{min-width:0;border:1px solid rgba(var(--l-primary-rgb),.17);border-radius:11px;padding:8px 2px;
 background:rgba(var(--l-primary-rgb),.06);color:var(--l-muted);font-size:11px}
.settings-tab[aria-selected="true"]{color:var(--l-text);border-color:var(--l-primary);
 background:linear-gradient(125deg,rgba(var(--l-primary-rgb),.42),rgba(var(--l-secondary-rgb),.12));box-shadow:0 0 15px rgba(var(--l-primary-rgb),.38)}
.settings-pane{min-height:0;overflow:auto;scrollbar-color:rgba(var(--l-primary-rgb),.45) transparent;scrollbar-width:thin;padding:0 4px 7px}
.settings-pane[hidden]{display:none}
.dialog .subhead{font-size:12px;color:var(--l-text);letter-spacing:.2px;text-transform:none;margin:3px 0 3px;font-weight:700}
.dialog .dialog-note{color:var(--l-muted);font-size:11px;line-height:1.45;margin:0 0 12px}
.theme-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:6px;align-items:stretch}
.theme-tile{position:relative;display:flex;flex-direction:column;justify-content:center;align-items:center;gap:7px;
 border:1px solid transparent;border-radius:12px;min-height:84px;padding:9px 4px 7px;background:rgba(var(--l-primary-rgb),.03);
 transition:border-color .2s,background .2s,transform .2s,box-shadow .2s}
.theme-tile:hover{transform:translateY(-2px);border-color:rgba(var(--l-primary-rgb),.55);background:rgba(var(--l-primary-rgb),.11)}
.theme-tile[aria-pressed="true"]{border-color:var(--l-primary);background:rgba(var(--l-primary-rgb),.18);box-shadow:0 0 15px rgba(var(--l-primary-rgb),.25),inset 0 0 9px rgba(var(--l-primary-rgb),.12)}
.theme-tile[aria-pressed="true"]::after{content:"✓";position:absolute;top:4px;right:5px;width:16px;height:16px;line-height:16px;text-align:center;
 border-radius:50%;background:var(--l-primary);color:#fff;font-size:10px;box-shadow:0 0 9px var(--l-primary)}
.theme-swatches{display:flex;justify-content:center;align-items:center;width:100%;height:auto}
.theme-dot {display:block;width:39px;height:39px;flex:none;border-radius:50%;
 background:
  radial-gradient(circle at 33% 25%,rgba(255,255,255,.97) 0%,rgba(255,255,255,.30) 8%,transparent 17%),
  radial-gradient(circle at 27% 22%,var(--swatch-secondary) 0%,var(--swatch-main) 42%,#03020b 100%)!important;
 border:1px solid rgba(255,255,255,.37);
 box-shadow:0 0 8px var(--swatch-main),inset -6px -7px 13px rgba(0,0,0,.48),inset 3px 4px 11px rgba(255,255,255,.15);}
.theme-swatches .theme-dot:not(:first-child){display:none}
.theme-tile small{font-size:10px;line-height:1.12;text-align:center;font-weight:500;color:var(--l-text)!important;max-width:100%}
.custom-row{margin-top:14px;padding:10px 8px;flex-wrap:wrap;gap:9px}
.custom-row label{font-size:11px}
.custom-btn{padding:9px 12px}
.setting{font-size:12px;align-items:center;flex-wrap:wrap;gap:8px;padding:14px 4px}
.brain-select{width:100%}
.dialog p{color:var(--l-muted)}
html.theme-light .shell {background:radial-gradient(ellipse at 40% 42%,rgba(var(--l-primary-rgb),.17),transparent 67%),var(--l-base)}
html.theme-light .topbar,html.theme-light .rail,html.theme-light .conversation,html.theme-light .dialog{background:linear-gradient(155deg,var(--l-panel),var(--l-panel2))}
html.theme-light .composer{background:var(--l-panel)}
html.theme-light .bubble.luna{background:color-mix(in srgb,var(--l-panel) 85%,var(--l-primary) 15%)}
html.theme-light .bubble.user{background:color-mix(in srgb,var(--l-panel2) 80%,var(--l-primary) 20%)}
html.theme-light .settings-tab{color:var(--l-muted)}
html.theme-light .settings-tab[aria-selected="true"]{color:var(--l-text)}
html.theme-light .theme-tile small{color:var(--l-text)!important}
html.eco .luna-art{filter:hue-rotate(var(--l-hue)) saturate(1.03)}
@keyframes lunarArtPulse {0%,100%{transform:scale(.99);opacity:.92}50%{transform:scale(1.015);opacity:1}}
@keyframes nebulaBreath {0%,100%{opacity:.55;transform:scale(1)}50%{opacity:.86;transform:scale(1.05)}}
@keyframes micBreath {0%,100%{box-shadow:0 0 0 6px rgba(var(--l-primary-rgb),.07),0 0 15px var(--l-primary)}50%{box-shadow:0 0 0 12px rgba(var(--l-primary-rgb),.11),0 0 24px var(--l-primary)}}
@keyframes micListen {0%,100%{box-shadow:0 0 0 6px rgba(var(--l-primary-rgb),.12),0 0 20px var(--l-primary)}50%{box-shadow:0 0 0 17px rgba(var(--l-primary-rgb),.08),0 0 36px var(--l-secondary)}}
@keyframes galaxyDrift {to {background-position:89px 112px,-147px 151px,center}}
@media(max-width:1450px){
 .workspace:has(.overlay:not([hidden])){grid-template-columns:76px minmax(290px,1.25fr) minmax(260px,1fr) minmax(250px,.92fr);gap:9px;padding-left:13px;padding-right:13px}
 .workspace:has(.overlay:not([hidden])) .orb{width:min(460px,100%,49vh)}
}
@media(max-width:1120px){
 .workspace,.workspace:has(.overlay:not([hidden])){grid-template-columns:73px minmax(290px,1.1fr) minmax(290px,1fr);gap:10px;padding:12px 12px 94px}
 .overlay{position:absolute;grid-column:auto;grid-row:auto;right:12px;top:12px;bottom:90px;width:min(350px,calc(100% - 100px));height:auto;
 box-shadow:0 0 30px rgba(0,0,0,.7)}
 .composer{left:100px;right:14px}
 .orb{width:min(470px,100%,51vh)}
}
@media(max-width:740px){
 .shell{border-radius:0;grid-template-rows:62px minmax(0,1fr)}
 .topbar{margin:5px 5px 0;min-height:49px;padding:0 10px}
 .topbar::after{display:none}.identity{font-size:13px;letter-spacing:2px}.identity svg{width:25px}
 .workspace,.workspace:has(.overlay:not([hidden])){display:grid;grid-template-columns:49px minmax(0,1fr);
  grid-template-rows:minmax(170px,.48fr) minmax(0,1fr);gap:6px;padding:8px 8px 82px}
 .rail{grid-row:1/3;border-radius:22px;padding:7px 0;gap:4px}.rail-btn{min-height:50px;width:42px}.rail-btn svg{height:19px;width:19px}.rail-btn span{font-size:9px}
 .rail::after{font-size:19px}.rail-bottom{font-size:7px}
 .stage{grid-column:2;grid-row:1;padding:2px 5px 0;overflow:hidden}
 .eyebrow,.stage .tech-chip{display:none!important}
 .orb{width:min(162px,48vw,22vh)}
 .waveform{height:24px;margin-top:-6px;width:160px;gap:3px}
 .core-status{margin-top:0;min-height:31px}.core-status strong{font-size:11px}.core-status span{display:none}
 .voice-trigger{width:37px;height:37px;margin-top:1px;box-shadow:0 0 8px var(--l-primary)}.voice-trigger svg{width:18px;height:18px}
 .voice-trigger span{font-size:9px;width:90px;left:calc(100% + 8px)}.ambient-line{display:none}
 .conversation{grid-column:2;grid-row:2;border-radius:23px}
 .conversation-head{height:36px;padding:0 11px}.conversation-head strong{font-size:11px}.conversation-head small{font-size:9px}
 .thread{padding:10px;gap:9px}.bubble{font-size:12px;padding:10px 12px}
 .composer{left:63px;right:9px;bottom:10px;min-height:57px;padding:5px 7px;gap:5px;border-radius:15px}
 .composer::before{width:24px;height:28px;font-size:20px}
 .composer textarea{min-height:42px;padding:10px 5px;font-size:12px}
 .send{height:40px;width:43px}
 .overlay{position:absolute;left:53px;top:7px;right:7px;bottom:76px;width:auto}
 .dialog{padding:10px;border-radius:22px}
 .theme-tile{min-height:75px}.theme-dot{width:35px;height:35px}
}
@media(max-height:650px) and (min-width:741px){
 .workspace{padding-bottom:84px}.orb{width:min(390px,100%,42vh)}
 .waveform{height:32px}.voice-trigger{width:48px;height:48px}.voice-trigger svg{width:21px}.core-status{min-height:32px;margin-top:0}
}
.cosmic-floor,.cosmic-skyline{position:absolute;left:0;right:0;z-index:0;pointer-events:none;
 filter:hue-rotate(var(--l-hue));background-size:100% 100%;background-position:center;opacity:.67}
.cosmic-floor{bottom:0;height:136px;background-image:url("data:image/webp;base64,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");animation:floorBreath 8s ease-in-out infinite;animation-play-state:var(--motion-play)}
.cosmic-skyline{top:0;height:70px;background-image:url("data:image/webp;base64,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");opacity:.7}
.topbar,.workspace{z-index:1}
@keyframes floorBreath{0%,100%{opacity:.52}50%{opacity:.8}}

</style>
</head>
<body>
<div class="shell" id="shell" data-state="idle">
  <div class="cosmic-skyline" aria-hidden="true"></div>
  <div class="cosmic-floor" aria-hidden="true"></div>
  <header class="topbar">
    <div class="identity" aria-label="Luna AI">
      <svg viewBox="0 0 40 40" aria-hidden="true"><path d="M20 3a17 17 0 1 0 17 24A16 16 0 0 1 20 3Z" fill="#ddafff"/></svg>
      <span>LUNA <em>AI</em></span>
    </div>
    <div class="top-center"><span class="pill"><span class="online-dot"></span> En línea</span>
      <span class="pill" id="brainChip">✧ Gemini <b>principal</b> · OpenRouter respaldo</span>
    </div>
    <div class="top-actions">
      <button class="icon-button" id="quickTheme" title="Cambiar color de Luna" aria-label="Cambiar tema de color">◈</button>
      <button class="icon-button" id="settingsButton" title="Configuración" aria-label="Configuración">⚙</button>
    </div>
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
      <div class="rail-bottom">LUNA · CELESTIAL</div>
    </nav>
    <section class="stage" aria-label="Núcleo visual de Luna">
      <div class="starfield" id="starfield" aria-hidden="true"></div>
      <svg class="constellation-sky" viewBox="0 0 480 440" preserveAspectRatio="none" aria-hidden="true">
        <g class="constellation"><polyline class="path" points="90,105 138,76 175,122 236,150 270,227 322,181 373,250"/>
          <circle class="point" cx="90" cy="105" r="2.5"/><circle class="point" cx="138" cy="76" r="3.5"/>
          <circle class="point" cx="175" cy="122" r="2.5"/><circle class="point" cx="236" cy="150" r="3"/>
          <circle class="point" cx="270" cy="227" r="2.5"/><circle class="point" cx="322" cy="181" r="3"/>
          <circle class="point" cx="373" cy="250" r="2.5"/></g>
        <g class="constellation"><polyline class="path" points="65,294 123,244 185,277 242,215 300,259"/>
          <circle class="point" cx="65" cy="294" r="3"/><circle class="point" cx="123" cy="244" r="2.5"/>
          <circle class="point" cx="185" cy="277" r="3.5"/><circle class="point" cx="242" cy="215" r="2.5"/>
          <circle class="point" cx="300" cy="259" r="3"/></g>
        <g class="constellation"><polyline class="path" points="86,170 147,132 207,162 254,212 317,197 380,144 405,102"/>
          <circle class="point" cx="86" cy="170" r="3"/><circle class="point" cx="147" cy="132" r="3.5"/>
          <circle class="point" cx="207" cy="162" r="2.5"/><circle class="point" cx="254" cy="212" r="3"/>
          <circle class="point" cx="317" cy="197" r="3.5"/><circle class="point" cx="380" cy="144" r="3"/>
          <circle class="point" cx="405" cy="102" r="2.5"/></g>
      </svg>
      <div class="stage-corners" aria-hidden="true"></div>
      <span class="tech-chip" aria-hidden="true">LUNA / SYNC 03</span>
      <span class="tech-chip right" aria-hidden="true">CELESTIAL · ACTIVE</span>
      <div class="eyebrow">✦  LUNA CORE  ·  CELESTIAL  ✦</div>
      <div class="orb" aria-hidden="true">
        <div class="cosmic-mist"></div><div class="cosmic-ring"></div>
        <div class="halo outer"></div><div class="halo middle"></div><div class="halo inner"></div><div class="halo ticks"></div>
        <div class="luna-art" aria-hidden="true"></div>
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
      <div class="waveform" id="visualizer" aria-hidden="true">
        <i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i>
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
        <div class="bubble luna"><span class="bubble-label">☾ LUNA</span>Hola, soy Luna. Ya estoy en línea. ¿Qué deseas hacer conmigo esta noche?</div>
      </div>
    </section>
    <div class="overlay" id="settingsOverlay" hidden>
      <section class="dialog" role="dialog" aria-modal="false" aria-labelledby="settingsTitle">
        <div class="settings-heading"><h2 id="settingsTitle">⚙ Ajustes de Luna</h2>
          <button class="settings-close" id="closeSettings" type="button" aria-label="Cerrar ajustes">×</button></div>
        <div class="settings-tabs" role="tablist" aria-label="Secciones de configuración">
          <button type="button" class="settings-tab" data-settings-tab="general" role="tab" aria-selected="false">☷ General</button>
          <button type="button" class="settings-tab" data-settings-tab="theme" role="tab" aria-selected="true">◈ Tema</button>
          <button type="button" class="settings-tab" data-settings-tab="voice" role="tab" aria-selected="false">♬ Voz</button>
        </div>
        <div class="settings-pane" data-settings-pane="theme" role="tabpanel">
          <div class="subhead">Tema de color</div>
          <p class="dialog-note">Personaliza el universo de Luna. Elige uno de los 25 colores o crea el tuyo.</p>
          <div class="theme-grid" id="themeGrid" role="group" aria-label="Temas de color"></div>
          <div class="custom-row">
            <label for="customColor">✦ Mi color</label>
            <input type="color" id="customColor" value="#bd46ff" aria-label="Elegir color principal">
            <button class="custom-btn" id="customApply" type="button">Aplicar</button>
          </div>
        </div>
        <div class="settings-pane" data-settings-pane="general" role="tabpanel" hidden>
          <div class="subhead">Inteligencia</div>
          <p class="dialog-note">Elige qué cerebro responde primero. El segundo quedará como respaldo.</p>
          <label class="setting" for="brainChoice">Cerebro principal
            <select id="brainChoice" class="brain-select">
              <option value="gemini">Gemini primero · OpenRouter respaldo</option>
              <option value="openrouter">OpenRouter primero · Gemini respaldo</option>
            </select>
          </label>
          <div class="subhead">Experiencia holográfica</div>
          <label class="setting">Animaciones del núcleo <input type="checkbox" id="motionToggle" checked></label>
          <label class="setting">Estrellas y constelaciones <input type="checkbox" id="skyToggle" checked></label>
          <label class="setting">Modo ligero <input type="checkbox" id="ecoToggle"></label>
        </div>
        <div class="settings-pane" data-settings-pane="voice" role="tabpanel" hidden>
          <div class="subhead">Voz de Luna</div>
          <label class="setting">Leer respuestas en voz alta <input type="checkbox" id="voiceToggle" checked></label>
          <p class="dialog-note">Luna utiliza ElevenLabs si está disponible. En caso contrario, intenta usar Microsoft Sabina y después responde por escrito.</p>
          <p class="dialog-note">Al dictar, tus palabras se acumulan. Luna solo envía la pregunta cuando pulsas «Terminar y enviar».</p>
        </div>
      </section>
    </div>
      <form class="composer" id="chatForm">
        <textarea id="userInput" rows="2" maxlength="2000" placeholder="Escribe o habla con Luna..." aria-label="Mensaje para Luna"></textarea>
        <button class="send" id="sendButton" type="submit"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 2 11 13M22 2l-7 20-4-9-9-4Z"/></svg><span>Enviar</span></button>
      </form>
  </main>
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
  const skyToggle = document.getElementById("skyToggle");
  const ecoToggle = document.getElementById("ecoToggle");
  const brainChoice = document.getElementById("brainChoice");
  const brainChip = document.getElementById("brainChip");
  const themeGrid = document.getElementById("themeGrid");
  const customColor = document.getElementById("customColor");
  const themeQuick = document.getElementById("quickTheme");
  let busy = false;
  let rec = null;
  let elevenUnavailable = false;
  // La pregunta no se enviara hasta pulsar «Terminar y enviar».
  let dictando = false;
  let textoAnterior = "";
  let segmentosGuardados = [];
  let finalesActuales = "";
  let parcialActual = "";
  let reintentosMicrofono = 0;
  let reinicioMicrofono = null;
  let enviandoDictado = false;
  let esperaCierre = null;


  // Preferencias de Luna: solo se guardan en el navegador, nunca las claves API.
  const preferenceKey = "luna-ai-prefs-v5";
  const themes = [
    {id:"violet",label:"Violeta Lunar",primary:"#bd46ff",secondary:"#ff52cd",base:"#070611",panel:"#110b20",panel2:"#1c1230",text:"#fbf4ff",muted:"#b8a5cd",light:false},
    {id:"scarlet",label:"Cyber Red",primary:"#ff355b",secondary:"#ff944c",base:"#100609",panel:"#200b12",panel2:"#34111c",text:"#fff3f5",muted:"#d6a9b3",light:false},
    {id:"azure",label:"Azul Estelar",primary:"#39a5ff",secondary:"#46eaff",base:"#050d18",panel:"#0a1728",panel2:"#10213a",text:"#eff9ff",muted:"#a0c1d9",light:false},
    {id:"solar",label:"Ámbar Solar",primary:"#ffbd35",secondary:"#ff7b35",base:"#120e06",panel:"#201808",panel2:"#352309",text:"#fff9ec",muted:"#d7c6a0",light:false},
    {id:"white",label:"Blanco Lunar",primary:"#8b70f5",secondary:"#80c5ff",base:"#f4f5fb",panel:"#ffffff",panel2:"#e7eaf5",text:"#20253a",muted:"#606982",light:true},
    {id:"obsidian",label:"Obsidiana",primary:"#929aae",secondary:"#d1d7e9",base:"#050508",panel:"#0e0e15",panel2:"#191923",text:"#f0f0f7",muted:"#a2a2b5",light:false},
    {id:"emerald",label:"Verde Quantum",primary:"#30efb7",secondary:"#58e3e7",base:"#03100d",panel:"#08231c",panel2:"#0e3429",text:"#e9fff7",muted:"#97c7b4",light:false},
    {id:"rose",label:"Rosa Nebulosa",primary:"#f961ac",secondary:"#d596ff",base:"#140813",panel:"#210e23",panel2:"#341637",text:"#fff1fb",muted:"#d4acce",light:false},
    {id:"plasma",label:"Plasma",primary:"#a129ff",secondary:"#ff1ef2",base:"#0b0415",panel:"#160921",panel2:"#220a32",text:"#fff1ff",muted:"#c5a7da",light:false},
    {id:"fuchsia",label:"Fucsia Cósmico",primary:"#ff28de",secondary:"#b12aff",base:"#130613",panel:"#250a25",panel2:"#360d37",text:"#fff0fb",muted:"#dfaad3",light:false},
    {id:"amethyst",label:"Amatista",primary:"#9769ff",secondary:"#d991ff",base:"#090618",panel:"#120c26",panel2:"#21133e",text:"#f8f2ff",muted:"#bcafdb",light:false},
    {id:"indigo",label:"Índigo",primary:"#6c60ff",secondary:"#b057ff",base:"#060617",panel:"#0c0e2c",panel2:"#17184a",text:"#f4f4ff",muted:"#acacdc",light:false},
    {id:"sapphire",label:"Zafiro",primary:"#176bff",secondary:"#55aeff",base:"#040a18",panel:"#0a1632",panel2:"#0d2250",text:"#edf4ff",muted:"#aac3e9",light:false},
    {id:"aqua",label:"Aqua Galáctico",primary:"#11edec",secondary:"#4abfff",base:"#031219",panel:"#06222a",panel2:"#0c3844",text:"#e7ffff",muted:"#8abdc8",light:false},
    {id:"mint",label:"Menta Astral",primary:"#76ffcb",secondary:"#53c8ff",base:"#061410",panel:"#0b251c",panel2:"#103a2c",text:"#effff9",muted:"#a5dac7",light:false},
    {id:"jade",label:"Jade",primary:"#00d78b",secondary:"#6affd2",base:"#04120c",panel:"#092217",panel2:"#0c3523",text:"#effff7",muted:"#99d1b3",light:false},
    {id:"lime",label:"Lima Nuclear",primary:"#b3ff46",secondary:"#4bff9d",base:"#0b1204",panel:"#162009",panel2:"#24340e",text:"#f5ffe9",muted:"#b6d19e",light:false},
    {id:"ruby",label:"Rubí",primary:"#ff215e",secondary:"#ff6294",base:"#16040a",panel:"#270813",panel2:"#3d0a1c",text:"#fff0f6",muted:"#e0a7b8",light:false},
    {id:"coral",label:"Coral",primary:"#ff6e77",secondary:"#ffb17b",base:"#170a0d",panel:"#281216",panel2:"#3b1c22",text:"#fff6f4",muted:"#dfb8b4",light:false},
    {id:"sunset",label:"Atardecer",primary:"#ff753b",secondary:"#fc45aa",base:"#16090a",panel:"#2a1111",panel2:"#3e1b17",text:"#fff4e9",muted:"#ddafa5",light:false},
    {id:"copper",label:"Cobre",primary:"#cc824a",secondary:"#ffc38c",base:"#120b07",panel:"#21140e",panel2:"#352015",text:"#fff5e9",muted:"#d2b7a3",light:false},
    {id:"pearl",label:"Perla",primary:"#a09bcc",secondary:"#decfff",base:"#faf8ff",panel:"#ffffff",panel2:"#efebfa",text:"#29243b",muted:"#746d85",light:true},
    {id:"midnight",label:"Medianoche",primary:"#5476bb",secondary:"#8f6db8",base:"#03060f",panel:"#080d1b",panel2:"#121a2e",text:"#f0f4ff",muted:"#9ca9c0",light:false},
    {id:"graphite",label:"Grafito",primary:"#c0c0cb",secondary:"#7d8da6",base:"#090a0d",panel:"#15161b",panel2:"#23252d",text:"#f7f7fb",muted:"#b1b3c0",light:false},
    {id:"lilac",label:"Lavanda",primary:"#c69fff",secondary:"#f2c2ff",base:"#100b18",panel:"#1b1228",panel2:"#2b1c3b",text:"#fdf6ff",muted:"#cab8dc",light:false}
  ];
  let prefs = {theme:"violet",custom:"#bd46ff",brain:"gemini",motion:true,sky:true,eco:false,voice:true};
  try {
    const previousPrefs = JSON.parse(localStorage.getItem(preferenceKey) || "{}");
    if (previousPrefs && typeof previousPrefs === "object" && !Array.isArray(previousPrefs)) {
      for (const key of Object.keys(prefs)) {
        if (Object.prototype.hasOwnProperty.call(previousPrefs,key)) prefs[key] = previousPrefs[key];
      }
    }
  } catch (_) {} // En modo privado puede estar bloqueado.
  function savePrefs(){try{localStorage.setItem(preferenceKey,JSON.stringify(prefs));}catch(_){}}
  function validHex(value){return typeof value === "string" && /^#[0-9a-fA-F]{6}$/.test(value);}
  function rgbOf(hex){return [1,3,5].map(i=>parseInt(hex.slice(i,i+2),16)).join(",");}
  function lightenHex(hex,amount){
    return "#"+[1,3,5].map(i=>Math.round(parseInt(hex.slice(i,i+2),16)+(255-parseInt(hex.slice(i,i+2),16))*amount).toString(16).padStart(2,"0")).join("");
  }
  function darkenHex(hex,amount){
    return "#"+[1,3,5].map(i=>Math.round(parseInt(hex.slice(i,i+2),16)*(1-amount)).toString(16).padStart(2,"0")).join("");
  }
  function hexHue(hex){
    const r=parseInt(hex.slice(1,3),16)/255, g=parseInt(hex.slice(3,5),16)/255, b=parseInt(hex.slice(5,7),16)/255;
    const max=Math.max(r,g,b), min=Math.min(r,g,b), diff=max-min;
    if(diff===0) return 0;
    let h=max===r ? ((g-b)/diff)%6 : max===g ? (b-r)/diff+2 : (r-g)/diff+4;
    return (h*60+360)%360;
  }
  function colorTheme(id){
    if (id==="custom") {
      const primary = validHex(prefs.custom) ? prefs.custom : "#bd46ff";
      return {id:"custom",label:"Personalizado",primary,secondary:lightenHex(primary,.38),base:"#060810",panel:"#0d1220",panel2:"#191d31",text:"#f7f9ff",muted:"#aebcd2",light:false};
    }
    return themes.find(t=>t.id===id) || themes[0];
  }
  function applyTheme(id,save=true){
    const theme = colorTheme(id);
    const root = document.documentElement;
    root.dataset.theme = theme.id;
    root.classList.toggle("theme-light",theme.light);
    root.style.setProperty("--l-hue",((hexHue(theme.primary)-hexHue("#bd46ff")+360)%360)+"deg");
    root.style.setProperty("--l-primary",theme.primary);
    root.style.setProperty("--l-secondary",theme.secondary);
    root.style.setProperty("--l-accent",theme.primary);
    root.style.setProperty("--l-primary-rgb",rgbOf(theme.primary));
    root.style.setProperty("--l-secondary-rgb",rgbOf(theme.secondary));
    root.style.setProperty("--l-base",theme.base);
    root.style.setProperty("--l-panel",theme.panel);
    root.style.setProperty("--l-panel2",theme.panel2);
    root.style.setProperty("--l-text",theme.text);
    root.style.setProperty("--l-muted",theme.muted);
    root.style.setProperty("--l-border",`rgba(${rgbOf(theme.primary)},${theme.light?.37:.27})`);
    root.style.setProperty("--l-moon1",theme.light?"#fcffff":lightenHex(theme.primary,.90));
    root.style.setProperty("--l-moon2",lightenHex(theme.primary,.63));
    root.style.setProperty("--l-moon3",darkenHex(theme.primary,.35));
    document.querySelector('meta[name="theme-color"]').setAttribute("content",theme.base);
    document.querySelectorAll(".theme-tile").forEach(btn=>btn.setAttribute("aria-pressed",String(btn.dataset.themeId===theme.id)));
    themeQuick.title = "Tema actual: " + theme.label + " · Cambiar color";
    if(save){prefs.theme=theme.id;savePrefs();}
  }
  function makeThemeButtons(){
    for(const theme of themes){
      const btn=document.createElement("button");
      btn.type="button";btn.className="theme-tile";btn.dataset.themeId=theme.id;
      btn.setAttribute("aria-label","Activar tema "+theme.label);
      const colors=document.createElement("span");colors.className="theme-swatches";
      const dot=document.createElement("span");dot.className="theme-dot";
      dot.style.setProperty("--swatch-main",theme.primary);
      dot.style.setProperty("--swatch-secondary",theme.secondary);
      colors.appendChild(dot);
      const name=document.createElement("small");name.textContent=theme.label;
      btn.append(colors,name);btn.addEventListener("click",()=>applyTheme(theme.id));themeGrid.appendChild(btn);
    }
    const custom=document.createElement("button");custom.type="button";custom.className="theme-tile";custom.dataset.themeId="custom";
    custom.setAttribute("aria-label","Activar último color personalizado");
    custom.innerHTML='<span class="theme-swatches"><span class="theme-dot" id="customDot"></span></span><small>Mi color</small>';
    custom.addEventListener("click",()=>applyTheme("custom"));themeGrid.appendChild(custom);
  }
  makeThemeButtons();
  const settingsTabs = Array.from(document.querySelectorAll("[data-settings-tab]"));
  const settingsPanes = Array.from(document.querySelectorAll("[data-settings-pane]"));
  function showSettingsTab(name){
    for (const tab of settingsTabs) tab.setAttribute("aria-selected", String(tab.dataset.settingsTab === name));
    for (const pane of settingsPanes) pane.hidden = pane.dataset.settingsPane !== name;
  }
  for (const tab of settingsTabs) tab.addEventListener("click",()=>showSettingsTab(tab.dataset.settingsTab));
  showSettingsTab("theme");
  if(!validHex(prefs.custom)) prefs.custom="#bd46ff";
  customColor.value=prefs.custom;
  const customDot=document.getElementById("customDot");
  function refreshCustomDot(){customDot.style.setProperty("--swatch-main",prefs.custom);customDot.style.setProperty("--swatch-secondary",lightenHex(prefs.custom,.35));}
  refreshCustomDot();
  document.getElementById("customApply").addEventListener("click",()=>{
    prefs.custom=customColor.value;refreshCustomDot();applyTheme("custom");
  });
  const themeSequence=themes.map(t=>t.id);
  themeQuick.addEventListener("click",()=>{
    const index=themeSequence.indexOf(prefs.theme);
    applyTheme(themeSequence[(index+1)%themeSequence.length]);
  });
  applyTheme(prefs.theme,false);
  motionToggle.checked=prefs.motion!==false;
  skyToggle.checked=prefs.sky!==false;
  ecoToggle.checked=prefs.eco===true;
  voiceToggle.checked=prefs.voice!==false;
  brainChoice.value=prefs.brain==="openrouter"?"openrouter":"gemini";
  document.documentElement.classList.toggle("motion-off",!motionToggle.checked);
  document.documentElement.classList.toggle("sky-off",!skyToggle.checked);
  document.documentElement.classList.toggle("eco",ecoToggle.checked);
  document.documentElement.style.setProperty("--motion-play",motionToggle.checked?"running":"paused");
  function updateBrainBadge(){
    brainChip.textContent = brainChoice.value==="openrouter"
      ? "◇ OpenRouter principal · Gemini respaldo"
      : "✧ Gemini principal · OpenRouter respaldo";
    brainInfo.textContent = "Preferido: " + (brainChoice.value==="openrouter"?"OpenRouter":"Gemini");
  }
  updateBrainBadge();
  brainChoice.addEventListener("change",()=>{prefs.brain=brainChoice.value;savePrefs();updateBrainBadge();});
  skyToggle.addEventListener("change",()=>{prefs.sky=skyToggle.checked;document.documentElement.classList.toggle("sky-off",!prefs.sky);savePrefs();});
  ecoToggle.addEventListener("change",()=>{prefs.eco=ecoToggle.checked;document.documentElement.classList.toggle("eco",prefs.eco);savePrefs();});
  voiceToggle.addEventListener("change",()=>{prefs.voice=voiceToggle.checked;savePrefs();});
  // El usuario controla por completo la activación de las animaciones.
  motionToggle.addEventListener("change",()=>{prefs.motion=motionToggle.checked;savePrefs();});

  // Estrellas de fondo, distribuidas una sola vez. Sin Canvas ni dependencias externas.
  const starfield = document.getElementById("starfield");
  for (let index = 0; index < 42; index++) {
    const spark = document.createElement("span");
    spark.className = "spark" + (index % 6 === 0 ? " magenta" : "");
    spark.style.left = ((index * 37 + 13) % 97 + 1) + "%";
    spark.style.top = ((index * 29 + (index * index) % 23) % 89 + 4) + "%";
    spark.style.animationDelay = -(index % 17) * .31 + "s";
    spark.style.animationDuration = (2.2 + (index % 7) * .51) + "s";
    starfield.appendChild(spark);
  }
  const waveBars = Array.from(document.querySelectorAll("#visualizer i"));
  let audioStream = null;
  let audioContext = null;
  let audioAnalyser = null;
  let frequencies = null;
  let audioAnimationId = null;
  let audioSessionId = 0;
  let audioLastFrame = 0;

  function stopMicrophoneVisualization() {
    audioSessionId++;
    if (audioAnimationId !== null) cancelAnimationFrame(audioAnimationId);
    audioAnimationId = null;
    shell.dataset.micLive = "false";
    for (const bar of waveBars) bar.style.removeProperty("transform");
    if (audioStream) {
      for (const track of audioStream.getTracks()) track.stop();
      audioStream = null;
    }
    if (audioContext) {
      audioContext.close().catch(() => {});
      audioContext = null;
    }
    audioAnalyser = null;
    frequencies = null;
  }

  // Web Audio muestra el volumen real del micrófono cuando Chrome lo permite.
  // Si el navegador bloquea una segunda captura, continúa la animación CSS.
  async function startMicrophoneVisualization() {
    if (audioStream || audioContext || !dictando || !motionToggle.checked) return;
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) return;
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    if (!AudioCtx) return;
    const sessionId = ++audioSessionId;
    let stream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({audio:{echoCancellation:true,noiseSuppression:true}});
      if (sessionId !== audioSessionId || !dictando || !motionToggle.checked) {
        for (const track of stream.getTracks()) track.stop();
        return;
      }
      audioStream = stream;
      audioContext = new AudioCtx();
      const source = audioContext.createMediaStreamSource(audioStream);
      audioAnalyser = audioContext.createAnalyser();
      audioAnalyser.fftSize = 256;
      audioAnalyser.smoothingTimeConstant = .68;
      source.connect(audioAnalyser);
      frequencies = new Uint8Array(audioAnalyser.frequencyBinCount);
      await audioContext.resume();
      if (sessionId !== audioSessionId || !dictando) {stopMicrophoneVisualization();return;}
      shell.dataset.micLive = "true";
      function draw(now) {
        if (sessionId !== audioSessionId || !dictando || !audioAnalyser || !motionToggle.checked) return;
        audioAnimationId = requestAnimationFrame(draw);
        if (now - audioLastFrame < 45) return; // unas 22 actualizaciones/s
        audioLastFrame = now;
        audioAnalyser.getByteFrequencyData(frequencies);
        const count = waveBars.length;
        for (let i = 0; i < count; i++) {
          // Combinación de bandas bajas y medias de voz, con rango mínimo visible.
          const bin = Math.min(frequencies.length-1, 2+Math.floor(i*1.2));
          const v = (frequencies[bin] + frequencies[Math.min(frequencies.length-1,bin+2)]) / 510;
          const center = 1-Math.abs(i-(count-1)/2)/((count-1)/2);
          const amp = Math.min(.98, .1 + Math.pow(v, .72)*1.8*(.6+.4*center));
          waveBars[i].style.transform = "scaleY(" + amp.toFixed(3) + ")";
        }
      }
      audioAnimationId = requestAnimationFrame(draw);
    } catch (_) {
      // Fallo visual no afecta al dictado: las barras CSS siguen animadas.
      if (stream && stream !== audioStream) for (const track of stream.getTracks()) track.stop();
      stopMicrophoneVisualization();
    }
  }

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
  function actualizarDictado() {
    input.value = [textoAnterior, ...segmentosGuardados, finalesActuales, parcialActual]
      .map(t => t.trim()).filter(Boolean).join(" ").slice(0, 2000);
    input.scrollTop = input.scrollHeight;
  }
  function stopRecognition() {
    stopMicrophoneVisualization();
    dictando = false;
    enviandoDictado = false;
    if (reinicioMicrofono !== null) {
      clearTimeout(reinicioMicrofono);
      reinicioMicrofono = null;
    }
    if (esperaCierre !== null) {
      clearTimeout(esperaCierre);
      esperaCierre = null;
    }
    if (rec) {
      const previous = rec;
      rec = null;
      previous.onresult = null;
      previous.onend = null;
      previous.onerror = null;
      try { previous.abort(); } catch (_) {}
    }
    micText.textContent = "Hablar con Luna";
    buttons();
  }

  // Finalizar sin perder la última parte reconocida por Chrome.
  // Esta es la ÚNICA ruta del dictado que puede enviar la pregunta.
  function finalizarDictado() {
    if (!enviandoDictado) return;
    const fragmento = [finalesActuales, parcialActual].filter(Boolean).join(" ").trim();
    if (fragmento) segmentosGuardados.push(fragmento);
    finalesActuales = "";
    parcialActual = "";
    actualizarDictado();
    const pregunta = input.value.trim();
    stopRecognition();
    if (pregunta) {
      askLuna(pregunta);
    } else {
      setState("idle", "Luna está lista", "No se escuchó ninguna pregunta. Inténtalo de nuevo.");
    }
  }

  function terminarYEnviar() {
    if (!dictando || enviandoDictado || busy) return;
    stopMicrophoneVisualization();
    dictando = false;
    enviandoDictado = true;
    if (reinicioMicrofono !== null) {
      clearTimeout(reinicioMicrofono);
      reinicioMicrofono = null;
    }
    micText.textContent = "Terminando...";
    micButton.disabled = true;
    setState("listening", "Terminando dictado", "Guardando las últimas palabras antes de enviar...");
    if (rec) {
      // Respaldo por si el navegador no dispara el evento onend.
      esperaCierre = setTimeout(finalizarDictado, 1800);
      try { rec.stop(); } catch (_) { finalizarDictado(); }
    } else {
      finalizarDictado();
    }
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
        method:"POST", headers:{"Content-Type":"application/json"},
        body:JSON.stringify({message,model_preference:brainChoice.value})
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
  form.addEventListener("submit", event => {
    event.preventDefault();
    if (dictando) { terminarYEnviar(); return; }
    if (!enviandoDictado) askLuna(input.value);
  });
  input.addEventListener("keydown", event => {
    if (event.key === "Enter" && !event.shiftKey && !event.isComposing) {
      event.preventDefault();
      if (dictando) terminarYEnviar();
      else if (!enviandoDictado) askLuna(input.value);
    }
  });
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

  function comenzarSesionVoz() {
    if (!dictando || busy) return;
    const recognition = new SpeechRecognition();
    rec = recognition;
    finalesActuales = "";
    parcialActual = "";
    recognition.lang = "es-DO";
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;
    recognition.onstart = () => {
      if (rec !== recognition) return;
      startMicrophoneVisualization();
      micText.textContent = "Terminar y enviar";
      setState("listening", "Luna te escucha", "Habla sin prisa. Pulsa «Terminar y enviar» cuando acabes.");
    };
    recognition.onresult = event => {
      if (rec !== recognition || busy || (!dictando && !enviandoDictado)) return;
      const finales = [];
      const parciales = [];
      for (let i = 0; i < event.results.length; i++) {
        const resultado = event.results[i];
        const fragmento = resultado[0].transcript.trim();
        if (resultado.isFinal) finales.push(fragmento);
        else parciales.push(fragmento);
      }
      finalesActuales = finales.join(" ").trim();
      parcialActual = parciales.join(" ").trim();
      actualizarDictado();
    };
    recognition.onerror = event => {
      if (rec !== recognition || !dictando) return;
      if (["not-allowed", "service-not-allowed", "audio-capture", "network"].includes(event.error)) {
        actualizarDictado();
        stopRecognition();
        setState("idle", "Micrófono no disponible", "El navegador informó: " + event.error + ". Puedes enviar el texto escrito.");
      }
    };
    recognition.onend = () => {
      if (rec !== recognition) return;
      rec = null;
      if (enviandoDictado) { finalizarDictado(); return; }
      const fragmento = [finalesActuales, parcialActual].filter(Boolean).join(" ").trim();
      if (fragmento) segmentosGuardados.push(fragmento);
      finalesActuales = "";
      parcialActual = "";
      actualizarDictado();
      if (!dictando || busy) return;
      // Una sesión puede terminar sola. Reiniciamos SIN enviar la pregunta.
      reintentosMicrofono = fragmento ? 0 : reintentosMicrofono + 1;
      if (reintentosMicrofono > 7) {
        stopRecognition();
        setState("idle", "Dictado pausado", "Chrome interrumpió varias sesiones. Tu texto se conserva; revisa y pulsa Enviar.");
        return;
      }
      reinicioMicrofono = setTimeout(() => {
        reinicioMicrofono = null;
        if (dictando && !busy) comenzarSesionVoz();
      }, 350);
    };
    try {
      recognition.start();
    } catch (_) {
      rec = null;
      stopRecognition();
      setState("idle", "Micrófono no disponible", "No se pudo iniciar el reconocimiento. Puedes escribir tu pregunta.");
    }
  }

  function listen() {
    if (busy || enviandoDictado) return;
    if (dictando) { terminarYEnviar(); return; }
    if (!SpeechRecognition) {
      setState("idle", "Micrófono no disponible", "Utiliza Chrome con reconocimiento de voz o escribe tu mensaje.");
      return;
    }
    dictando = true;
    textoAnterior = input.value.trim();
    segmentosGuardados = [];
    finalesActuales = "";
    parcialActual = "";
    reintentosMicrofono = 0;
    micText.textContent = "Terminar y enviar";
    setState("listening", "Luna te escucha", "Puedes hablar una frase larga. Pulsa «Terminar y enviar» cuando acabes.");
    comenzarSesionVoz();
  }
  micButton.addEventListener("click",listen);
  document.getElementById("navVoice").addEventListener("click",listen);
  document.getElementById("navChat").addEventListener("click",()=>input.focus());
  function showSettings(){settings.hidden=false;showSettingsTab("theme");document.getElementById("closeSettings").focus({preventScroll:true});}
  function hideSettings(){settings.hidden=true;document.getElementById("settingsButton").focus();}
  document.getElementById("settingsButton").addEventListener("click",showSettings);
  document.getElementById("navSettings").addEventListener("click",showSettings);
  document.getElementById("closeSettings").addEventListener("click",hideSettings);
  settings.addEventListener("click",e=>{if(e.target===settings)hideSettings();});
  document.addEventListener("keydown",e=>{if(e.key==="Escape"&&!settings.hidden)hideSettings();});
  motionToggle.addEventListener("change",()=>{
    document.documentElement.classList.toggle("motion-off", !motionToggle.checked);
    document.documentElement.style.setProperty("--motion-play", motionToggle.checked ? "running" : "paused");
    if (!motionToggle.checked) stopMicrophoneVisualization();
    else if (dictando) startMicrophoneVisualization();
  });
  // Respetar la elección guardada del usuario desde el primer render.
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
# LUNA AI — Selección de cerebro con respaldo
# Sin cambiar las claves existentes en Render.
# ==========================================

def _gemini_answer(message, instrucciones):
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        raise RuntimeError("Gemini sin clave configurada")
    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        "models/gemini-3.1-flash-lite:generateContent"
    )
    payload = {
        "systemInstruction": {"parts": [{"text": instrucciones}]},
        "contents": [{"role": "user", "parts": [{"text": message}]}],
        "generationConfig": {"maxOutputTokens": 512},
    }
    req = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-goog-api-key": key},
        method="POST",
    )
    with urlopen(req, timeout=25) as response:
        result = json.load(response)
    candidates = result.get("candidates") or []
    parts = (
        candidates[0].get("content", {}).get("parts", [])
        if candidates and isinstance(candidates[0], dict) else []
    )
    answer = "".join(
        part.get("text", "") for part in parts
        if isinstance(part, dict) and not part.get("thought")
    ).strip()
    if not answer:
        raise ValueError("Gemini devolvió una respuesta vacía")
    return {"reply": answer, "brain": "Gemini"}


def _openrouter_answer(message, instrucciones):
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not key:
        raise RuntimeError("OpenRouter sin clave configurada")
    payload = {
        "model": "openrouter/free",
        "messages": [
            {"role": "system", "content": instrucciones},
            {"role": "user", "content": message},
        ],
        "max_tokens": 512,
    }
    req = Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
            "X-Title": "Luna AI",
        },
        method="POST",
    )
    with urlopen(req, timeout=40) as response:
        result = json.load(response)
    choices = result.get("choices") or []
    if not choices:
        raise ValueError("OpenRouter no devolvió respuestas")
    content = choices[0].get("message", {}).get("content", "")
    if isinstance(content, list):
        answer = "".join(
            item.get("text", "") for item in content
            if isinstance(item, dict)
        ).strip()
    elif isinstance(content, str):
        answer = content.strip()
    else:
        answer = ""
    if not answer:
        raise ValueError("OpenRouter devolvió una respuesta vacía")
    return {
        "reply": answer,
        "brain": "OpenRouter",
        "model": result.get("model", "openrouter/free"),
    }


@app.post("/api/chat")
def chat():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()
    if not message or len(message) > 2000:
        return jsonify(error="Escribe un mensaje de hasta 2000 caracteres."), 400

    now = datetime.now(ZoneInfo("America/Santo_Domingo"))
    weekdays = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
    months = [
        "enero", "febrero", "marzo", "abril", "mayo", "junio",
        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
    ]
    fecha = f"{weekdays[now.weekday()]} {now.day} de {months[now.month-1]} de {now.year}"
    hora = now.strftime("%H:%M")
    instrucciones = (
        "Eres Luna, una asistente personal femenina, amable, inteligente, "
        "tierna y comprensiva. Habla naturalmente en español. "
        "Responde de forma clara y normalmente breve. "
        "No repitas innecesariamente las respuestas. "
        "Tu personalidad es cercana y conversacional. "
        "No inventes información que desconozcas. "
        f"La fecha actual en República Dominicana es {fecha}. "
        f"La hora local es {hora}. "
        "Utiliza esa fecha para responder preguntas temporales."
    )

    preference = str(data.get("model_preference", "gemini")).lower()
    order = (
        [("OpenRouter", _openrouter_answer), ("Gemini", _gemini_answer)]
        if preference == "openrouter" else
        [("Gemini", _gemini_answer), ("OpenRouter", _openrouter_answer)]
    )
    errors = []
    for name, provider in order:
        try:
            response = provider(message, instrucciones)
            response["preferred_brain"] = order[0][0]
            return jsonify(response)
        except HTTPError as error:
            app.logger.warning("%s devolvió HTTP %s", name, error.code)
            errors.append(f"{name}: HTTP {error.code}")
        except (URLError, TimeoutError):
            app.logger.warning("No se pudo conectar con %s", name)
            errors.append(f"{name}: sin conexión")
        except (ValueError, KeyError, TypeError, RuntimeError) as error:
            app.logger.warning("%s no pudo responder: %s", name, str(error)[:160])
            errors.append(f"{name}: {str(error)[:80]}")
    return jsonify(error="Los dos cerebros están indisponibles. " + " | ".join(errors)), 503


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
