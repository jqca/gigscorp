"""
有限会社ギグス コーポレートサイト
Routes:
  GET  /          - ホーム
  GET  /akiya     - 空き家ビジネス
  GET  /company   - 会社概要
  GET  /contact   - お問い合わせ
  POST /api/contact - お問い合わせ送信API
"""
import os
from flask import Flask, render_template_string, request, jsonify
from datetime import timedelta

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'gigscorp-2024')

SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY', '')
CONTACT_EMAIL    = os.getenv('CONTACT_EMAIL', 'info@gigscorp.jp')

# ─────────────────────────────────────────────────────────────
#  共通パーツ
# ─────────────────────────────────────────────────────────────
COMMON_CSS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  html { scroll-behavior: smooth; }
  body { font-family: 'Noto Sans JP', 'Hiragino Sans', sans-serif; background: #f7f9fb; color: #1f2937; line-height: 1.75; }
  a { color: inherit; text-decoration: none; }
  img { display: block; max-width: 100%; }

  /* ── NAV ── */
  nav {
    position: fixed; top: 0; left: 0; right: 0; z-index: 200;
    background: rgba(255,255,255,0.96); backdrop-filter: blur(12px);
    border-bottom: 1px solid #e5e7eb;
    height: 68px; padding: 0 40px;
    display: flex; align-items: center; justify-content: space-between;
    box-shadow: 0 1px 8px rgba(0,0,0,0.07);
  }
  .nav-brand { display: flex; align-items: center; gap: 10px; }
  .nav-logo-mark {
    width: 44px; height: 44px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
  }
  .nav-logo-mark img { width: 44px; height: 44px; object-fit: contain; }
  .nav-logo-text { line-height: 1.1; }
  .nav-logo-ja { font-size: 0.95rem; font-weight: 900; color: #0f3460; }
  .nav-logo-en { font-size: 0.62rem; color: #6b7280; letter-spacing: 0.1em; }
  .nav-links { display: flex; gap: 32px; list-style: none; }
  .nav-links a { font-size: 0.88rem; font-weight: 600; color: #374151; transition: color 0.2s; position: relative; padding-bottom: 4px; }
  .nav-links a::after { content: ''; position: absolute; bottom: 0; left: 0; width: 0; height: 2px; background: #0f3460; transition: width 0.3s; }
  .nav-links a:hover { color: #0f3460; }
  .nav-links a:hover::after { width: 100%; }
  .nav-cta {
    background: linear-gradient(135deg, #0f3460, #16534a);
    color: #fff; padding: 10px 22px; border-radius: 8px;
    font-size: 0.84rem; font-weight: 700;
    box-shadow: 0 4px 14px rgba(15,52,96,0.25); transition: transform 0.2s, box-shadow 0.2s;
  }
  .nav-cta:hover { transform: translateY(-1px); box-shadow: 0 6px 20px rgba(15,52,96,0.35); }
  @media (max-width: 768px) { .nav-links { display: none; } nav { padding: 0 20px; } }

  /* ── SECTION BASE ── */
  section { padding: 92px 24px; }
  .si { max-width: 1120px; margin: 0 auto; }
  .tag {
    display: inline-block; font-size: 0.7rem; font-weight: 800;
    letter-spacing: 0.18em; padding: 5px 14px; border-radius: 20px; margin-bottom: 12px;
  }
  .tag-navy { background: #e0e7f3; color: #0f3460; }
  .tag-green { background: #d1ede5; color: #16534a; }
  .tag-gold  { background: #fdf0d3; color: #9a6c00; }
  .tag-gray  { background: #f3f4f6; color: #4b5563; }
  .h2 { font-size: clamp(1.8rem,3.5vw,2.6rem); font-weight: 900; color: #0f172a; line-height: 1.22; letter-spacing: -0.02em; margin-bottom: 14px; }
  .lead { font-size: 1rem; color: #4b5563; line-height: 1.85; max-width: 640px; }
  .tc { text-align: center; }
  .tc .lead { margin: 0 auto; }

  /* ── BUTTONS ── */
  .btn-primary {
    display: inline-flex; align-items: center; gap: 8px;
    background: linear-gradient(135deg, #0f3460, #16534a); color: #fff;
    padding: 14px 32px; border-radius: 8px; font-weight: 700; font-size: 0.95rem;
    box-shadow: 0 6px 20px rgba(15,52,96,0.28); transition: transform 0.2s, box-shadow 0.2s;
  }
  .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 10px 28px rgba(15,52,96,0.38); }
  .btn-outline {
    display: inline-flex; align-items: center; gap: 8px;
    border: 2px solid #0f3460; color: #0f3460;
    padding: 12px 28px; border-radius: 8px; font-weight: 700; font-size: 0.93rem;
    transition: background 0.2s, color 0.2s;
  }
  .btn-outline:hover { background: #0f3460; color: #fff; }

  /* ── FOOTER ── */
  footer { background: #0f172a; color: rgba(255,255,255,0.65); padding: 56px 40px 32px; }
  .footer-inner { max-width: 1120px; margin: 0 auto; }
  .footer-top { display: grid; grid-template-columns: 1.5fr 1fr 1fr 1fr; gap: 48px; padding-bottom: 40px; border-bottom: 1px solid rgba(255,255,255,0.1); }
  @media (max-width: 768px) { .footer-top { grid-template-columns: 1fr 1fr; gap: 28px; } }
  .footer-brand { }
  .footer-logo-ja { font-size: 1.1rem; font-weight: 900; color: #fff; margin-bottom: 4px; }
  .footer-logo-en { font-size: 0.72rem; color: rgba(255,255,255,0.4); letter-spacing: 0.12em; margin-bottom: 16px; }
  .footer-desc { font-size: 0.83rem; line-height: 1.85; color: rgba(255,255,255,0.5); }
  .footer-col h4 { font-size: 0.8rem; font-weight: 700; color: rgba(255,255,255,0.9); margin-bottom: 16px; letter-spacing: 0.06em; }
  .footer-col ul { list-style: none; }
  .footer-col li { margin-bottom: 10px; }
  .footer-col a { font-size: 0.82rem; color: rgba(255,255,255,0.5); transition: color 0.2s; }
  .footer-col a:hover { color: rgba(255,255,255,0.85); }
  .footer-bottom { display: flex; justify-content: space-between; align-items: center; padding-top: 24px; flex-wrap: wrap; gap: 12px; }
  .footer-bottom p { font-size: 0.76rem; color: rgba(255,255,255,0.3); }
  .footer-license { font-size: 0.76rem; color: rgba(255,255,255,0.35); text-align: right; line-height: 1.7; }

  /* ── IMG FALLBACK ── */
  .img-fallback { background: linear-gradient(135deg, #0f3460, #16534a); }
</style>
"""

def nav_html(active=""):
    pages = [("ホーム","/"),("空き家サービス","/akiya"),("会社概要","/company"),("お問い合わせ","/contact")]
    links = "".join(f'<li><a href="{u}">{n}</a></li>' for n,u in pages)
    return f"""
<nav>
  <a href="/" class="nav-brand">
    <div class="nav-logo-mark"><img src="/static/images/logo.png" alt="有限会社ギグス ロゴ"></div>
    <div class="nav-logo-text">
      <div class="nav-logo-ja">有限会社ギグス</div>
      <div class="nav-logo-en">GIGS CORP.</div>
    </div>
  </a>
  <ul class="nav-links">{links}</ul>
  <a href="/contact" class="nav-cta">無料相談はこちら</a>
</nav>"""

def akiya_nav_html():
    """空き家サービスページ専用ナビ"""
    return """
<nav>
  <a href="/akiya" class="nav-brand" style="text-decoration:none;">
    <div class="nav-logo-mark" style="width:36px;height:36px;font-size:1.4rem;display:flex;align-items:center;justify-content:center;">🏠</div>
    <div class="nav-logo-text">
      <div class="nav-logo-ja" style="font-size:0.88rem;">空き家管理サポート</div>
      <div class="nav-logo-en" style="font-size:0.6rem;">有限会社ギグス</div>
    </div>
  </a>
  <ul class="nav-links">
    <li><a href="/akiya/service">サービスについて</a></li>
    <li><a href="/akiya/service#price">料金の目安</a></li>
    <li><a href="/akiya#faq">よくある質問</a></li>
    <li><a href="/company">会社案内</a></li>
  </ul>
  <a href="/contact?subject=akiya_free" class="nav-cta" style="background:linear-gradient(135deg,#2d7a3e,#1e5c2d);">無料で状態を確認する</a>
</nav>"""

FOOTER_HTML = """
<footer>
  <div class="footer-inner">
    <div class="footer-top">
      <div class="footer-brand">
        <div class="footer-logo-ja">有限会社ギグス</div>
        <div class="footer-logo-en">GIGS CORP.</div>
        <p class="footer-desc">不動産の売買・仲介・コンサルティングから空き家ビジネス・M&A仲介まで、お客様の資産価値最大化を総合的にサポートします。</p>
      </div>
      <div class="footer-col">
        <h4>サービス</h4>
        <ul>
          <li><a href="/akiya">空き家ビジネス</a></li>
          <li><a href="/#services">不動産売買仲介</a></li>
          <li><a href="/#services">不動産コンサルティング</a></li>
          <li><a href="/#services">M&A仲介</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>会社情報</h4>
        <ul>
          <li><a href="/company">会社概要</a></li>
          <li><a href="/company#philosophy">経営理念</a></li>
          <li><a href="/company#license">免許・資格</a></li>
          <li><a href="/contact">採用情報</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>お問い合わせ</h4>
        <ul>
          <li><a href="/contact">無料相談フォーム</a></li>
          <li><a href="tel:07083943791">070-8394-3791</a></li>
          <li><a href="mailto:info@gigscorp.jp">info@gigscorp.jp</a></li>
          <li><a href="/akiya#faq">よくある質問</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <p>&copy; 2024 有限会社ギグス (GIGS CORP.) All rights reserved.</p>
      <div class="footer-license">
        宅地建物取引士 / 1級建築施工管理技士<br>
        不動産コンサルティングマスター / AFP
      </div>
    </div>
  </div>
</footer>"""

# ─────────────────────────────────────────────────────────────
#  ホーム
# ─────────────────────────────────────────────────────────────
HOME_HTML = """<!DOCTYPE html>
<html lang="ja"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>有限会社ギグス | 地主・不動産オーナーの長期パートナー</title>
<meta name="description" content="空き家の確認から、資産活用の相談、事業の将来まで。有限会社ギグスは不動産オーナー・地主の方の「次の一手」を長期的にサポートします。東京都文京区本駒込。">
%(CSS)s
<style>
  /* HERO */
  .hero { position:relative; min-height:100vh; display:flex; align-items:center; overflow:hidden; padding:120px 24px 80px; }
  .hero-bg { position:absolute; inset:0; background:url('/static/images/hero.png') center/cover no-repeat; }
  .hero-bg::after { content:''; position:absolute; inset:0; background:linear-gradient(100deg,rgba(10,25,60,0.90) 0%,rgba(10,25,60,0.72) 55%,rgba(10,25,60,0.25) 100%); }
  .hero-inner { position:relative; z-index:1; max-width:640px; }
  .hero-eyebrow { display:inline-flex; align-items:center; gap:8px; background:rgba(255,255,255,0.12); border:1px solid rgba(255,255,255,0.22); color:#93c5fd; padding:7px 18px; border-radius:30px; font-size:0.78rem; font-weight:700; letter-spacing:0.12em; margin-bottom:28px; }
  .hero h1 { font-size:clamp(2.2rem,5vw,3.6rem); font-weight:900; color:#fff; line-height:1.2; letter-spacing:-0.02em; margin-bottom:20px; }
  .hero h1 em { font-style:normal; color:#fcd34d; }
  .hero-sub { font-size:1.02rem; color:rgba(255,255,255,0.78); line-height:1.9; margin-bottom:40px; max-width:500px; }
  .hero-btns { display:flex; gap:14px; flex-wrap:wrap; margin-bottom:52px; }
  .btn-hero-p { background:linear-gradient(135deg,#2d7a3e,#1e5c2d); color:#fff; padding:16px 36px; border-radius:8px; font-weight:800; font-size:0.98rem; box-shadow:0 6px 24px rgba(45,122,62,0.4); transition:transform 0.2s,box-shadow 0.2s; }
  .btn-hero-p:hover { transform:translateY(-2px); box-shadow:0 10px 32px rgba(45,122,62,0.5); }
  .btn-hero-s { border:2px solid rgba(255,255,255,0.4); color:#fff; padding:14px 32px; border-radius:8px; font-weight:700; font-size:0.95rem; transition:background 0.2s; }
  .btn-hero-s:hover { background:rgba(255,255,255,0.12); }
  .hero-trust { display:flex; gap:28px; flex-wrap:wrap; padding-top:36px; border-top:1px solid rgba(255,255,255,0.18); }
  .trust-pill { display:flex; align-items:center; gap:8px; color:rgba(255,255,255,0.72); font-size:0.82rem; font-weight:600; }
  .trust-dot { width:8px; height:8px; border-radius:50%; background:#fcd34d; flex-shrink:0; }

  /* NUMBERS */
  .numbers { background:#0f3460; padding:52px 24px; }
  .num-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:0; max-width:960px; margin:0 auto; }
  @media(max-width:640px){.num-grid{grid-template-columns:repeat(2,1fr);}}
  .num-item { text-align:center; padding:24px 16px; border-right:1px solid rgba(255,255,255,0.12); }
  .num-item:last-child { border-right:none; }
  .num-val { font-size:2.4rem; font-weight:900; color:#fcd34d; line-height:1; }
  .num-unit { font-size:0.85rem; color:#fcd34d; }
  .num-label { font-size:0.78rem; color:rgba(255,255,255,0.55); margin-top:6px; }

  /* PERSONA */
  .persona { background:#f7f9fb; padding:80px 24px; }
  .persona-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin-top:44px; }
  @media(max-width:768px){ .persona-grid { grid-template-columns:repeat(2,1fr); } }
  @media(max-width:480px){ .persona-grid { grid-template-columns:1fr; } }
  .persona-card { background:#fff; border-radius:16px; padding:24px 20px; border:1.5px solid #e5e7eb; transition:border-color 0.2s,box-shadow 0.2s; }
  .persona-card:hover { border-color:#0f3460; box-shadow:0 4px 20px rgba(15,52,96,0.08); }
  .persona-ico { font-size:1.8rem; margin-bottom:12px; }
  .persona-card h4 { font-size:0.9rem; font-weight:800; color:#0f172a; margin-bottom:8px; line-height:1.4; }
  .persona-card p { font-size:0.8rem; color:#6b7280; line-height:1.7; }

  /* JOURNEY SERVICES */
  .services { background:#fff; padding:92px 24px; }
  .journey-wrap { margin-top:60px; display:flex; flex-direction:column; gap:0; }

  /* STEP 1: 空き家（入口） */
  .je-entry { background:#f0faf3; border:1.5px solid #a7d4b3; border-radius:20px; padding:36px 40px; display:flex; align-items:center; gap:32px; position:relative; }
  @media(max-width:768px){ .je-entry { flex-direction:column; padding:28px 24px; gap:20px; } }
  .je-step-label { position:absolute; top:-14px; left:32px; background:#2d7a3e; color:#fff; font-size:0.68rem; font-weight:800; letter-spacing:0.12em; padding:4px 14px; border-radius:20px; }
  .je-icon-wrap { width:72px; height:72px; border-radius:16px; background:#fff; border:1.5px solid #a7d4b3; display:flex; align-items:center; justify-content:center; font-size:2.2rem; flex-shrink:0; }
  .je-text { flex:1; }
  .je-text h3 { font-size:1.15rem; font-weight:900; color:#1e5c2d; margin-bottom:8px; }
  .je-text p { font-size:0.88rem; color:#374151; line-height:1.8; }
  .je-free { background:#2d7a3e; color:#fff; font-size:0.7rem; font-weight:800; letter-spacing:0.1em; padding:5px 14px; border-radius:20px; white-space:nowrap; flex-shrink:0; }
  .je-link { display:inline-flex; align-items:center; gap:4px; margin-top:12px; font-size:0.85rem; font-weight:700; color:#2d7a3e; }
  .je-link::after { content:'→'; }

  /* ARROW */
  .journey-arrow { text-align:center; padding:20px 0; color:#9ca3af; font-size:0.82rem; font-weight:600; display:flex; align-items:center; justify-content:center; gap:8px; }
  .journey-arrow::before, .journey-arrow::after { content:''; display:block; width:60px; height:1px; background:#e5e7eb; }

  /* STEP 2: 不動産コンサル（本業） */
  .jm-main { background:linear-gradient(135deg,#0f3460 0%,#1a4a7a 100%); border-radius:20px; padding:48px 48px; position:relative; overflow:hidden; }
  @media(max-width:768px){ .jm-main { padding:36px 24px; } }
  .jm-main::before { content:''; position:absolute; right:-60px; top:-60px; width:280px; height:280px; border-radius:50%; background:rgba(255,255,255,0.04); }
  .jm-step-label { display:inline-block; background:rgba(252,211,77,0.2); color:#fcd34d; font-size:0.68rem; font-weight:800; letter-spacing:0.12em; padding:4px 14px; border-radius:20px; margin-bottom:20px; }
  .jm-inner { display:grid; grid-template-columns:1fr 1fr; gap:48px; align-items:start; }
  @media(max-width:768px){ .jm-inner { grid-template-columns:1fr; gap:28px; } }
  .jm-left h3 { font-size:clamp(1.4rem,2.5vw,1.9rem); font-weight:900; color:#fff; line-height:1.3; margin-bottom:14px; }
  .jm-left p { font-size:0.9rem; color:rgba(255,255,255,0.72); line-height:1.85; margin-bottom:28px; }
  .btn-gold { display:inline-flex; align-items:center; gap:8px; background:linear-gradient(135deg,#e8a020,#c47d10); color:#fff; padding:14px 28px; border-radius:8px; font-weight:800; font-size:0.9rem; box-shadow:0 6px 20px rgba(232,160,32,0.35); transition:transform 0.2s; }
  .btn-gold:hover { transform:translateY(-2px); }
  .jm-axes { display:grid; grid-template-columns:1fr 1fr; gap:12px; }
  .jm-axis { background:rgba(255,255,255,0.08); border:1px solid rgba(255,255,255,0.12); border-radius:12px; padding:18px 20px; }
  .jm-axis-ico { font-size:1.4rem; margin-bottom:8px; }
  .jm-axis h4 { font-size:0.85rem; font-weight:800; color:#fff; margin-bottom:4px; }
  .jm-axis p { font-size:0.78rem; color:rgba(255,255,255,0.55); line-height:1.6; }

  /* STEP 3: M&A（奥・控えめ） */
  .jb-back { background:#f8f9fa; border:1px solid #e5e7eb; border-radius:16px; padding:24px 32px; display:flex; align-items:center; gap:20px; flex-wrap:wrap; margin-top:0; }
  .jb-ico { font-size:1.6rem; flex-shrink:0; }
  .jb-text { flex:1; min-width:200px; }
  .jb-text strong { font-size:0.92rem; font-weight:800; color:#374151; display:block; margin-bottom:4px; }
  .jb-text span { font-size:0.82rem; color:#6b7280; line-height:1.7; }
  .jb-link { display:inline-flex; align-items:center; gap:4px; font-size:0.82rem; font-weight:700; color:#6b7280; border:1px solid #d1d5db; padding:8px 18px; border-radius:8px; transition:color 0.2s,border-color 0.2s; white-space:nowrap; }
  .jb-link:hover { color:#0f3460; border-color:#0f3460; }

  /* AKIYA FEATURE */
  .akiya-feature { background:linear-gradient(135deg,#0f3460 0%,#16534a 100%); padding:92px 24px; }
  .af-inner { max-width:1120px; margin:0 auto; display:grid; grid-template-columns:1fr 1fr; gap:64px; align-items:center; }
  @media(max-width:768px){.af-inner{grid-template-columns:1fr;}}
  .af-img { border-radius:20px; overflow:hidden; box-shadow:0 24px 64px rgba(0,0,0,0.3); }
  .af-img img { width:100%; height:360px; object-fit:cover; }
  .af-content { color:#fff; }
  .af-tag { background:rgba(252,211,77,0.2); color:#fcd34d; font-size:0.72rem; font-weight:800; letter-spacing:0.15em; padding:5px 14px; border-radius:20px; display:inline-block; margin-bottom:16px; }
  .af-content h2 { font-size:clamp(1.7rem,3vw,2.4rem); font-weight:900; line-height:1.25; margin-bottom:18px; }
  .af-content p { font-size:0.95rem; color:rgba(255,255,255,0.78); line-height:1.85; margin-bottom:24px; }
  .af-points { list-style:none; margin-bottom:36px; }
  .af-points li { display:flex; align-items:flex-start; gap:10px; font-size:0.9rem; color:rgba(255,255,255,0.85); padding:8px 0; border-bottom:1px solid rgba(255,255,255,0.1); }
  .af-points li::before { content:'✓'; color:#fcd34d; font-weight:900; flex-shrink:0; margin-top:2px; }
  .btn-gold-af { background:linear-gradient(135deg,#e8a020,#c47d10); color:#fff; padding:14px 32px; border-radius:8px; font-weight:800; font-size:0.95rem; box-shadow:0 6px 20px rgba(232,160,32,0.35); transition:transform 0.2s; display:inline-flex; align-items:center; gap:8px; }
  .btn-gold-af:hover { transform:translateY(-2px); }

  /* STRENGTHS */
  .strengths { background:#f7f9fb; }
  .str-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:24px; margin-top:56px; }
  @media(max-width:640px){.str-grid{grid-template-columns:1fr;}}
  .str-card { background:#fff; border-radius:20px; padding:36px 28px; border:1px solid #e5e7eb; transition:box-shadow 0.3s; }
  .str-card:hover { box-shadow:0 8px 32px rgba(0,0,0,0.08); }
  .str-num { font-size:3rem; font-weight:900; color:#e8e8e8; line-height:1; margin-bottom:8px; }
  .str-icon { font-size:2rem; margin-bottom:14px; }
  .str-card h3 { font-size:1.1rem; font-weight:800; color:#0f172a; margin-bottom:10px; }
  .str-card p { font-size:0.86rem; color:#4b5563; line-height:1.8; }

  /* CTA */
  .cta-section { background:#fff; }
  .cta-box { background:linear-gradient(135deg,#0f3460,#16534a); border-radius:24px; padding:64px 48px; text-align:center; color:#fff; }
  @media(max-width:640px){ .cta-box { padding:44px 24px; } }
  .cta-box h2 { font-size:clamp(1.7rem,3vw,2.4rem); font-weight:900; margin-bottom:14px; }
  .cta-box p { font-size:1rem; color:rgba(255,255,255,0.75); margin-bottom:36px; }
  .cta-btns { display:flex; gap:14px; justify-content:center; flex-wrap:wrap; }
  .btn-white { background:#fff; color:#0f3460; padding:14px 32px; border-radius:8px; font-weight:800; font-size:0.95rem; transition:opacity 0.2s; }
  .btn-white:hover { opacity:0.9; }
  .btn-white-outline { border:2px solid rgba(255,255,255,0.5); color:#fff; padding:14px 32px; border-radius:8px; font-weight:700; font-size:0.93rem; transition:background 0.2s; }
  .btn-white-outline:hover { background:rgba(255,255,255,0.1); }
</style>
</head>
<body>
%(NAV)s

<!-- ─── HERO ─── -->
<section class="hero">
  <div class="hero-bg"></div>
  <div class="hero-inner">
    <div class="hero-eyebrow">地主・不動産オーナーの方へ</div>
    <h1>物件のことも、<br>会社の将来も。<br><em>ひとつの窓口で。</em></h1>
    <p class="hero-sub">空き家の確認から始まり、資産活用のご相談、そして必要なら事業の承継まで。ギグスはあなたの状況を丸ごと知っている、長期パートナーでありたいと思っています。</p>
    <div class="hero-btns">
      <a href="/akiya" class="btn-hero-p">まず空き家の状態を確認する（無料）</a>
      <a href="/contact" class="btn-hero-s">不動産の相談をする</a>
    </div>
    <div class="hero-trust">
      <div class="trust-pill"><span class="trust-dot"></span>創業2006年・18年の実績</div>
      <div class="trust-pill"><span class="trust-dot"></span>宅建士・不動産コンサルマスター</div>
      <div class="trust-pill"><span class="trust-dot"></span>秘密厳守・しつこい営業なし</div>
    </div>
  </div>
</section>

<!-- ─── NUMBERS ─── -->
<div class="numbers">
  <div class="num-grid">
    <div class="num-item"><div class="num-val">18<span class="num-unit">年</span></div><div class="num-label">不動産業界での実績</div></div>
    <div class="num-item"><div class="num-val">宅建<span class="num-unit">士</span></div><div class="num-label">コンサルマスター取得</div></div>
    <div class="num-item"><div class="num-val">無料<span class="num-unit">から</span></div><div class="num-label">空き家確認スタート</div></div>
    <div class="num-item"><div class="num-val">全国<span class="num-unit">対応</span></div><div class="num-label">ご相談・調査エリア</div></div>
  </div>
</div>

<!-- ─── PERSONA ─── -->
<section class="persona">
  <div class="si">
    <div class="tc">
      <span class="tag tag-navy">OWNER'S CONCERNS</span>
      <h2 class="h2">こんな方にご相談いただいています</h2>
      <p class="lead">「不動産を持っているオーナー」に共通する悩みに、ひとつの窓口でお応えします。</p>
    </div>
    <div class="persona-grid">
      <div class="persona-card">
        <div class="persona-ico">🏠</div>
        <h4>遠方の実家や空き家が気になっている</h4>
        <p>「特に困っていないが、少し気になる」という方。まず現状確認だけでも。</p>
      </div>
      <div class="persona-card">
        <div class="persona-ico">📋</div>
        <h4>相続した物件の活用をどうすべきか迷っている</h4>
        <p>売る・貸す・維持する——選択肢の整理からお手伝いします。</p>
      </div>
      <div class="persona-card">
        <div class="persona-ico">🏗️</div>
        <h4>土地や物件をもっと活かしたいと思っている</h4>
        <p>賃貸経営・土地活用・売却タイミングなど戦略的に考えたい方へ。</p>
      </div>
      <div class="persona-card">
        <div class="persona-ico">🤝</div>
        <h4>会社や事業の将来について考え始めている</h4>
        <p>後継者がいない、売却を考えている。まず話を聞いてほしい方へ。</p>
      </div>
    </div>
  </div>
</section>

<!-- ─── JOURNEY SERVICES ─── -->
<section class="services" id="services">
  <div class="si">
    <div class="tc">
      <span class="tag tag-navy">SERVICES</span>
      <h2 class="h2">オーナーの「次の一手」を、段階的にサポート</h2>
      <p class="lead">まず気軽に話せる入口から始まり、本格的な資産活用の相談へ。必要な方には事業の出口まで。ギグスはそのすべてに対応できる存在です。</p>
    </div>

    <div class="journey-wrap">

      <!-- STEP 1: 空き家（入口） -->
      <div class="je-entry">
        <span class="je-step-label">STEP 1 ── まずはここから</span>
        <div class="je-icon-wrap">🏠</div>
        <div class="je-text">
          <h3>空き家の「今の状態」を、無料でお伝えします</h3>
          <p>お困りでなくても大丈夫です。「少し気になる」という段階で十分。外観確認・写真共有・簡単なコメントを無料で行います。文京区を中心に対応。判断はそのあとで。</p>
          <a href="/akiya" class="je-link">空き家サービスの詳細を見る</a>
        </div>
        <span class="je-free">無料から</span>
      </div>

      <!-- ARROW -->
      <div class="journey-arrow">そのまま、資産活用のご相談へ</div>

      <!-- STEP 2: 不動産コンサル（本業） -->
      <div class="jm-main">
        <span class="jm-step-label">CORE — 本業・中核サービス</span>
        <div class="jm-inner">
          <div class="jm-left">
            <h3>物件を、どう活かすか。<br>一緒に考えます。</h3>
            <p>売る・貸す・活用する・相続に備える——正解はお客様の状況によって変わります。18年の経験と宅建士・不動産コンサルマスターの資格で、あなたに合ったプランを提案します。営業はしません。まず話を聞かせてください。</p>
            <a href="/contact" class="btn-gold">不動産の相談をする →</a>
          </div>
          <div class="jm-axes">
            <div class="jm-axis">
              <div class="jm-axis-ico">🏷️</div>
              <h4>売却・売買仲介</h4>
              <p>住宅・ビル・土地。適正価格での売却を丁寧にサポート。</p>
            </div>
            <div class="jm-axis">
              <div class="jm-axis-ico">🏘️</div>
              <h4>賃貸・土地活用</h4>
              <p>遊んでいる物件を収益化。最適な活用方法をご提案。</p>
            </div>
            <div class="jm-axis">
              <div class="jm-axis-ico">⚖️</div>
              <h4>相続・資産対策</h4>
              <p>相続が発生する前から。税対策・名義変更の整理まで。</p>
            </div>
            <div class="jm-axis">
              <div class="jm-axis-ico">📊</div>
              <h4>資産運用・戦略</h4>
              <p>複数物件のポートフォリオ最適化。長期的視点で助言。</p>
            </div>
          </div>
        </div>
      </div>

      <!-- ARROW -->
      <div class="journey-arrow">さらに必要な方へ</div>

      <!-- STEP 3: M&A（奥・控えめ） -->
      <div class="jb-back">
        <span class="jb-ico">🤝</span>
        <div class="jb-text">
          <strong>事業承継・M&A仲介</strong>
          <span>会社や事業の将来についても、ご相談いただけます。後継者問題・売却・買収——内容を問わず、まず話を聞かせてください。秘密厳守で対応します。</span>
        </div>
        <a href="/contact?subject=ma" class="jb-link">個別相談へ →</a>
      </div>

    </div><!-- /journey-wrap -->
  </div>
</section>

<!-- ─── AKIYA FEATURE ─── -->
<section class="akiya-feature">
  <div class="af-inner">
    <div class="af-img">
      <img src="/static/images/akiya_hero.png" onerror="this.parentElement.style.background='linear-gradient(135deg,#0a2040,#0f3460)';this.remove()" alt="空き家管理サポート">
    </div>
    <div class="af-content">
      <span class="af-tag">空き家管理サポート ── まずはここから</span>
      <h2>空き家の"今の状態"を、<br>まず無料でお伝えします。</h2>
      <p>特にお困りでなくても大丈夫です。「少し気になる」という段階で、いきなり管理を勧めることはしません。まず現在の状態をお伝えし、判断はそのあとで。文京区を中心に対応しています。</p>
      <ul class="af-points">
        <li>外観確認・写真共有・簡単なコメントを無料で実施</li>
        <li>AIライトプランは月3,000円から。必要な方だけご利用ください</li>
        <li>草刈り・清掃・修繕などの個別対応も承ります</li>
        <li>遠方にお住まいの方も安心してご相談ください</li>
      </ul>
      <a href="/akiya" class="btn-gold-af">空き家サービスの詳細を見る →</a>
    </div>
  </div>
</section>

<!-- ─── STRENGTHS ─── -->
<section class="strengths">
  <div class="si">
    <div class="tc">
      <span class="tag tag-green">WHY GIGS</span>
      <h2 class="h2">オーナーがギグスを選ぶ理由</h2>
      <p class="lead">「この人に任せれば大丈夫」と思っていただけるよう、3つのことを大切にしています。</p>
    </div>
    <div class="str-grid">
      <div class="str-card">
        <div class="str-num">01</div>
        <div class="str-icon">🛡️</div>
        <h3>しつこい営業・特別な契約、一切なし</h3>
        <p>「まず話を聞くだけ」で構いません。相談したからといって、契約を急かすことはしません。お客様のペースを尊重します。</p>
      </div>
      <div class="str-card">
        <div class="str-num">02</div>
        <div class="str-icon">📋</div>
        <h3>不動産×M&Aを一人で見られる専門家</h3>
        <p>宅建士・不動産コンサルマスター・AFPを保有。物件の相談が、いつのまにか事業の将来の話になっても、同じ窓口で対応できます。</p>
      </div>
      <div class="str-card">
        <div class="str-num">03</div>
        <div class="str-icon">⏱️</div>
        <h3>2営業日以内に返答。迅速・丁寧に</h3>
        <p>お問い合わせから2営業日以内にご連絡します。お客様一人ひとりの状況をヒアリングした上で、最適な提案をします。</p>
      </div>
    </div>
  </div>
</section>

<!-- ─── CTA ─── -->
<section class="cta-section">
  <div class="si">
    <div class="cta-box">
      <h2>物件のことも、会社の将来も、<br>まずご相談ください</h2>
      <p>空き家の無料確認から、不動産活用、事業承継まで。<br>ギグスはオーナーの長期パートナーです。</p>
      <div class="cta-btns">
        <a href="/akiya" class="btn-white">空き家の状態を確認する（無料）</a>
        <a href="/contact" class="btn-white-outline">不動産・その他の相談をする</a>
      </div>
    </div>
  </div>
</section>

%(FOOTER)s
</body></html>"""

# ─────────────────────────────────────────────────────────────
#  空き家サービス TOPページ
# ─────────────────────────────────────────────────────────────
AKIYA_HTML = """<!DOCTYPE html>
<html lang="ja"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>空き家の今の状態を無料でお伝えします | 空き家管理サポート（有限会社ギグス）</title>
<meta name="description" content="特にお困りでなくても大丈夫です。まずは空き家の今の状態だけ確認してみませんか。外観確認・写真共有・簡単なコメントを無料で行います。文京区の空き家管理なら有限会社ギグス。">
%(CSS)s
<style>
  /* ── AKIYA TOP PAGE STYLES ── */
  :root { --g: #2d7a3e; --gl: #e8f5ed; --gb: #a7d4b3; --gd: #1e5c2d; --navy: #1d3461; }

  /* HERO */
  .ak-hero { position:relative; min-height:90vh; display:flex; align-items:center; padding:100px 40px 60px; overflow:hidden; background:#fff; }
  .ak-hero-bg { position:absolute; right:0; top:0; bottom:0; width:50%; background:url('/static/images/akiya_hero.png') center/cover no-repeat; }
  .ak-hero-bg::after { content:''; position:absolute; inset:0; background:linear-gradient(to right, rgba(255,255,255,1) 0%, rgba(255,255,255,0.4) 50%, rgba(255,255,255,0) 100%); }
  @media(max-width:768px){ .ak-hero-bg { width:100%; opacity:0.15; } .ak-hero { min-height:auto; padding:100px 24px 56px; } }
  .ak-hero-inner { position:relative; z-index:1; max-width:540px; }
  .ak-eyebrow { display:inline-block; background:#f0f9f3; border:1px solid var(--gb); color:var(--g); font-size:0.82rem; font-weight:700; padding:6px 16px; border-radius:20px; margin-bottom:24px; }
  .ak-hero h1 { font-size:clamp(1.8rem,4vw,2.8rem); font-weight:900; color:#1a1a2e; line-height:1.3; margin-bottom:16px; }
  .ak-hero h1 em { font-style:normal; color:var(--g); }
  .ak-hero-sub { font-size:1rem; color:#4b5563; line-height:1.85; margin-bottom:36px; }
  .ak-hero-btns { display:flex; gap:12px; flex-wrap:wrap; }
  .btn-green { display:inline-flex; align-items:center; gap:8px; background:linear-gradient(135deg,var(--g),var(--gd)); color:#fff; padding:14px 28px; border-radius:8px; font-weight:800; font-size:0.95rem; box-shadow:0 6px 20px rgba(45,122,62,0.3); transition:transform 0.2s,box-shadow 0.2s; }
  .btn-green:hover { transform:translateY(-2px); box-shadow:0 10px 28px rgba(45,122,62,0.4); }
  .btn-green-outline { display:inline-flex; align-items:center; gap:8px; border:2px solid var(--g); color:var(--g); padding:12px 24px; border-radius:8px; font-weight:700; font-size:0.9rem; transition:background 0.2s,color 0.2s; }
  .btn-green-outline:hover { background:var(--g); color:#fff; }

  /* WHO */
  .who-sec { background:#f8faf8; padding:72px 24px; }
  .who-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:20px; margin-top:40px; }
  @media(max-width:640px){ .who-grid { grid-template-columns:1fr; } }
  .who-card { background:#fff; border-radius:16px; padding:28px 22px; text-align:center; border:1px solid #e5e7eb; }
  .who-ico { font-size:2rem; margin-bottom:12px; }
  .who-card p { font-size:0.9rem; color:#374151; font-weight:600; line-height:1.55; }

  /* FREE BOX */
  .free-sec { background:#fff; padding:72px 24px; }
  .free-grid { display:grid; grid-template-columns:1fr 1fr; gap:28px; margin-top:40px; }
  @media(max-width:768px){ .free-grid { grid-template-columns:1fr; } }
  .free-box { background:var(--gl); border:1px solid var(--gb); border-radius:20px; padding:32px 28px; }
  .free-box h3 { font-size:1rem; font-weight:900; color:var(--gd); margin-bottom:20px; }
  .free-item { display:flex; align-items:flex-start; gap:12px; margin-bottom:14px; }
  .free-ico { width:36px; height:36px; border-radius:8px; background:#fff; border:1px solid var(--gb); display:flex; align-items:center; justify-content:center; font-size:1.1rem; flex-shrink:0; }
  .free-item p { font-size:0.9rem; color:#374151; line-height:1.6; font-weight:600; }
  .free-note { font-size:0.78rem; color:#6b7280; margin-top:16px; padding-top:14px; border-top:1px solid var(--gb); line-height:1.7; }
  .why-box { background:#fff; border:1px solid #e5e7eb; border-radius:20px; padding:32px 28px; }
  .why-box h3 { font-size:1rem; font-weight:900; color:#1a1a2e; margin-bottom:16px; }
  .why-box p { font-size:0.9rem; color:#374151; line-height:1.85; }
  .why-box .highlight { color:var(--g); font-weight:700; }

  /* TRUST BADGES */
  .trust-row { display:flex; gap:20px; flex-wrap:wrap; margin-top:32px; }
  .trust-badge { display:flex; align-items:center; gap:8px; font-size:0.88rem; color:#374151; font-weight:600; }
  .trust-check { width:22px; height:22px; border-radius:50%; background:var(--g); display:flex; align-items:center; justify-content:center; color:#fff; font-size:0.7rem; font-weight:900; flex-shrink:0; }

  /* BANNER CTA */
  .banner-sec { background:var(--navy); padding:40px 24px; }
  .banner-inner { max-width:960px; margin:0 auto; display:flex; align-items:center; justify-content:space-between; gap:24px; flex-wrap:wrap; }
  .banner-inner p { color:rgba(255,255,255,0.9); font-size:1rem; font-weight:700; }
  .banner-inner small { display:block; color:rgba(255,255,255,0.55); font-size:0.82rem; font-weight:400; margin-top:4px; }
  .btn-banner { background:#fff; color:var(--navy); padding:12px 28px; border-radius:8px; font-weight:800; font-size:0.92rem; white-space:nowrap; transition:opacity 0.2s; display:inline-flex; align-items:center; gap:6px; }
  .btn-banner:hover { opacity:0.88; }

  /* CONTACT ROW */
  .contact-row-sec { background:#f8faf8; padding:60px 24px; }
  .contact-row-inner { max-width:900px; margin:0 auto; text-align:center; }
  .contact-row-inner h2 { font-size:1.3rem; font-weight:900; color:#1a1a2e; margin-bottom:6px; }
  .contact-row-inner p { font-size:0.9rem; color:#4b5563; margin-bottom:28px; }
  .contact-methods { display:flex; gap:16px; justify-content:center; flex-wrap:wrap; }
  .c-method { background:#fff; border:1.5px solid #e5e7eb; border-radius:14px; padding:18px 24px; display:flex; flex-direction:column; align-items:center; gap:6px; min-width:180px; transition:border-color 0.2s,box-shadow 0.2s; }
  .c-method:hover { border-color:var(--g); box-shadow:0 4px 16px rgba(45,122,62,0.12); }
  .c-method .c-icon { font-size:1.6rem; }
  .c-method .c-label { font-size:0.72rem; color:#6b7280; }
  .c-method .c-val { font-size:0.9rem; font-weight:800; color:#1a1a2e; }
  .c-method .c-sub { font-size:0.72rem; color:#9ca3af; }

  /* FAQ */
  .faq-sec { background:#fff; padding:72px 24px; }
  .faq-list { max-width:720px; margin:40px auto 0; }
  .faq-item { border-bottom:1px solid #e5e7eb; }
  .faq-q { width:100%; background:none; border:none; color:#1a1a2e; text-align:left; padding:18px 0; font-size:0.93rem; font-weight:700; cursor:pointer; display:flex; justify-content:space-between; align-items:center; gap:16px; font-family:inherit; }
  .faq-icon { width:26px; height:26px; border-radius:50%; background:var(--gl); display:flex; align-items:center; justify-content:center; font-size:1rem; color:var(--g); flex-shrink:0; transition:transform 0.3s,background 0.3s; }
  .faq-item.open .faq-icon { transform:rotate(45deg); background:var(--g); color:#fff; }
  .faq-a { display:none; padding:0 0 18px; font-size:0.88rem; color:#4b5563; line-height:1.85; }
  .faq-item.open .faq-a { display:block; }
</style>
</head>
<body>
%(NAV)s

<!-- HERO -->
<section class="ak-hero">
  <div class="ak-hero-bg"></div>
  <div class="ak-hero-inner">
    <div class="ak-eyebrow">特にお困りでなくても大丈夫です。</div>
    <h1>空き家の<em>"今の状態"</em>を<br>無料でお伝えします</h1>
    <p class="ak-hero-sub">まずは<strong>"今どうなっているか"</strong>だけ<br>確認してみませんか？</p>
    <div class="ak-hero-btns">
      <a href="/contact?subject=akiya_free" class="btn-green">
        <span>✉</span> 無料で状態を確認する <span>›</span>
      </a>
      <a href="/akiya/service" class="btn-green-outline">どんな内容か見る ›</a>
    </div>
  </div>
</section>

<!-- こんな方が増えています -->
<section class="who-sec">
  <div class="si">
    <div class="tc">
      <h2 class="h2" style="font-size:clamp(1.3rem,2.5vw,1.8rem);color:#1a1a2e;">こんな方が増えています</h2>
    </div>
    <div class="who-grid">
      <div class="who-card">
        <div class="who-ico">📍</div>
        <p>使っていないが、<br>特に困っていない</p>
      </div>
      <div class="who-card">
        <div class="who-ico">🚗</div>
        <p>遠方で様子が<br>分からない</p>
      </div>
      <div class="who-card">
        <div class="who-ico">🏠</div>
        <p>管理まではまだ<br>考えていない</p>
      </div>
    </div>
  </div>
</section>

<!-- 無料で行うこと + なぜ無料か -->
<section class="free-sec">
  <div class="si">
    <div class="free-grid">
      <div class="free-box">
        <h3>🏠 無料で行うこと</h3>
        <div class="free-item">
          <div class="free-ico">🏠</div>
          <p>外観の確認<br><span style="font-weight:400;font-size:0.83rem;color:#6b7280;">（建物・敷地まわり）</span></p>
        </div>
        <div class="free-item">
          <div class="free-ico">📷</div>
          <p>写真1〜2枚の共有</p>
        </div>
        <div class="free-item">
          <div class="free-ico">💬</div>
          <p>簡単なコメント</p>
        </div>
        <div class="free-note">
          ※ 敷地内には立ち入りません<br>
          ※ 作業は行いません
        </div>
        <div class="trust-row" style="margin-top:24px;padding-top:20px;border-top:1px solid var(--gb);">
          <div class="trust-badge"><div class="trust-check">✓</div> 1回だけでもOK</div>
          <div class="trust-badge"><div class="trust-check">✓</div> 継続の必要はありません</div>
          <div class="trust-badge"><div class="trust-check">✓</div> 営業はいたしません</div>
        </div>
      </div>
      <div class="why-box">
        <h3>なぜ無料で確認しているのか</h3>
        <p>
          空き家については、「特に困ってはいないが、少し気になる」という方がたくさんいらっしゃいます。<br><br>
          この段階で、いきなり管理や費用のご提案をすることは、かえってご負担になると考えています。<br><br>
          そのため当社では、まず<strong class="highlight">現在の状態を知っていただくこと</strong>を目的に、外観の確認と簡単なレポートを無料で行っています。<br><br>
          <strong class="highlight">判断は、そのあとで大丈夫です。</strong>
        </p>
        <div style="margin-top:24px;padding:16px 18px;background:#f8faf8;border-radius:10px;border-left:3px solid var(--g);">
          <p style="font-size:0.83rem;color:#4b5563;line-height:1.8;">
            ちなみに、文京区でも空き家は年々増えています。全国的な課題ですが、地域での小さなサポートが積み重なることで、街の安心につながると考え、この取り組みをはじめました。
          </p>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- 管理・お手入れバナー -->
<div class="banner-sec">
  <div class="banner-inner">
    <div>
      <p>👤 必要に応じて、管理やお手入れも対応可能です。
        <small>状況を確認した上で、ご希望の場合のみご提案します。</small>
      </p>
    </div>
    <a href="/akiya/service" class="btn-banner">空き家サービスの詳細を見る ›</a>
  </div>
</div>

<!-- FAQ -->
<section class="faq-sec" id="faq">
  <div class="si">
    <div class="tc">
      <h2 class="h2" style="font-size:clamp(1.3rem,2.5vw,1.8rem);">よくある質問</h2>
    </div>
    <div class="faq-list">
      <div class="faq-item">
        <button class="faq-q">無料確認は、1回だけでも依頼できますか？<div class="faq-icon">+</div></button>
        <div class="faq-a">はい、もちろんです。「まず1回だけ様子を見てほしい」というご依頼も歓迎しています。継続のご契約は一切必要ありません。</div>
      </div>
      <div class="faq-item">
        <button class="faq-q">遠方に住んでいて、物件に行けないのですが大丈夫ですか？<div class="faq-icon">+</div></button>
        <div class="faq-a">大丈夫です。当社が現地に伺い、外観の写真とコメントをメール等でお送りします。お客様にお越しいただく必要はありません。</div>
      </div>
      <div class="faq-item">
        <button class="faq-q">空き家が文京区以外にあります。対応してもらえますか？<div class="faq-icon">+</div></button>
        <div class="faq-a">物件の場所によりご相談ください。文京区およびその近隣エリアを中心に対応しております。まずはお気軽にお問い合わせください。</div>
      </div>
      <div class="faq-item">
        <button class="faq-q">無料確認の後、しつこく営業されませんか？<div class="faq-icon">+</div></button>
        <div class="faq-a">いたしません。ご報告をお送りした後は、お客様のご判断をお待ちします。「このままで大丈夫だった」というケースも多くあります。追いかけてご連絡することはありません。</div>
      </div>
      <div class="faq-item">
        <button class="faq-q">管理サービスを頼もうか迷っています。まず相談だけできますか？<div class="faq-icon">+</div></button>
        <div class="faq-a">もちろんです。まずは無料確認で状態を把握した上で、管理が必要かどうか一緒に考えましょう。必要なければ「そのままで大丈夫です」とお伝えすることもあります。</div>
      </div>
    </div>
  </div>
</section>

<!-- お問い合わせ -->
<section class="contact-row-sec">
  <div class="contact-row-inner">
    <h2>「まずは状態だけ知りたい」でも構いません<br>お気軽にご連絡ください。</h2>
    <p style="color:#6b7280;margin-bottom:28px;">受付時間 9:00〜18:00（土日祝も対応）</p>
    <div class="contact-methods">
      <a href="tel:07083943791" class="c-method" style="text-decoration:none;">
        <span class="c-icon">📞</span>
        <span class="c-label">お電話で相談する</span>
        <span class="c-val">070-8394-3791</span>
        <span class="c-sub">受付時間 9:00〜18:00</span>
      </a>
      <a href="https://lin.ee/gigscorp" class="c-method" style="text-decoration:none;background:#f0fdf4;border-color:var(--gb);">
        <span class="c-icon">💬</span>
        <span class="c-label">LINEで相談する</span>
        <span class="c-val" style="color:var(--g);">LINE で相談</span>
        <span class="c-sub">気軽にご相談いただけます</span>
      </a>
      <a href="/contact?subject=akiya_free" class="c-method" style="text-decoration:none;background:var(--gl);border-color:var(--gb);">
        <span class="c-icon">✉️</span>
        <span class="c-label">フォームで依頼する</span>
        <span class="c-val" style="color:var(--g);">無料で状態を確認する</span>
        <span class="c-sub">2営業日以内にご連絡</span>
      </a>
    </div>
  </div>
</section>

%(FOOTER)s
<script>
document.querySelectorAll('.faq-q').forEach(btn=>{
  btn.addEventListener('click',()=>{
    const item=btn.parentElement, isOpen=item.classList.contains('open');
    document.querySelectorAll('.faq-item').forEach(i=>i.classList.remove('open'));
    if(!isOpen)item.classList.add('open');
  });
});
</script>
</body></html>"""

# ─────────────────────────────────────────────────────────────
#  空き家サービス 詳細ページ
# ─────────────────────────────────────────────────────────────
AKIYA_SERVICE_HTML = """<!DOCTYPE html>
<html lang="ja"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>空き家の管理・サポートサービス | 有限会社ギグス</title>
<meta name="description" content="空き家の状態やご事情により、必要な対応はそれぞれ異なります。無料確認から月3,000円のAIライトプラン、月10,000円のスタンダードプランまで。文京区の空き家管理なら有限会社ギグス。">
%(CSS)s
<style>
  :root { --g: #2d7a3e; --gl: #e8f5ed; --gb: #a7d4b3; --gd: #1e5c2d; --navy: #1d3461; }

  /* PAGE HEADER */
  .sv-header { background:#fff; padding:80px 0 0; border-bottom:1px solid #e5e7eb; }
  .sv-breadcrumb { font-size:0.76rem; color:#9ca3af; max-width:1100px; margin:0 auto; padding:0 24px 10px; }
  .sv-breadcrumb a { color:#9ca3af; text-decoration:none; }
  .sv-breadcrumb a:hover { color:var(--g); }
  .sv-page-ttl { max-width:1100px; margin:0 auto; padding:16px 24px 28px; }
  .sv-page-ttl h1 { font-size:clamp(1.5rem,3vw,2.2rem); font-weight:900; color:#1a1a2e; margin-bottom:8px; }
  .sv-page-ttl p { font-size:0.9rem; color:#4b5563; line-height:1.8; }

  /* HERO IMAGE */
  .sv-hero-img { width:100%; height:280px; object-fit:cover; display:block; }

  /* PHILOSOPHY */
  .phil-sec { background:#fff; padding:64px 24px; }
  .phil-grid { display:grid; grid-template-columns:1.2fr 1fr; gap:36px; margin-top:40px; align-items:start; }
  @media(max-width:768px){ .phil-grid { grid-template-columns:1fr; } }
  .phil-left h3 { font-size:1rem; font-weight:800; color:#1a1a2e; margin-bottom:20px; }
  .phil-steps { display:grid; grid-template-columns:repeat(3,1fr); gap:12px; }
  @media(max-width:560px){ .phil-steps { grid-template-columns:1fr; } }
  .phil-step { background:#f8faf8; border-radius:12px; padding:20px 16px; text-align:center; border:1px solid #e5e7eb; }
  .phil-step-ico { font-size:1.8rem; margin-bottom:8px; }
  .phil-step p { font-size:0.82rem; color:#374151; font-weight:700; line-height:1.5; }
  .phil-step small { font-size:0.75rem; color:#9ca3af; font-weight:400; }
  .phil-right { background:var(--gl); border:1px solid var(--gb); border-radius:16px; padding:24px; }
  .phil-right h3 { font-size:0.85rem; font-weight:800; color:var(--gd); margin-bottom:14px; display:flex; align-items:center; gap:6px; }
  .free-item2 { display:flex; align-items:center; gap:12px; padding:10px 0; border-bottom:1px solid var(--gb); }
  .free-item2:last-of-type { border-bottom:none; }
  .free-item2 .fi-ico { width:32px; height:32px; background:#fff; border-radius:8px; display:flex; align-items:center; justify-content:center; font-size:1rem; flex-shrink:0; border:1px solid var(--gb); }
  .free-item2 span { font-size:0.87rem; font-weight:600; color:#374151; }
  .phil-note { font-size:0.75rem; color:#6b7280; margin-top:10px; }

  /* PRICE */
  .price-sec { background:#f8faf8; padding:72px 24px; }
  .price-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:20px; margin-top:40px; }
  @media(max-width:640px){ .price-grid { grid-template-columns:1fr; } }
  .pc { background:#fff; border-radius:18px; border:1.5px solid #e5e7eb; overflow:hidden; }
  .pc-head { padding:24px 22px; border-bottom:1px solid #f3f4f6; }
  .pc-label { font-size:0.7rem; font-weight:800; letter-spacing:0.08em; margin-bottom:8px; }
  .pc-name { font-size:1.1rem; font-weight:900; color:#1a1a2e; }
  .pc-price-note { font-size:0.75rem; color:#6b7280; margin-top:4px; }
  .pc-price { font-size:1.8rem; font-weight:900; color:var(--g); margin-top:8px; line-height:1.1; }
  .pc-price span { font-size:0.78rem; color:#6b7280; font-weight:400; }
  .pc-img { width:100%; height:140px; object-fit:cover; display:block; }
  .pc-body { padding:22px; }
  .pc-ul { list-style:none; }
  .pc-ul li { display:flex; gap:8px; align-items:flex-start; font-size:0.86rem; color:#374151; padding:7px 0; border-bottom:1px solid #f3f4f6; }
  .pc-ul li:last-child { border-bottom:none; }
  .pc-ul li::before { content:'✓'; color:var(--g); font-weight:900; flex-shrink:0; margin-top:1px; }
  .pc-featured { border-color:var(--g); }
  .pc-featured .pc-head { background:var(--gl); }

  /* FLOW */
  .flow-sec { background:#fff; padding:72px 24px; }
  .flow-steps { display:grid; grid-template-columns:repeat(4,1fr); gap:0; margin-top:48px; }
  @media(max-width:640px){ .flow-steps { grid-template-columns:repeat(2,1fr); gap:20px; } }
  .flow-step { text-align:center; padding:0 8px; position:relative; }
  .flow-step:not(:last-child)::after { content:'›'; position:absolute; right:-6px; top:22px; font-size:1.4rem; color:#d1d5db; }
  @media(max-width:640px){ .flow-step:not(:last-child)::after { display:none; } }
  .flow-circle { width:52px; height:52px; border-radius:50%; background:linear-gradient(135deg,var(--g),var(--gd)); display:flex; flex-direction:column; align-items:center; justify-content:center; margin:0 auto 14px; box-shadow:0 4px 14px rgba(45,122,62,0.25); }
  .flow-circle .fn { font-size:0.5rem; color:#b2f0c4; font-weight:700; }
  .flow-circle .fv { font-size:1rem; font-weight:900; color:#fff; }
  .flow-step h4 { font-size:0.88rem; font-weight:800; color:#1a1a2e; margin-bottom:6px; line-height:1.35; }
  .flow-step p { font-size:0.78rem; color:#4b5563; line-height:1.65; }
  .flow-note { text-align:center; margin-top:28px; font-size:0.82rem; color:#9ca3af; }

  /* CASES */
  .cases-sec { background:#f8faf8; padding:72px 24px; }
  .cases-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:20px; margin-top:40px; }
  @media(max-width:640px){ .cases-grid { grid-template-columns:1fr; } }
  .case-card { background:#fff; border-radius:16px; border:1px solid #e5e7eb; overflow:hidden; }
  .case-img { width:100%; height:140px; object-fit:cover; display:block; background:linear-gradient(135deg,#e8f5ed,#c5e8d0); }
  .case-body { padding:20px; }
  .case-num { font-size:0.68rem; font-weight:800; color:var(--g); letter-spacing:0.1em; margin-bottom:6px; }
  .case-body p { font-size:0.88rem; color:#374151; font-weight:600; line-height:1.6; }

  /* FUTURE HINT */
  .future-hint { background:var(--navy); padding:20px 24px; text-align:center; }
  .future-hint p { font-size:0.88rem; color:rgba(255,255,255,0.8); }
  .future-hint strong { color:#fff; }

  /* BOTTOM CTA */
  .bottom-cta { background:#fff; padding:64px 24px; }
  .bottom-cta-inner { max-width:760px; margin:0 auto; text-align:center; }
  .bottom-cta h2 { font-size:clamp(1.3rem,2.5vw,1.8rem); font-weight:900; color:#1a1a2e; margin-bottom:16px; }
  .bottom-cta p { font-size:0.9rem; color:#4b5563; margin-bottom:28px; }
  .cta-btns3 { display:flex; gap:12px; justify-content:center; flex-wrap:wrap; }
  .btn-green { display:inline-flex; align-items:center; gap:6px; background:linear-gradient(135deg,var(--g),var(--gd)); color:#fff; padding:13px 26px; border-radius:8px; font-weight:800; font-size:0.92rem; box-shadow:0 5px 18px rgba(45,122,62,0.28); transition:transform 0.2s; }
  .btn-green:hover { transform:translateY(-2px); }
  .btn-nav { display:inline-flex; align-items:center; gap:6px; border:2px solid #e5e7eb; color:#374151; padding:11px 22px; border-radius:8px; font-weight:700; font-size:0.88rem; transition:border-color 0.2s; }
  .btn-nav:hover { border-color:var(--g); color:var(--g); }
  .phone-row { margin-top:20px; font-size:0.85rem; color:#6b7280; }
  .phone-row a { color:var(--navy); font-weight:800; font-size:1rem; }
</style>
</head>
<body>
%(AKIYA_NAV)s

<!-- PAGE HEADER -->
<div class="sv-header">
  <p class="sv-breadcrumb"><a href="/">TOP</a> &rsaquo; <a href="/akiya">空き家サービス</a> &rsaquo; サービスについて</p>
  <div class="sv-page-ttl">
    <h1>空き家の管理・サポートサービス</h1>
    <p>空き家の状態やご事情により、必要な対応はそれぞれ異なります。<br>まずは無料確認の上、必要な場合のみご提案いたします。</p>
  </div>
</div>
<img src="/static/images/akiya_hero.png" class="sv-hero-img" alt="空き家管理サービス" onerror="this.style.display='none'">

<!-- 当サービスの考え方 -->
<section class="phil-sec">
  <div class="si">
    <div class="phil-grid">
      <div class="phil-left">
        <span class="tag tag-green" style="background:var(--gl);color:var(--gd);">当サービスの考え方</span>
        <h3 class="h2" style="font-size:1.5rem;margin-top:10px;">無理に管理をおすすめするものではありません</h3>
        <div class="phil-steps">
          <div class="phil-step">
            <div class="phil-step-ico">✅</div>
            <p>そのままで<br>問題ない</p>
            <small>何もしない</small>
          </div>
          <div class="phil-step">
            <div class="phil-step-ico">🌱</div>
            <p>少し気になる</p>
            <small>軽い確認</small>
          </div>
          <div class="phil-step">
            <div class="phil-step-ico">🏠</div>
            <p>必要な場合<br>のみ対応</p>
            <small>ご提案します</small>
          </div>
        </div>
        <p style="font-size:0.83rem;color:#4b5563;margin-top:16px;line-height:1.8;">状況に応じてご判断いただきます。</p>
      </div>
      <div class="phil-right">
        <h3>🏠 無料でできること <small style="font-size:0.7rem;font-weight:400;color:var(--gd);">（ここまでは完全無料です）</small></h3>
        <div class="free-item2">
          <div class="fi-ico">🏠</div>
          <span>外観チェック（建物・敷地まわり）</span>
        </div>
        <div class="free-item2">
          <div class="fi-ico">📷</div>
          <span>写真の共有（1〜2枚）</span>
        </div>
        <div class="free-item2">
          <div class="fi-ico">💬</div>
          <span>状況コメントのご報告</span>
        </div>
        <p class="phil-note">※ 敷地内には立ち入りません　※ 作業は行いません</p>
      </div>
    </div>
  </div>
</section>

<!-- 有料サービス -->
<section class="price-sec" id="price">
  <div class="si">
    <div class="tc">
      <span class="tag tag-gray">有料でご提供するサービス</span>
      <h2 class="h2" style="font-size:clamp(1.3rem,2.5vw,1.8rem);margin-top:8px;">（必要な場合のみご利用いただけます）</h2>
    </div>
    <div class="price-grid">

      <!-- ライトプラン -->
      <div class="pc pc-featured">
        <div class="pc-head">
          <div class="pc-label" style="color:var(--g);">ライトプラン</div>
          <div class="pc-name">AI外観チェック＋定期レポート</div>
          <div class="pc-price-note">固定</div>
          <div class="pc-price">¥3,000<span> / 月</span></div>
        </div>
        <img src="/static/images/service_akiya.png" class="pc-img" onerror="this.style.display='none'" alt="ライトプラン">
        <div class="pc-body">
          <ul class="pc-ul">
            <li>AI外観チェック</li>
            <li>郵便確認</li>
            <li>定期レポート</li>
          </ul>
          <p style="font-size:0.78rem;color:#6b7280;margin-top:10px;">定期的に状況を把握したい方向けのプランです。</p>
        </div>
      </div>

      <!-- スタンダードプラン -->
      <div class="pc">
        <div class="pc-head">
          <div class="pc-label" style="color:var(--navy);">スタンダードプラン</div>
          <div class="pc-name">室内確認＋管理対応</div>
          <div class="pc-price-note">目安</div>
          <div class="pc-price" style="color:var(--navy);">¥10,000<span> / 月〜</span></div>
        </div>
        <img src="/static/images/akiya_solution.png" class="pc-img" onerror="this.style.display='none'" alt="スタンダードプラン">
        <div class="pc-body">
          <ul class="pc-ul">
            <li>室内確認（換気）</li>
            <li>通水</li>
            <li>詳細レポート</li>
            <li>軽微な一次対応</li>
          </ul>
          <p style="font-size:0.78rem;color:#6b7280;margin-top:10px;">室内の確認や、より詳しい状況把握が必要な方向けのプランです。</p>
        </div>
      </div>

      <!-- 個別対応 -->
      <div class="pc">
        <div class="pc-head">
          <div class="pc-label" style="color:#374151;">個別対応</div>
          <div class="pc-name">草刈り・清掃・修繕など</div>
          <div class="pc-price-note">都度お見積り</div>
          <div class="pc-price" style="color:#374151;font-size:1.3rem;">ご相談ください</div>
        </div>
        <img src="/static/images/akiya_problem.png" class="pc-img" onerror="this.style.background='#f3f4f6';this.style.display='block'" alt="個別対応">
        <div class="pc-body">
          <ul class="pc-ul">
            <li>草刈り</li>
            <li>清掃</li>
            <li>修繕 など</li>
          </ul>
          <p style="font-size:0.78rem;color:#6b7280;margin-top:10px;">必要な時に、必要な内容だけご依頼いただけます。</p>
        </div>
      </div>

    </div>
    <p style="text-align:center;margin-top:16px;font-size:0.8rem;color:#9ca3af;">※ 料金は物件の状況・場所・作業内容により異なります。まずはお気軽にご相談ください。</p>
  </div>
</section>

<!-- ご利用の流れ -->
<section class="flow-sec">
  <div class="si">
    <div class="tc">
      <span class="tag tag-green" style="background:var(--gl);color:var(--gd);">ご利用の流れ</span>
      <h2 class="h2" style="font-size:clamp(1.3rem,2.5vw,1.8rem);margin-top:8px;"></h2>
    </div>
    <div class="flow-steps">
      <div class="flow-step">
        <div class="flow-circle"><span class="fn">STEP</span><span class="fv">1</span></div>
        <h4>無料確認のご依頼</h4>
        <p>フォーム・お電話・LINEでお気軽にご連絡ください。</p>
      </div>
      <div class="flow-step">
        <div class="flow-circle"><span class="fn">STEP</span><span class="fv">2</span></div>
        <h4>状況の確認・写真撮影</h4>
        <p>当社スタッフが現地に伺い、外観の確認と写真撮影を行います。</p>
      </div>
      <div class="flow-step">
        <div class="flow-circle"><span class="fn">STEP</span><span class="fv">3</span></div>
        <h4>状況のご報告・ご提案</h4>
        <p>写真と簡単なコメントをお送りします。必要な場合のみご提案します。</p>
      </div>
      <div class="flow-step">
        <div class="flow-circle"><span class="fn">STEP</span><span class="fv">4</span></div>
        <h4>ご希望があれば対応開始</h4>
        <p>ご要望があればプランをご提案します。ご不要であれば終了でOKです。</p>
      </div>
    </div>
    <p class="flow-note">こちらから強くおすすめすることはありません。</p>
  </div>
</section>

<!-- ご利用事例 -->
<section class="cases-sec">
  <div class="si">
    <div class="tc">
      <h2 class="h2" style="font-size:clamp(1.3rem,2.5vw,1.8rem);">ご利用事例</h2>
    </div>
    <div class="cases-grid">
      <div class="case-card">
        <img src="/static/images/service_akiya.png" class="case-img" onerror="this.style.height='80px'" alt="事例01">
        <div class="case-body">
          <div class="case-num">ケース 01</div>
          <p>外観確認を定期的に行い、<br>安心している</p>
        </div>
      </div>
      <div class="case-card">
        <img src="/static/images/akiya_problem.png" class="case-img" onerror="this.style.height='80px'" alt="事例02">
        <div class="case-body">
          <div class="case-num">ケース 02</div>
          <p>遠方に住んでいるため、<br>月1回の巡回を依頼</p>
        </div>
      </div>
      <div class="case-card">
        <img src="/static/images/akiya_solution.png" class="case-img" onerror="this.style.height='80px'" alt="事例03">
        <div class="case-body">
          <div class="case-num">ケース 03</div>
          <p>草が伸びていたため、<br>除草をお願いした</p>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- 将来的な相談の示唆 -->
<div class="future-hint">
  <p>将来的な <strong>売却・賃貸・活用・各種手続き</strong> のご相談も可能です 🏡</p>
</div>

<!-- CTA -->
<section class="bottom-cta">
  <div class="bottom-cta-inner">
    <h2>まずは無料で状態をご確認ください</h2>
    <p>「様子だけ見てほしい」という依頼も歓迎しています。お気軽にどうぞ。</p>
    <div class="cta-btns3">
      <a href="/contact?subject=akiya_free" class="btn-green">✉ 無料で状態を確認する</a>
      <a href="tel:07083943791" class="btn-nav">📞 070-8394-3791</a>
      <a href="https://lin.ee/gigscorp" class="btn-nav">💬 LINEで相談する</a>
    </div>
    <div class="phone-row">
      お電話での相談：<a href="tel:07083943791">070-8394-3791</a>　受付時間 9:00〜18:00（土日祝も対応）
    </div>
  </div>
</section>

%(FOOTER)s
</body></html>"""

# ─────────────────────────────────────────────────────────────
#  会社概要
# ─────────────────────────────────────────────────────────────
COMPANY_HTML = """<!DOCTYPE html>
<html lang="ja"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>会社案内 | 有限会社ギグス</title>
%(CSS)s
<style>
  /* ── ページタイトルバー ── */
  .co-header { background:#fff; padding:88px 0 0; border-bottom:1px solid #e5e7eb; }
  .co-breadcrumb { font-size:0.76rem; color:#9ca3af; max-width:1080px; margin:0 auto; padding:0 24px 10px; }
  .co-breadcrumb a { color:#9ca3af; text-decoration:none; }
  .co-breadcrumb a:hover { color:#1d3461; }
  .co-breadcrumb span { margin:0 6px; }
  .co-page-ttl { max-width:1080px; margin:0 auto; padding:0 24px 20px; border-left:4px solid #1d3461; }
  .co-page-ttl h1 { font-size:1.6rem; font-weight:900; color:#1d3461; line-height:1.2; margin-bottom:2px; }
  .co-page-ttl small { font-size:0.8rem; color:#9ca3af; letter-spacing:1px; }

  /* ── メイン（写真＋テキスト） ── */
  .co-main { background:#fff; padding:48px 0; }
  .co-main-inner { max-width:1080px; margin:0 auto; padding:0 24px;
    display:grid; grid-template-columns:300px 1fr; gap:48px; align-items:start; }
  @media(max-width:768px){ .co-main-inner { grid-template-columns:1fr; } }
  .co-photo { width:100%; border-radius:4px; overflow:hidden; }
  .co-photo img { width:100%; display:block; object-fit:cover; }
  .co-mission-ttl { font-size:clamp(1.35rem,2.4vw,1.9rem); font-weight:900; color:#1d3461;
    line-height:1.55; margin-bottom:14px; }
  .co-mission-sub { font-size:0.95rem; font-weight:700; color:#9a7b2e; line-height:1.7; margin-bottom:24px; }
  .co-mission-body p { font-size:0.88rem; color:#374151; line-height:2.05; margin-bottom:10px; }
  .co-callout { margin-top:28px; border:1px solid #d4b483; border-radius:6px; padding:14px 18px;
    display:flex; gap:14px; align-items:flex-start; background:#fdf9f2; }
  .co-callout-icon { font-size:2rem; flex-shrink:0; }
  .co-callout-text { font-size:0.87rem; color:#374151; line-height:1.85; font-weight:600; }

  /* ── 中段：経営理念 ＆ 会社概要 ── */
  .co-mid { background:#f7f9fb; padding:40px 0; }
  .co-mid-inner { max-width:1080px; margin:0 auto; padding:0 24px;
    display:grid; grid-template-columns:1fr 1fr; gap:24px; align-items:start; }
  @media(max-width:768px){ .co-mid-inner { grid-template-columns:1fr; } }

  /* ── 下段：資格 ＆ 行わないこと ── */
  .co-btm { background:#fff; padding:40px 0; }
  .co-btm-inner { max-width:1080px; margin:0 auto; padding:0 24px;
    display:grid; grid-template-columns:1fr 1fr; gap:24px; align-items:start; }
  @media(max-width:768px){ .co-btm-inner { grid-template-columns:1fr; } }

  /* セクションカード共通 */
  .co-card { background:#fff; border-radius:6px; padding:24px; box-shadow:0 2px 8px rgba(0,0,0,.07); }
  .co-card-hd { background:#1d3461; color:#fff; border-radius:4px; padding:9px 14px;
    font-size:0.85rem; font-weight:800; margin-bottom:18px;
    display:flex; align-items:center; gap:7px; }

  /* 経営理念 */
  .co-phil-lead { font-size:0.9rem; font-weight:700; color:#1d3461; line-height:1.8;
    margin-bottom:18px; padding-bottom:14px; border-bottom:2px solid #e5e7eb; }
  .co-check-list { list-style:none; padding:0; margin:0 0 18px; }
  .co-check-list li { display:flex; gap:10px; align-items:flex-start;
    font-size:0.86rem; color:#374151; padding:8px 0; border-bottom:1px solid #f3f4f6; }
  .co-check-list li:last-child { border-bottom:none; }
  .co-check-mark { width:20px; height:20px; background:#1d3461; border-radius:50%;
    display:flex; align-items:center; justify-content:center;
    color:#fff; font-size:0.68rem; flex-shrink:0; margin-top:1px; }
  .co-origin-ttl { font-size:0.84rem; font-weight:800; color:#1d3461;
    margin-bottom:7px; display:flex; align-items:center; gap:6px; }
  .co-origin-body { font-size:0.82rem; color:#6b7280; line-height:1.9; }

  /* 会社概要テーブル */
  .co-info-table { width:100%; border-collapse:collapse; font-size:0.84rem; }
  .co-info-table tr { border-bottom:1px solid #f3f4f6; }
  .co-info-table tr:last-child { border-bottom:none; }
  .co-info-table th { padding:9px 12px; font-weight:700; color:#374151;
    background:#f8fafc; width:80px; vertical-align:top; white-space:nowrap; }
  .co-info-table td { padding:9px 12px; color:#1f2937; line-height:1.8; }
  .co-table-note { font-size:0.74rem; color:#6b7280; margin-top:12px; line-height:1.8; }

  /* 資格リスト */
  .co-lic-list { list-style:none; padding:0; margin:0; }
  .co-lic-item { display:flex; gap:10px; padding:10px 0; border-bottom:1px solid #f3f4f6; align-items:flex-start; }
  .co-lic-item:last-child { border-bottom:none; }
  .co-lic-num { width:26px; height:26px; border-radius:5px; background:#f0f4fa;
    border:1px solid #c8d4ed; display:flex; align-items:center; justify-content:center;
    font-size:0.75rem; font-weight:800; color:#1d3461; flex-shrink:0; margin-top:1px; }
  .co-lic-icon { font-size:1.15rem; flex-shrink:0; margin-top:2px; }
  .co-lic-content h4 { font-size:0.86rem; font-weight:800; color:#1d3461; margin-bottom:2px; }
  .co-lic-content p { font-size:0.77rem; color:#6b7280; line-height:1.6; }

  /* 行わないことリスト */
  .co-nodo-list { list-style:none; padding:0; margin:0; }
  .co-nodo-item { padding:12px 0; border-bottom:1px solid #f3f4f6; }
  .co-nodo-item:last-child { border-bottom:none; }
  .co-nodo-hd { display:flex; gap:8px; align-items:flex-start; margin-bottom:3px; }
  .co-nodo-x { color:#dc2626; font-size:1rem; font-weight:900; flex-shrink:0; line-height:1.4; }
  .co-nodo-ttl { font-size:0.87rem; font-weight:800; color:#1f2937; line-height:1.4; }
  .co-nodo-body { font-size:0.79rem; color:#6b7280; line-height:1.75; padding-left:18px; }

  /* ── フッターCTA ── */
  .co-cta { background:#1d3461; padding:22px 24px;
    display:flex; align-items:center; justify-content:space-between; gap:20px; flex-wrap:wrap; }
  .co-cta-left { display:flex; align-items:center; gap:14px; color:#fff; }
  .co-cta-left .icon { font-size:1.8rem; }
  .co-cta-left p { font-size:0.87rem; line-height:1.7; }
  .co-cta-btn { background:#b8963e; color:#fff; padding:13px 28px; border-radius:4px;
    font-size:0.88rem; font-weight:800; text-decoration:none;
    display:flex; align-items:center; gap:8px; flex-shrink:0; white-space:nowrap; }
  .co-cta-btn:hover { background:#9a7b2e; color:#fff; }
</style>
</head>
<body>
%(NAV)s

<!-- ページタイトル -->
<div class="co-header">
  <div class="co-breadcrumb">
    <a href="/">HOME</a><span>&gt;</span>会社案内
  </div>
  <div class="co-page-ttl">
    <h1>会社案内</h1>
    <small>Company</small>
  </div>
</div>

<!-- メイン：写真＋ミッション -->
<section class="co-main">
  <div class="co-main-inner">
    <div class="co-photo">
      <img src="/static/images/ceo.png" alt="代表 高田裕行"
           onerror="this.parentElement.style.cssText='background:#e5e7eb;height:380px;border-radius:4px;';this.style.display='none'">
    </div>
    <div>
      <div class="co-mission-ttl">
        不動産は人生の基盤です。<br>
        その基盤を守り、活かすことが<br>
        私たちの使命です。
      </div>
      <div class="co-mission-sub">
        お客様にとって最適な判断を支援することが、<br>私たちギグスの存在意義です。
      </div>
      <div class="co-mission-body">
        <p>有限会社ギグスは2006年の創業以来、不動産・事業・資産に関する意思決定を支援してきました。</p>
        <p>私たちが重視しているのは、特定の取引に偏らない中立的な立場です。売却・保有・賃貸・再生といった複数の選択肢を比較し、お客様にとって最適な判断をご提案します。</p>
        <p>実際に、売却ではなく保有をお勧めしたり、リフォームを行わない方が良いとお伝えすることもあります。</p>
        <p>近年は空き家問題への対応として、AI技術を活用した現地調査を取り入れ、より正確で合理的な判断を可能にしています。</p>
        <p>当社は「取引」を目的とせず、「最適な判断」を提供する会社です。</p>
      </div>
      <div class="co-callout">
        <div class="co-callout-icon">🏠</div>
        <div class="co-callout-text">
          空き家・不動産・M&amp;Aについて、現状を踏まえた最適な選択肢をご提案します。<br>
          まずは一度、今の状況をお聞かせください。
        </div>
      </div>
    </div>
  </div>
</section>

<!-- 経営理念 ＆ 会社概要 -->
<section class="co-mid">
  <div class="co-mid-inner">

    <!-- 経営理念 -->
    <div class="co-card">
      <div class="co-card-hd">📋 経営理念</div>
      <p class="co-phil-lead">
        お客様にとって最適な判断を支援し、<br>
        資産価値の最大化と安心できる未来の実現に貢献します。
      </p>
      <ul class="co-check-list">
        <li><div class="co-check-mark">✓</div><span>状況を正しく把握し、最適な判断をご提案します</span></li>
        <li><div class="co-check-mark">✓</div><span>短期的な利益ではなく、中長期視点で支援します</span></li>
        <li><div class="co-check-mark">✓</div><span>中立的な立場で、複数の選択肢を比較します</span></li>
        <li><div class="co-check-mark">✓</div><span>誠実で透明性の高い対応を徹底します</span></li>
      </ul>
      <div class="co-origin-ttl">👤 私たちの原点</div>
      <p class="co-origin-body">
        現場では、十分な検討がなされないまま意思決定が行われているケースを多く見てきました。
        だからこそ私たちは、「正しい情報」と「中立的な視点」に基づいた判断支援にこだわっています。
      </p>
    </div>

    <!-- 会社概要 -->
    <div class="co-card">
      <div class="co-card-hd">📋 会社概要</div>
      <table class="co-info-table">
        <tr><th>会社名</th><td>有限会社ギグス</td></tr>
        <tr><th>代表者</th><td>高田 裕行</td></tr>
        <tr><th>所在地</th><td>〒113-0021 東京都文京区本駒込二丁目5番3号</td></tr>
        <tr><th>電話番号</th><td>070-8394-3791</td></tr>
        <tr><th>設立</th><td>2006年1月4日</td></tr>
        <tr><th>資本金</th><td>300万円</td></tr>
        <tr><th>事業内容</th><td>
          ・不動産コンサルティング<br>
          ・空き家活用支援<br>
          ・M&amp;A仲介
        </td></tr>
      </table>
      <p class="co-table-note">
        ※当社は宅地建物取引業者ではありません。<br>
        　不動産の売買・賃貸に関する媒介業務は、<br>
        　提携する宅地建物取引業者と連携して対応しています。
      </p>
    </div>

  </div>
</section>

<!-- 代表者保有資格 ＆ 私たちが行わないこと -->
<section class="co-btm">
  <div class="co-btm-inner">

    <!-- 代表者保有資格 -->
    <div class="co-card">
      <div class="co-card-hd">📋 代表者保有資格（6資格）</div>
      <ul class="co-lic-list">
        <li class="co-lic-item">
          <div class="co-lic-num">1</div>
          <div class="co-lic-icon">🏗️</div>
          <div class="co-lic-content">
            <h4>1級建築施工管理技士</h4>
            <p>建築工事の計画・施工・管理に関する専門資格</p>
          </div>
        </li>
        <li class="co-lic-item">
          <div class="co-lic-num">2</div>
          <div class="co-lic-icon">🏠</div>
          <div class="co-lic-content">
            <h4>宅地建物取引士</h4>
            <p>不動産取引における適正な判断とリスク管理</p>
          </div>
        </li>
        <li class="co-lic-item">
          <div class="co-lic-num">3</div>
          <div class="co-lic-icon">📊</div>
          <div class="co-lic-content">
            <h4>不動産コンサルティングマスター</h4>
            <p>不動産の有効活用・資産戦略に関する専門資格</p>
          </div>
        </li>
        <li class="co-lic-item">
          <div class="co-lic-num">4</div>
          <div class="co-lic-icon">💰</div>
          <div class="co-lic-content">
            <h4>AFP（日本FP協会認定）</h4>
            <p>資産設計・ライフプランニングの専門知識</p>
          </div>
        </li>
        <li class="co-lic-item">
          <div class="co-lic-num">5</div>
          <div class="co-lic-icon">🏦</div>
          <div class="co-lic-content">
            <h4>住宅ローンアドバイザー</h4>
            <p>住宅ローンに関する適切な提案・助言</p>
          </div>
        </li>
        <li class="co-lic-item">
          <div class="co-lic-num">6</div>
          <div class="co-lic-icon">🔑</div>
          <div class="co-lic-content">
            <h4>賃貸不動産経営管理士</h4>
            <p>賃貸不動産の運営・管理に関する専門資格</p>
          </div>
        </li>
      </ul>
    </div>

    <!-- 私たちが行わないこと -->
    <div class="co-card">
      <div class="co-card-hd">📋 私たちが行わないこと</div>
      <ul class="co-nodo-list">
        <li class="co-nodo-item">
          <div class="co-nodo-hd">
            <span class="co-nodo-x">✕</span>
            <span class="co-nodo-ttl">特定の取引を前提とした提案</span>
          </div>
          <p class="co-nodo-body">特定の物件や業者の利益を優先する提案は行いません。</p>
        </li>
        <li class="co-nodo-item">
          <div class="co-nodo-hd">
            <span class="co-nodo-x">✕</span>
            <span class="co-nodo-ttl">売却やリフォームを前提とした誘導</span>
          </div>
          <p class="co-nodo-body">状況によっては「しない方が良い」とお伝えします。</p>
        </li>
        <li class="co-nodo-item">
          <div class="co-nodo-hd">
            <span class="co-nodo-x">✕</span>
            <span class="co-nodo-ttl">短期的な利益を優先した判断</span>
          </div>
          <p class="co-nodo-body">中長期的にお客様の資産価値を高める提案を行います。</p>
        </li>
        <li class="co-nodo-item">
          <div class="co-nodo-hd">
            <span class="co-nodo-x">✕</span>
            <span class="co-nodo-ttl">十分な調査・分析を伴わない提案</span>
          </div>
          <p class="co-nodo-body">正確な情報に基づいた判断を最も重視します。</p>
        </li>
      </ul>
    </div>

  </div>
</section>

<!-- フッターCTA -->
<div class="co-cta">
  <div class="co-cta-left">
    <div class="icon">📞</div>
    <p>空き家・不動産・M&amp;Aに関するご相談は<br>お気軽にお問い合わせください</p>
  </div>
  <a href="/contact" class="co-cta-btn">✉️ 無料相談・お問い合わせはこちら &gt;</a>
</div>

%(FOOTER)s
</body></html>"""

# ─────────────────────────────────────────────────────────────
#  お問い合わせ
# ─────────────────────────────────────────────────────────────
CONTACT_HTML = """<!DOCTYPE html>
<html lang="ja"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>お問い合わせ | 有限会社ギグス</title>
%(CSS)s
<style>
  .ct-hero { background:linear-gradient(135deg,#0f3460,#16534a); padding:120px 24px 80px; text-align:center; }
  .ct-hero h1 { font-size:clamp(2rem,4vw,3rem); font-weight:900; color:#fff; margin-bottom:12px; }
  .ct-hero p { font-size:1rem; color:rgba(255,255,255,0.72); }
  .contact-sec { background:#f7f9fb; }
  .ct-grid { display:grid; grid-template-columns:1fr 1.6fr; gap:48px; margin-top:56px; align-items:start; }
  @media(max-width:768px){.ct-grid{grid-template-columns:1fr;}}
  .ct-info h3 { font-size:1.1rem; font-weight:900; color:#0f172a; margin-bottom:20px; }
  .ct-item { display:flex; gap:14px; align-items:flex-start; margin-bottom:20px; }
  .ct-ico { width:44px; height:44px; border-radius:10px; background:linear-gradient(135deg,#0f3460,#16534a); display:flex; align-items:center; justify-content:center; font-size:1.2rem; flex-shrink:0; }
  .ct-item h4 { font-size:0.85rem; font-weight:700; color:#0f172a; }
  .ct-item p { font-size:0.88rem; color:#4b5563; margin-top:2px; }
  .ct-form-card { background:#fff; border-radius:24px; padding:44px; box-shadow:0 4px 24px rgba(0,0,0,0.07); }
  .fg { margin-bottom:18px; }
  .fg label { display:block; font-size:0.82rem; font-weight:700; color:#374151; margin-bottom:7px; }
  .fg .req { color:#dc2626; margin-left:3px; font-size:0.75rem; }
  .fg input,.fg select,.fg textarea { width:100%; background:#f7f9fb; border:1.5px solid #e5e7eb; border-radius:10px; padding:12px 16px; color:#1f2937; font-size:0.9rem; font-family:inherit; outline:none; transition:border-color 0.2s; }
  .fg input:focus,.fg select:focus,.fg textarea:focus { border-color:#0f3460; background:#fff; }
  .fg textarea { height:120px; resize:vertical; }
  .form-submit { width:100%; background:linear-gradient(135deg,#0f3460,#16534a); color:#fff; border:none; padding:16px; border-radius:12px; font-size:1rem; font-weight:800; cursor:pointer; transition:opacity 0.2s; font-family:inherit; }
  .form-submit:hover { opacity:0.88; }
  .form-submit:disabled { opacity:0.5; cursor:not-allowed; }
  #form-msg { text-align:center; margin-top:14px; font-size:0.9rem; }
  .form-row { display:grid; grid-template-columns:1fr 1fr; gap:16px; }
  @media(max-width:560px){.form-row{grid-template-columns:1fr;}}
</style>
</head>
<body>
%(NAV)s
<div class="ct-hero">
  <h1>お問い合わせ</h1>
  <p>空き家・不動産・M&Aに関するご相談は無料です。お気軽にどうぞ。</p>
</div>
<section class="contact-sec">
  <div class="si">
    <div class="ct-grid">
      <div class="ct-info">
        <h3>ご連絡先</h3>
        <div class="ct-item"><div class="ct-ico">📞</div><div><h4>お電話</h4><p>070-8394-3791<br>（平日 9:00〜18:00）</p></div></div>
        <div class="ct-item"><div class="ct-ico">✉️</div><div><h4>メール</h4><p>info@gigscorp.jp<br>（2営業日以内に返信）</p></div></div>
        <div class="ct-item"><div class="ct-ico">📍</div><div><h4>所在地</h4><p>〒113-0021<br>東京都文京区本駒込二丁目5番3号</p></div></div>
        <div style="margin-top:32px;background:#eff6ff;border-radius:12px;padding:20px;">
          <p style="font-size:0.85rem;color:#1d4ed8;font-weight:700;margin-bottom:8px;">🌐 オンライン相談も対応</p>
          <p style="font-size:0.83rem;color:#374151;line-height:1.75;">Zoom・Google Meetでのオンライン相談に対応しております。遠方の方もお気軽にご相談ください。</p>
        </div>
      </div>
      <div class="ct-form-card">
        <div class="form-row">
          <div class="fg"><label>お名前<span class="req">*</span></label><input type="text" id="name" placeholder="山田 太郎"></div>
          <div class="fg"><label>会社名・法人名</label><input type="text" id="company" placeholder="（任意）"></div>
        </div>
        <div class="form-row">
          <div class="fg"><label>メールアドレス<span class="req">*</span></label><input type="email" id="email" placeholder="mail@example.com"></div>
          <div class="fg"><label>電話番号</label><input type="tel" id="tel" placeholder="070-8394-3791"></div>
        </div>
        <div class="fg">
          <label>ご相談内容<span class="req">*</span></label>
          <select id="subject">
            <option value="">選択してください</option>
            <option value="空き家（調査・報告書）">空き家（AI調査・報告書作成）</option>
            <option value="空き家（管理代行）">空き家（管理代行）</option>
            <option value="空き家（売却・賃貸）">空き家（売却・賃貸仲介）</option>
            <option value="不動産売買仲介">不動産売買仲介</option>
            <option value="不動産コンサルティング">不動産コンサルティング</option>
            <option value="M&A仲介">M&A仲介</option>
            <option value="その他">その他</option>
          </select>
        </div>
        <div class="fg"><label>物件の所在地（空き家の方）</label><input type="text" id="location" placeholder="例：東京都〇〇区（任意）"></div>
        <div class="fg"><label>ご質問・ご要望<span class="req">*</span></label><textarea id="message" placeholder="物件の状況・ご要望など、お気軽にご記入ください。"></textarea></div>
        <button class="form-submit" id="submit-btn" onclick="submitContact()">送信する →</button>
        <div id="form-msg"></div>
        <p style="margin-top:16px;font-size:0.78rem;color:#9ca3af;text-align:center;">送信いただいた情報は、お問い合わせへの返答以外には使用しません。</p>
      </div>
    </div>
  </div>
</section>
%(FOOTER)s
<script>
async function submitContact(){
  const btn=document.getElementById('submit-btn'), msg=document.getElementById('form-msg');
  const name=document.getElementById('name').value.trim();
  const email=document.getElementById('email').value.trim();
  const subject=document.getElementById('subject').value;
  const message=document.getElementById('message').value.trim();
  if(!name||!email||!subject||!message){msg.style.color='#dc2626';msg.textContent='必須項目をすべてご入力ください。';return;}
  btn.disabled=true;btn.textContent='送信中...';msg.textContent='';
  try{
    const res=await fetch('/api/contact',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({name,company:document.getElementById('company').value,email,tel:document.getElementById('tel').value,subject,location:document.getElementById('location').value,message})});
    const data=await res.json();
    if(data.success){msg.style.color='#16a34a';msg.textContent='お問い合わせを受け付けました。2営業日以内にご連絡いたします。';}
    else{msg.style.color='#dc2626';msg.textContent='送信に失敗しました。info@gigscorp.jp までご連絡ください。';}
  }catch{msg.style.color='#dc2626';msg.textContent='通信エラーが発生しました。';}
  btn.disabled=false;btn.textContent='送信する →';
}
</script>
</body></html>"""

# ─────────────────────────────────────────────────────────────
#  Flask ルート
# ─────────────────────────────────────────────────────────────
def render(html, active=""):
    return (html
        .replace("%(CSS)s", COMMON_CSS)
        .replace("%(NAV)s", nav_html(active))
        .replace("%(FOOTER)s", FOOTER_HTML))

def render_akiya(html):
    """空き家ページ専用レンダー（専用ナビ使用）"""
    return (html
        .replace("%(CSS)s", COMMON_CSS)
        .replace("%(AKIYA_NAV)s", akiya_nav_html())
        .replace("%(NAV)s", akiya_nav_html())
        .replace("%(FOOTER)s", FOOTER_HTML))

@app.route('/')
def home():
    return render(HOME_HTML, "ホーム")

@app.route('/akiya')
def akiya():
    return render_akiya(AKIYA_HTML)

@app.route('/akiya/service')
def akiya_service():
    return render_akiya(AKIYA_SERVICE_HTML)

@app.route('/company')
def company():
    return render(COMPANY_HTML, "会社概要")

@app.route('/contact')
def contact():
    return render(CONTACT_HTML, "お問い合わせ")

@app.route('/api/contact', methods=['POST'])
def contact_api():
    data = request.get_json() or {}
    name    = data.get('name', '')
    company = data.get('company', '')
    email   = data.get('email', '')
    tel     = data.get('tel', '')
    subject = data.get('subject', '')
    location= data.get('location', '')
    message = data.get('message', '')

    if not all([name, email, subject, message]):
        return jsonify({'success': False, 'error': 'missing fields'})

    if not SENDGRID_API_KEY:
        # 開発環境: ログ出力のみ
        print(f"[CONTACT] {name} <{email}> / {subject}")
        return jsonify({'success': True})

    try:
        import sendgrid
        from sendgrid.helpers.mail import Mail, Email, To, Content
        sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
        body = f"""【お問い合わせ】

お名前: {name}
会社名: {company or 'なし'}
メール: {email}
電話: {tel or 'なし'}
件名: {subject}
物件所在地: {location or 'なし'}

内容:
{message}
"""
        sg.send(Mail(
            from_email=Email('info@gigscorp.jp', '有限会社ギグス'),
            to_emails=CONTACT_EMAIL,
            subject=f'【ギグス】お問い合わせ: {subject} / {name}様',
            plain_text_content=Content('text/plain', body)
        ))
        # 自動返信
        reply = f"""{name} 様

この度は有限会社ギグスへのお問い合わせありがとうございます。
以下の内容でお問い合わせを受け付けました。

━━━━━━━━━━━━━━━━━━━━
件名: {subject}
━━━━━━━━━━━━━━━━━━━━
{message}
━━━━━━━━━━━━━━━━━━━━

担当者より2営業日以内にご連絡いたします。

有限会社ギグス（GIGS CORP.）
https://gigscorp.jp
info@gigscorp.jp
"""
        sg.send(Mail(
            from_email=Email('info@gigscorp.jp', '有限会社ギグス'),
            to_emails=email,
            subject='【ギグス】お問い合わせを受け付けました',
            plain_text_content=Content('text/plain', reply)
        ))
        return jsonify({'success': True})
    except Exception as e:
        print(f'[contact_api] error: {e}')
        return jsonify({'success': True})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)
