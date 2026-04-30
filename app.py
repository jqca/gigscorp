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
    width: 48px; height: 48px;
    display: flex; align-items: center; justify-content: center;
  }
  .nav-logo-mark img { width: 48px; height: 48px; object-fit: contain; }
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
    pages = [("ホーム","/"),("空き家ビジネス","/akiya"),("会社概要","/company"),("お問い合わせ","/contact")]
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
<title>有限会社ギグス | 不動産・空き家・M&A 総合コンサルティング</title>
<meta name="description" content="有限会社ギグスは不動産売買仲介・空き家ビジネス・M&A仲介を手がける総合不動産コンサルティング会社です。東京都文京区本駒込。">
%(CSS)s
<style>
  /* HERO */
  .hero { position:relative; min-height:100vh; display:flex; align-items:center; overflow:hidden; padding:120px 24px 80px; }
  .hero-bg { position:absolute; inset:0; background:url('/static/images/hero.png') center/cover no-repeat; }
  .hero-bg::after { content:''; position:absolute; inset:0; background:linear-gradient(100deg,rgba(10,25,60,0.88) 0%,rgba(10,25,60,0.7) 55%,rgba(10,25,60,0.3) 100%); }
  .hero-inner { position:relative; z-index:1; max-width:640px; }
  .hero-eyebrow { display:inline-flex; align-items:center; gap:8px; background:rgba(255,255,255,0.12); border:1px solid rgba(255,255,255,0.22); color:#93c5fd; padding:7px 18px; border-radius:30px; font-size:0.78rem; font-weight:700; letter-spacing:0.12em; margin-bottom:28px; }
  .hero h1 { font-size:clamp(2.2rem,5vw,3.6rem); font-weight:900; color:#fff; line-height:1.18; letter-spacing:-0.02em; margin-bottom:20px; }
  .hero h1 em { font-style:normal; color:#fcd34d; }
  .hero-sub { font-size:1.05rem; color:rgba(255,255,255,0.78); line-height:1.85; margin-bottom:40px; max-width:480px; }
  .hero-btns { display:flex; gap:14px; flex-wrap:wrap; margin-bottom:56px; }
  .btn-hero-p { background:linear-gradient(135deg,#e8a020,#c47d10); color:#fff; padding:16px 36px; border-radius:8px; font-weight:800; font-size:1rem; box-shadow:0 6px 24px rgba(232,160,32,0.4); transition:transform 0.2s,box-shadow 0.2s; }
  .btn-hero-p:hover { transform:translateY(-2px); box-shadow:0 10px 32px rgba(232,160,32,0.5); }
  .btn-hero-s { border:2px solid rgba(255,255,255,0.4); color:#fff; padding:14px 32px; border-radius:8px; font-weight:700; font-size:0.95rem; transition:background 0.2s; }
  .btn-hero-s:hover { background:rgba(255,255,255,0.12); }
  .hero-trust { display:flex; gap:28px; flex-wrap:wrap; padding-top:36px; border-top:1px solid rgba(255,255,255,0.18); }
  .trust-pill { display:flex; align-items:center; gap:8px; color:rgba(255,255,255,0.72); font-size:0.82rem; font-weight:600; }
  .trust-dot { width:8px; height:8px; border-radius:50%; background:#fcd34d; flex-shrink:0; }

  /* NUMBERS */
  .numbers { background:#0f3460; padding:56px 24px; }
  .num-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:0; max-width:960px; margin:0 auto; }
  @media(max-width:640px){.num-grid{grid-template-columns:repeat(2,1fr);}}
  .num-item { text-align:center; padding:28px 16px; border-right:1px solid rgba(255,255,255,0.12); }
  .num-item:last-child { border-right:none; }
  .num-val { font-size:2.4rem; font-weight:900; color:#fcd34d; line-height:1; }
  .num-unit { font-size:0.85rem; color:#fcd34d; }
  .num-label { font-size:0.78rem; color:rgba(255,255,255,0.55); margin-top:6px; }

  /* SERVICES */
  .services { background:#fff; }
  .svc-grid { display:grid; grid-template-columns:repeat(2,1fr); gap:24px; margin-top:56px; }
  @media(max-width:760px){.svc-grid{grid-template-columns:1fr;}}
  .svc-card { border-radius:20px; overflow:hidden; border:1px solid #e5e7eb; transition:box-shadow 0.3s,transform 0.3s; }
  .svc-card:hover { box-shadow:0 12px 40px rgba(0,0,0,0.1); transform:translateY(-4px); }
  .svc-img { width:100%; height:200px; object-fit:cover; }
  .svc-body { padding:28px; }
  .svc-icon { font-size:1.8rem; margin-bottom:12px; }
  .svc-body h3 { font-size:1.2rem; font-weight:900; color:#0f172a; margin-bottom:10px; }
  .svc-body p { font-size:0.88rem; color:#4b5563; line-height:1.8; margin-bottom:16px; }
  .svc-link { font-size:0.84rem; font-weight:700; color:#0f3460; display:inline-flex; align-items:center; gap:4px; }
  .svc-link::after { content:'→'; }

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
  .btn-gold { background:linear-gradient(135deg,#e8a020,#c47d10); color:#fff; padding:14px 32px; border-radius:8px; font-weight:800; font-size:0.95rem; box-shadow:0 6px 20px rgba(232,160,32,0.35); transition:transform 0.2s; display:inline-flex; align-items:center; gap:8px; }
  .btn-gold:hover { transform:translateY(-2px); }

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
  .cta-box h2 { font-size:clamp(1.7rem,3vw,2.4rem); font-weight:900; margin-bottom:14px; }
  .cta-box p { font-size:1rem; color:rgba(255,255,255,0.75); margin-bottom:36px; }
  .cta-btns { display:flex; gap:14px; justify-content:center; flex-wrap:wrap; }
  .btn-white { background:#fff; color:#0f3460; padding:14px 32px; border-radius:8px; font-weight:800; font-size:0.95rem; transition:opacity 0.2s; }
  .btn-white:hover { opacity:0.9; }
</style>
</head>
<body>
%(NAV)s
<section class="hero">
  <div class="hero-bg"></div>
  <div class="hero-inner">
    <div class="hero-eyebrow">不動産×AI×M&A 総合コンサルティング</div>
    <h1>不動産の未来を、<br><em>ともに創る。</em></h1>
    <p class="hero-sub">有限会社ギグスは、不動産売買仲介・空き家ビジネス・M&A仲介を通じてお客様の大切な資産を守り、最大化します。2006年の創業以来、誠実さと専門性でお客様のご期待にお応えしてきました。</p>
    <div class="hero-btns">
      <a href="/akiya" class="btn-hero-p">空き家ビジネスを見る</a>
      <a href="/contact" class="btn-hero-s">無料相談はこちら</a>
    </div>
    <div class="hero-trust">
      <div class="trust-pill"><span class="trust-dot"></span>創業2006年</div>
      <div class="trust-pill"><span class="trust-dot"></span>宅地建物取引業免許 取得</div>
      <div class="trust-pill"><span class="trust-dot"></span>AI×不動産 最先端対応</div>
    </div>
  </div>
</section>

<div class="numbers">
  <div class="num-grid">
    <div class="num-item"><div class="num-val">18<span class="num-unit">年</span></div><div class="num-label">創業からの実績</div></div>
    <div class="num-item"><div class="num-val">AI<span class="num-unit">活用</span></div><div class="num-label">最先端の調査・分析</div></div>
    <div class="num-item"><div class="num-val">4<span class="num-unit">事業</span></div><div class="num-label">総合的なサービス展開</div></div>
    <div class="num-item"><div class="num-val">全国<span class="num-unit">対応</span></div><div class="num-label">ご相談・調査対応エリア</div></div>
  </div>
</div>

<section class="services" id="services">
  <div class="si">
    <div class="tc">
      <span class="tag tag-navy">SERVICES</span>
      <h2 class="h2">サービス一覧</h2>
      <p class="lead">不動産に関するあらゆるご相談に、ワンストップで対応します。</p>
    </div>
    <div class="svc-grid">
      <div class="svc-card">
        <img src="/static/images/service_akiya.png" class="svc-img" onerror="this.parentElement.querySelector('.svc-icon').style.fontSize='4rem'" alt="空き家ビジネス">
        <div class="svc-body">
          <div class="svc-icon">🏚️</div>
          <h3>空き家ビジネス</h3>
          <p>放置された空き家の調査・管理代行・売却・賃貸仲介・リノベーション提案まで。AI技術を活用した現地調査報告書で、迅速かつ正確な資産評価を実現します。</p>
          <a href="/akiya" class="svc-link">詳しく見る</a>
        </div>
      </div>
      <div class="svc-card">
        <img src="/static/images/service_re.png" class="svc-img" onerror="this.style.display='none'" alt="不動産売買仲介">
        <div class="svc-body">
          <div class="svc-icon">🏢</div>
          <h3>不動産売買仲介</h3>
          <p>住宅・ビル・土地の売買仲介を専門家が丁寧にサポート。豊富な経験と市場分析で、最適な価格での取引を実現します。</p>
          <a href="/contact" class="svc-link">お問い合わせ</a>
        </div>
      </div>
      <div class="svc-card">
        <img src="/static/images/service_consult.png" class="svc-img" onerror="this.style.display='none'" alt="不動産コンサルティング">
        <div class="svc-body">
          <div class="svc-icon">📊</div>
          <h3>不動産コンサルティング</h3>
          <p>資産運用・相続対策・土地活用など、不動産に関する戦略的なアドバイスを提供。お客様の状況に合わせた最適なプランをご提案します。</p>
          <a href="/contact" class="svc-link">お問い合わせ</a>
        </div>
      </div>
      <div class="svc-card">
        <img src="/static/images/service_ma.png" class="svc-img" onerror="this.style.display='none'" alt="M&A仲介">
        <div class="svc-body">
          <div class="svc-icon">🤝</div>
          <h3>M&A仲介</h3>
          <p>不動産会社・管理会社・建設会社のM&A仲介サービス。買収・売却・事業継承のご相談を秘密厳守で承ります。</p>
          <a href="/contact" class="svc-link">お問い合わせ</a>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="akiya-feature">
  <div class="af-inner">
    <div class="af-img">
      <img src="/static/images/akiya_hero.png" onerror="this.parentElement.style.background='linear-gradient(135deg,#0a2040,#0f3460)';this.remove()" alt="空き家ビジネス">
    </div>
    <div class="af-content">
      <span class="af-tag">NEW BUSINESS</span>
      <h2>放置された空き家を、<br>価値ある資産へ。</h2>
      <p>全国の空き家は約900万戸（総務省調査）。放置するリスクを解消し、資産価値を取り戻すお手伝いをします。ギグスのAI活用調査で、迅速・正確・低コストを実現。</p>
      <ul class="af-points">
        <li>AI技術を活用した現地調査報告書の自動生成</li>
        <li>空き家の管理代行から売却・賃貸仲介まで一貫サポート</li>
        <li>リノベーション提案で資産価値を最大化</li>
        <li>相続空き家・遠方物件のご相談も対応</li>
      </ul>
      <a href="/akiya" class="btn-gold">空き家ビジネスの詳細を見る →</a>
    </div>
  </div>
</section>

<section class="strengths">
  <div class="si">
    <div class="tc">
      <span class="tag tag-green">WHY GIGS</span>
      <h2 class="h2">ギグスが選ばれる理由</h2>
    </div>
    <div class="str-grid">
      <div class="str-card">
        <div class="str-num">01</div>
        <div class="str-icon">🔬</div>
        <h3>AI技術で精度の高い調査</h3>
        <p>最先端のAI（Claude Vision API）を活用した現地調査報告書を提供。写真分析で正確な物件状況を把握し、迅速な意思決定をサポートします。</p>
      </div>
      <div class="str-card">
        <div class="str-num">02</div>
        <div class="str-icon">🛡️</div>
        <h3>18年の実績と信頼</h3>
        <p>2006年の創業以来、不動産売買仲介・コンサルティング・M&Aで培ってきた経験と信頼。宅地建物取引業免許を取得した専門家集団です。</p>
      </div>
      <div class="str-card">
        <div class="str-num">03</div>
        <div class="str-icon">💬</div>
        <h3>丁寧で迅速な対応</h3>
        <p>お問い合わせから2営業日以内に返答。お客様一人ひとりの状況を丁寧にヒアリングし、最適な解決策をご提案します。</p>
      </div>
    </div>
  </div>
</section>

<section class="cta-section">
  <div class="si">
    <div class="cta-box">
      <h2>まずはお気軽に<br>ご相談ください</h2>
      <p>空き家・不動産・M&Aに関するご相談は無料です。<br>専門スタッフが丁寧にお答えします。</p>
      <div class="cta-btns">
        <a href="/contact" class="btn-white">無料相談フォームへ</a>
        <a href="/akiya" style="border:2px solid rgba(255,255,255,0.5);color:#fff;padding:14px 32px;border-radius:8px;font-weight:700;font-size:0.93rem;">空き家ビジネスを見る</a>
      </div>
    </div>
  </div>
</section>

%(FOOTER)s
</body></html>"""

# ─────────────────────────────────────────────────────────────
#  空き家ビジネスページ
# ─────────────────────────────────────────────────────────────
AKIYA_HTML = """<!DOCTYPE html>
<html lang="ja"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>空き家ビジネス | 有限会社ギグス</title>
<meta name="description" content="放置された空き家を価値ある資産へ。AI技術を活用した現地調査・管理代行・売却仲介・リノベーション提案。有限会社ギグスの空き家ビジネスサービス。">
%(CSS)s
<style>
  .ak-hero { position:relative; min-height:80vh; display:flex; align-items:center; padding:120px 40px 80px; overflow:hidden; }
  .ak-hero-bg { position:absolute; inset:0; background:url('/static/images/akiya_hero.png') center/cover; }
  .ak-hero-bg::after { content:''; position:absolute; inset:0; background:linear-gradient(100deg,rgba(5,20,10,0.9) 0%,rgba(5,20,10,0.7) 55%,rgba(5,20,10,0.35) 100%); }
  .ak-hero-inner { position:relative; z-index:1; max-width:620px; }
  .ak-hero h1 { font-size:clamp(2rem,4.5vw,3.2rem); font-weight:900; color:#fff; line-height:1.2; margin-bottom:20px; letter-spacing:-0.02em; }
  .ak-hero h1 em { font-style:normal; color:#6ee7b7; }
  .ak-hero p { font-size:1.05rem; color:rgba(255,255,255,0.78); line-height:1.85; margin-bottom:36px; }
  .stat-pills { display:flex; gap:14px; flex-wrap:wrap; margin-bottom:40px; }
  .stat-pill { background:rgba(255,255,255,0.1); border:1px solid rgba(255,255,255,0.2); color:#fff; padding:10px 18px; border-radius:8px; font-size:0.82rem; font-weight:600; }
  .stat-pill strong { color:#6ee7b7; font-size:1rem; }

  /* PROBLEM */
  .problem { background:#fff; }
  .prob-grid { display:grid; grid-template-columns:1fr 1fr; gap:48px; align-items:center; margin-top:56px; }
  @media(max-width:768px){.prob-grid{grid-template-columns:1fr;}}
  .prob-img { border-radius:20px; overflow:hidden; box-shadow:0 12px 40px rgba(0,0,0,0.12); }
  .prob-img img { width:100%; height:360px; object-fit:cover; }
  .prob-stats { display:grid; grid-template-columns:1fr 1fr; gap:16px; margin-top:32px; }
  .ps-item { background:#fef2f2; border-radius:12px; padding:20px; text-align:center; }
  .ps-num { font-size:2rem; font-weight:900; color:#dc2626; }
  .ps-label { font-size:0.78rem; color:#6b7280; margin-top:4px; }

  /* SOLUTION */
  .solution { background:#f7f9fb; }
  .sol-grid { display:grid; grid-template-columns:1fr 1fr; gap:48px; align-items:center; margin-top:56px; }
  @media(max-width:768px){.sol-grid{grid-template-columns:1fr;}}
  .sol-img { border-radius:20px; overflow:hidden; box-shadow:0 12px 40px rgba(0,0,0,0.12); }
  .sol-img img { width:100%; height:360px; object-fit:cover; }
  .sol-points { list-style:none; margin-top:24px; }
  .sol-points li { display:flex; gap:14px; padding:14px 0; border-bottom:1px solid #e5e7eb; }
  .sol-points li:last-child { border-bottom:none; }
  .sol-ico { width:44px; height:44px; border-radius:10px; background:linear-gradient(135deg,#0f3460,#16534a); display:flex; align-items:center; justify-content:center; font-size:1.3rem; flex-shrink:0; }
  .sol-text h4 { font-size:0.95rem; font-weight:800; color:#0f172a; margin-bottom:4px; }
  .sol-text p { font-size:0.84rem; color:#4b5563; line-height:1.75; }

  /* AI FEATURE */
  .ai-feature { background:linear-gradient(135deg,#0f172a,#0f3460); padding:92px 24px; }
  .ai-inner { max-width:1120px; margin:0 auto; }
  .ai-card { background:rgba(255,255,255,0.06); border:1px solid rgba(255,255,255,0.12); border-radius:24px; padding:48px; display:grid; grid-template-columns:1fr 1fr; gap:48px; align-items:center; }
  @media(max-width:768px){.ai-card{grid-template-columns:1fr;}}
  .ai-tag { background:rgba(110,231,183,0.2); color:#6ee7b7; font-size:0.72rem; font-weight:800; letter-spacing:0.15em; padding:5px 14px; border-radius:20px; display:inline-block; margin-bottom:14px; }
  .ai-card h2 { font-size:clamp(1.6rem,2.8vw,2.2rem); font-weight:900; color:#fff; line-height:1.25; margin-bottom:16px; }
  .ai-card p { font-size:0.93rem; color:rgba(255,255,255,0.72); line-height:1.85; margin-bottom:24px; }
  .ai-features { list-style:none; }
  .ai-features li { display:flex; gap:10px; font-size:0.88rem; color:rgba(255,255,255,0.8); padding:8px 0; border-bottom:1px solid rgba(255,255,255,0.08); }
  .ai-features li:last-child { border-bottom:none; }
  .ai-features li::before { content:'⚡'; flex-shrink:0; }
  .ai-visual { background:rgba(0,0,0,0.3); border-radius:16px; padding:28px; }
  .ai-report-mock { background:rgba(255,255,255,0.06); border-radius:12px; padding:20px; }
  .ai-report-mock h4 { font-size:0.8rem; font-weight:700; color:#6ee7b7; margin-bottom:12px; letter-spacing:0.1em; }
  .ai-field { display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid rgba(255,255,255,0.06); font-size:0.82rem; }
  .ai-field .k { color:rgba(255,255,255,0.5); }
  .ai-field .v { color:#fff; font-weight:600; }
  .ai-score { margin-top:16px; text-align:center; }
  .ai-score-num { font-size:2.8rem; font-weight:900; color:#6ee7b7; }
  .ai-score-label { font-size:0.75rem; color:rgba(255,255,255,0.5); }

  /* FLOW */
  .flow { background:#fff; }
  .flow-steps { display:grid; grid-template-columns:repeat(5,1fr); gap:0; margin-top:60px; }
  @media(max-width:900px){.flow-steps{grid-template-columns:1fr 1fr;gap:24px;}}
  .flow-step { text-align:center; padding:0 12px; position:relative; }
  .flow-step:not(:last-child)::after { content:'→'; position:absolute; right:-8px; top:28px; font-size:1.2rem; color:#d1d5db; }
  @media(max-width:900px){.flow-step:not(:last-child)::after{display:none;}}
  .step-circle { width:60px; height:60px; border-radius:50%; background:linear-gradient(135deg,#0f3460,#16534a); display:flex; flex-direction:column; align-items:center; justify-content:center; margin:0 auto 16px; box-shadow:0 6px 18px rgba(15,52,96,0.28); }
  .step-circle .sn { font-size:0.55rem; color:#93c5fd; font-weight:700; }
  .step-circle .sv { font-size:1.05rem; font-weight:900; color:#fff; }
  .flow-step h4 { font-size:0.88rem; font-weight:800; color:#0f172a; margin-bottom:8px; line-height:1.3; }
  .flow-step p { font-size:0.78rem; color:#4b5563; line-height:1.7; }

  /* PRICE */
  .price-sec { background:#f7f9fb; }
  .price-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:20px; margin-top:56px; }
  @media(max-width:640px){.price-grid{grid-template-columns:1fr;}}
  .price-card { background:#fff; border-radius:20px; padding:32px; border:2px solid #e5e7eb; transition:border-color 0.3s,box-shadow 0.3s; text-align:center; }
  .price-card.featured { border-color:#0f3460; box-shadow:0 8px 32px rgba(15,52,96,0.12); }
  .price-card .badge { font-size:0.7rem; font-weight:800; padding:4px 12px; border-radius:20px; margin-bottom:14px; display:inline-block; }
  .badge-basic { background:#f3f4f6; color:#4b5563; }
  .badge-std { background:#e0e7f3; color:#0f3460; }
  .badge-prem { background:linear-gradient(135deg,#0f3460,#16534a); color:#fff; }
  .price-card h3 { font-size:1.15rem; font-weight:900; color:#0f172a; margin-bottom:8px; }
  .price-card .price { font-size:2rem; font-weight:900; color:#0f3460; margin:16px 0 4px; }
  .price-card .price span { font-size:0.85rem; color:#6b7280; font-weight:500; }
  .price-card ul { list-style:none; text-align:left; margin:16px 0 24px; }
  .price-card li { font-size:0.84rem; color:#374151; padding:7px 0; border-bottom:1px solid #f3f4f6; display:flex; align-items:center; gap:8px; }
  .price-card li::before { content:'✓'; color:#16534a; font-weight:900; }

  /* FAQ */
  .faq-sec { background:#fff; }
  .faq-list { max-width:760px; margin:56px auto 0; }
  .faq-item { background:#f7f9fb; border-radius:14px; margin-bottom:10px; overflow:hidden; }
  .faq-q { width:100%; background:none; border:none; color:#0f172a; text-align:left; padding:20px 24px; font-size:0.95rem; font-weight:700; cursor:pointer; display:flex; justify-content:space-between; align-items:center; gap:16px; font-family:inherit; }
  .faq-icon { width:28px; height:28px; border-radius:50%; background:#e0e7f3; display:flex; align-items:center; justify-content:center; font-size:1.1rem; color:#0f3460; flex-shrink:0; transition:transform 0.3s,background 0.3s; }
  .faq-item.open .faq-icon { transform:rotate(45deg); background:#0f3460; color:#fff; }
  .faq-a { display:none; padding:0 24px 20px; font-size:0.9rem; color:#4b5563; line-height:1.85; }
  .faq-item.open .faq-a { display:block; }

  /* CTA */
  .ak-cta { background:linear-gradient(135deg,#0f3460,#16534a); padding:92px 24px; text-align:center; }
  .ak-cta h2 { font-size:clamp(1.7rem,3vw,2.4rem); font-weight:900; color:#fff; margin-bottom:14px; }
  .ak-cta p { font-size:1rem; color:rgba(255,255,255,0.75); margin-bottom:36px; }
  .ak-cta-btns { display:flex; gap:14px; justify-content:center; flex-wrap:wrap; }
  .btn-wh { background:#fff; color:#0f3460; padding:14px 32px; border-radius:8px; font-weight:800; transition:opacity 0.2s; }
  .btn-wh:hover { opacity:0.9; }
</style>
</head>
<body>
%(NAV)s

<section class="ak-hero">
  <div class="ak-hero-bg"></div>
  <div class="ak-hero-inner">
    <h1>放置された空き家を、<br><em>価値ある資産へ。</em></h1>
    <p>全国に約900万戸もの空き家が存在し、毎年その数は増え続けています。ギグスはAI技術と不動産専門知識を組み合わせ、空き家オーナーの課題を解決します。</p>
    <div class="stat-pills">
      <div class="stat-pill">全国空き家数 <strong>約900万戸</strong></div>
      <div class="stat-pill">空き家率 <strong>13.8%</strong>（総務省2023年）</div>
      <div class="stat-pill">AI調査で <strong>迅速・正確</strong></div>
    </div>
    <div style="display:flex;gap:14px;flex-wrap:wrap;">
      <a href="/contact" class="btn-gold">無料相談はこちら →</a>
      <a href="#flow" style="border:2px solid rgba(255,255,255,0.4);color:#fff;padding:12px 28px;border-radius:8px;font-weight:700;font-size:0.92rem;">ご利用の流れを見る</a>
    </div>
  </div>
</section>

<!-- 問題提起 -->
<section class="problem">
  <div class="si">
    <span class="tag tag-gray">PROBLEM</span>
    <h2 class="h2">空き家問題が深刻化しています</h2>
    <div class="prob-grid">
      <div class="prob-content">
        <p style="font-size:1rem;color:#374151;line-height:1.85;margin-bottom:20px;">
          少子高齢化と人口減少が加速する日本では、相続や転居で空き家となった物件が増え続けています。放置された空き家は資産価値の低下、建物の劣化、近隣への悪影響など、さまざまな問題を引き起こします。
        </p>
        <p style="font-size:0.93rem;color:#4b5563;line-height:1.85;margin-bottom:28px;">
          一方で、空き家は適切な対処を行うことで<strong>有効な資産</strong>になりえます。ギグスはお客様の大切な空き家を、負債から資産へ転換するお手伝いをします。
        </p>
        <div class="prob-stats">
          <div class="ps-item"><div class="ps-num">900<span style="font-size:1rem;">万戸</span></div><div class="ps-label">全国の空き家数（2023年）</div></div>
          <div class="ps-item"><div class="ps-num">13.8<span style="font-size:1rem;">%</span></div><div class="ps-label">過去最高の空き家率</div></div>
          <div class="ps-item"><div class="ps-num">50<span style="font-size:1rem;">%↓</span></div><div class="ps-label">放置による資産価値低下</div></div>
          <div class="ps-item"><div class="ps-num">1/3<span style="font-size:1rem;"></span></div><div class="ps-label">相続空き家の割合</div></div>
        </div>
      </div>
      <div class="prob-img">
        <img src="/static/images/akiya_problem.png" onerror="this.parentElement.style.background='#e5e7eb';this.remove()" alt="空き家問題">
      </div>
    </div>
  </div>
</section>

<!-- ソリューション -->
<section class="solution">
  <div class="si">
    <span class="tag tag-green">SOLUTION</span>
    <h2 class="h2">ギグスの空き家ソリューション</h2>
    <p class="lead">調査から活用・売却まで、ワンストップでサポートします。</p>
    <div class="sol-grid">
      <div class="sol-img">
        <img src="/static/images/akiya_solution.png" onerror="this.parentElement.style.background='#d1ede5';this.remove()" alt="空き家ソリューション">
      </div>
      <div>
        <ul class="sol-points">
          <li>
            <div class="sol-ico">🔍</div>
            <div class="sol-text">
              <h4>AI活用・現地調査報告書</h4>
              <p>Claude Vision APIを搭載したAIシステムで現地写真を自動分析。正確で詳細な調査報告書を迅速に作成します。</p>
            </div>
          </li>
          <li>
            <div class="sol-ico">🏠</div>
            <div class="sol-text">
              <h4>空き家管理代行</h4>
              <p>定期的な見回り・清掃・建物点検などの管理業務を代行。遠方オーナー様も安心してお任せいただけます。</p>
            </div>
          </li>
          <li>
            <div class="sol-ico">💰</div>
            <div class="sol-text">
              <h4>売却・賃貸仲介</h4>
              <p>市場分析に基づく適正価格での売却・賃貸仲介。豊富な買い手・借り手ネットワークで早期成約を目指します。</p>
            </div>
          </li>
          <li>
            <div class="sol-ico">🔨</div>
            <div class="sol-text">
              <h4>リノベーション提案</h4>
              <p>費用対効果の高いリノベーションを提案。資産価値を高め、賃貸収入の最大化をサポートします。</p>
            </div>
          </li>
        </ul>
      </div>
    </div>
  </div>
</section>

<!-- AI技術 -->
<section class="ai-feature">
  <div class="ai-inner">
    <div class="ai-card">
      <div>
        <span class="ai-tag">AI TECHNOLOGY</span>
        <h2>最先端AIで、<br>空き家調査を革新する</h2>
        <p>ギグスはJQCA（一般社団法人日本量子コンピューティング協会）と提携し、Claude Vision AIを活用した現地調査報告書の自動生成システムを導入。従来の人力調査と比べ、スピード・精度・コストのすべてを改善します。</p>
        <ul class="ai-features">
          <li>現地写真をアップロードするだけで詳細な報告書を自動生成</li>
          <li>劣化状況・修繕必要箇所を画像AIが自動判定</li>
          <li>報告書作成時間を従来比80%以上短縮</li>
          <li>全国どこでもオンラインで対応可能</li>
        </ul>
      </div>
      <div class="ai-visual">
        <div class="ai-report-mock">
          <h4>🤖 AI調査報告書 — サンプル</h4>
          <div class="ai-field"><span class="k">物件種別</span><span class="v">木造2階建（築38年）</span></div>
          <div class="ai-field"><span class="k">外壁状態</span><span class="v">軽微な劣化あり</span></div>
          <div class="ai-field"><span class="k">屋根状態</span><span class="v">要点検（経年劣化）</span></div>
          <div class="ai-field"><span class="k">修繕推定費用</span><span class="v">80〜120万円</span></div>
          <div class="ai-field"><span class="k">活用推奨</span><span class="v">賃貸リノベーション</span></div>
          <div class="ai-score">
            <div class="ai-score-num">B+</div>
            <div class="ai-score-label">総合評価スコア</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- ご利用の流れ -->
<section class="flow" id="flow">
  <div class="si">
    <div class="tc">
      <span class="tag tag-navy">FLOW</span>
      <h2 class="h2">ご利用の流れ</h2>
      <p class="lead">お問い合わせから空き家活用まで、ギグスが一貫してサポートします。</p>
    </div>
    <div class="flow-steps">
      <div class="flow-step">
        <div class="step-circle"><span class="sn">STEP</span><span class="sv">1</span></div>
        <h4>無料相談</h4>
        <p>フォームまたはお電話でお気軽にご連絡ください。2営業日以内にご連絡します。</p>
      </div>
      <div class="flow-step">
        <div class="step-circle"><span class="sn">STEP</span><span class="sv">2</span></div>
        <h4>現地調査</h4>
        <p>AIシステムで現地写真を分析し、詳細な調査報告書を作成します。</p>
      </div>
      <div class="flow-step">
        <div class="step-circle"><span class="sn">STEP</span><span class="sv">3</span></div>
        <h4>ご提案</h4>
        <p>調査結果をもとに最適な活用方法（管理・売却・賃貸・リノベ）をご提案します。</p>
      </div>
      <div class="flow-step">
        <div class="step-circle"><span class="sn">STEP</span><span class="sv">4</span></div>
        <h4>ご契約</h4>
        <p>ご納得いただけましたら、ご希望のサービスについてご契約を締結します。</p>
      </div>
      <div class="flow-step">
        <div class="step-circle"><span class="sn">STEP</span><span class="sv">5</span></div>
        <h4>サービス開始</h4>
        <p>管理開始・売却活動・リノベーション工事などをギグスが責任をもって進めます。</p>
      </div>
    </div>
  </div>
</section>

<!-- 料金 -->
<section class="price-sec" id="price">
  <div class="si">
    <div class="tc">
      <span class="tag tag-gold">PRICE</span>
      <h2 class="h2">サービス料金のご案内</h2>
      <p class="lead">まずは無料相談からお気軽にどうぞ。</p>
    </div>
    <div class="price-grid">
      <div class="price-card">
        <span class="badge badge-basic">ライトプラン</span>
        <h3>現地調査のみ</h3>
        <p style="font-size:0.84rem;color:#4b5563;margin-top:8px;">AI調査報告書の作成</p>
        <div class="price">要相談<span> 円〜</span></div>
        <ul>
          <li>AI現地調査報告書</li>
          <li>劣化状況の分析</li>
          <li>修繕費用の概算</li>
          <li>活用方針のアドバイス</li>
        </ul>
        <a href="/contact" class="btn-outline" style="width:100%;justify-content:center;">相談する</a>
      </div>
      <div class="price-card featured">
        <span class="badge badge-std">スタンダード</span>
        <h3>管理代行プラン</h3>
        <p style="font-size:0.84rem;color:#4b5563;margin-top:8px;">空き家の維持管理</p>
        <div class="price">要相談<span> 円/月〜</span></div>
        <ul>
          <li>定期巡回・点検</li>
          <li>清掃・除草対応</li>
          <li>異常時の緊急対応</li>
          <li>月次レポート提供</li>
        </ul>
        <a href="/contact" class="btn-primary" style="width:100%;justify-content:center;">相談する</a>
      </div>
      <div class="price-card">
        <span class="badge badge-prem">フルサポート</span>
        <h3>売却・活用プラン</h3>
        <p style="font-size:0.84rem;color:#4b5563;margin-top:8px;">売却〜賃貸まで一貫対応</p>
        <div class="price">成功報酬<span> 型</span></div>
        <ul>
          <li>現地調査・報告書作成</li>
          <li>売却・賃貸仲介</li>
          <li>リノベーション提案</li>
          <li>契約〜引渡しサポート</li>
        </ul>
        <a href="/contact" class="btn-outline" style="width:100%;justify-content:center;">相談する</a>
      </div>
    </div>
    <p style="text-align:center;margin-top:20px;font-size:0.82rem;color:#6b7280;">※料金は物件の状況・エリア・内容によって異なります。まずはお気軽にご相談ください。</p>
  </div>
</section>

<!-- FAQ -->
<section class="faq-sec" id="faq">
  <div class="si">
    <div class="tc">
      <span class="tag tag-navy">FAQ</span>
      <h2 class="h2">よくあるご質問</h2>
    </div>
    <div class="faq-list">
      <div class="faq-item"><button class="faq-q">遠方に空き家があるのですが、対応してもらえますか？<div class="faq-icon">+</div></button><div class="faq-a">はい、全国対応しております。写真・書類のご提供はオンラインで完結できますので、遠方にお住まいのオーナー様でも安心してご依頼いただけます。まずはお問い合わせフォームよりご連絡ください。</div></div>
      <div class="faq-item"><button class="faq-q">相続した空き家なのですが、相談できますか？<div class="faq-icon">+</div></button><div class="faq-a">もちろんです。相続空き家はギグスが最も多くご相談を承っているケースのひとつです。相続登記のご案内・税務専門家のご紹介も含め、ワンストップでサポートいたします。</div></div>
      <div class="faq-item"><button class="faq-q">AI調査報告書の精度はどれくらいですか？<div class="faq-icon">+</div></button><div class="faq-a">世界最高水準のClaude Vision AIを活用した画像分析を行います。劣化状況・修繕箇所の特定精度は従来の目視調査と同等以上を実現。報告書完成まで最短1営業日で対応できます。</div></div>
      <div class="faq-item"><button class="faq-q">売却するか管理するか迷っています。どちらがよいですか？<div class="faq-icon">+</div></button><div class="faq-a">物件の状態・立地・オーナー様のご希望によって最適解は異なります。ギグスでは現地調査の結果をもとに、売却・管理・賃貸・リノベーションのすべての選択肢をシミュレーションしてご提案します。</div></div>
      <div class="faq-item"><button class="faq-q">費用はいつ発生しますか？<div class="faq-icon">+</div></button><div class="faq-a">初回相談・見積もりは無料です。サービスの種類によって、着手金型・成功報酬型・月額型があります。費用の発生タイミングは契約前に明確にお伝えしますのでご安心ください。</div></div>
    </div>
  </div>
</section>

<section class="ak-cta">
  <h2>空き家でお困りでしたら、<br>まずはご相談ください。</h2>
  <p>初回相談は無料です。オンライン・電話でもお気軽にどうぞ。</p>
  <div class="ak-cta-btns">
    <a href="/contact" class="btn-wh">無料相談フォームへ</a>
    <a href="tel:07083943791" style="border:2px solid rgba(255,255,255,0.4);color:#fff;padding:14px 28px;border-radius:8px;font-weight:700;">📞 お電話で相談</a>
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
#  会社概要
# ─────────────────────────────────────────────────────────────
COMPANY_HTML = """<!DOCTYPE html>
<html lang="ja"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>会社概要 | 有限会社ギグス</title>
%(CSS)s
<style>
  .pg-hero { position:relative; height:480px; display:flex; align-items:center; padding:100px 40px 60px; overflow:hidden; }
  .pg-hero-bg { position:absolute; inset:0; background:url('/static/images/about_hero.png') center/cover; }
  .pg-hero-bg::after { content:''; position:absolute; inset:0; background:rgba(10,20,50,0.78); }
  .pg-hero-inner { position:relative; z-index:1; }
  .pg-hero h1 { font-size:clamp(2rem,4vw,3rem); font-weight:900; color:#fff; line-height:1.2; margin-bottom:12px; }
  .pg-hero p { font-size:1rem; color:rgba(255,255,255,0.72); }

  /* CEO MESSAGE */
  .message-sec { background:#fff; }
  .msg-grid { display:grid; grid-template-columns:280px 1fr; gap:56px; align-items:start; margin-top:56px; }
  @media(max-width:768px){.msg-grid{grid-template-columns:1fr;}}
  .msg-photo { border-radius:20px; overflow:hidden; box-shadow:0 12px 36px rgba(0,0,0,0.12); }
  .msg-photo img { width:100%; height:320px; object-fit:cover; object-position:top; }
  .msg-name { text-align:center; margin-top:14px; }
  .msg-name .name { font-size:1.1rem; font-weight:900; color:#0f172a; }
  .msg-name .role { font-size:0.8rem; color:#6b7280; margin-top:2px; }
  blockquote { border-left:4px solid #0f3460; padding-left:20px; margin:24px 0; }
  blockquote p { font-size:1.05rem; color:#0f3460; font-weight:700; font-style:italic; line-height:1.7; }
  .msg-text p { font-size:0.93rem; color:#374151; line-height:1.95; margin-bottom:16px; }

  /* PHILOSOPHY */
  .philosophy { background:linear-gradient(135deg,#0f3460,#16534a); padding:80px 24px; }
  .ph-inner { max-width:960px; margin:0 auto; text-align:center; }
  .ph-inner h2 { font-size:1.5rem; font-weight:900; color:#fff; margin-bottom:48px; }
  .ph-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:20px; }
  @media(max-width:640px){.ph-grid{grid-template-columns:1fr;}}
  .ph-card { background:rgba(255,255,255,0.08); border:1px solid rgba(255,255,255,0.15); border-radius:16px; padding:32px 24px; }
  .ph-icon { font-size:2rem; margin-bottom:14px; }
  .ph-card h3 { font-size:0.95rem; font-weight:800; color:#fcd34d; margin-bottom:10px; }
  .ph-card p { font-size:0.84rem; color:rgba(255,255,255,0.72); line-height:1.8; }

  /* COMPANY INFO TABLE */
  .info-sec { background:#f7f9fb; }
  .info-table { width:100%; border-collapse:collapse; margin-top:48px; background:#fff; border-radius:16px; overflow:hidden; box-shadow:0 2px 12px rgba(0,0,0,0.06); }
  .info-table tr { border-bottom:1px solid #f3f4f6; }
  .info-table tr:last-child { border-bottom:none; }
  .info-table th { width:180px; padding:18px 24px; background:#f8fafc; font-size:0.85rem; font-weight:700; color:#374151; text-align:left; vertical-align:top; }
  .info-table td { padding:18px 24px; font-size:0.9rem; color:#1f2937; line-height:1.75; }
  @media(max-width:640px){.info-table th{width:120px;}}

  /* LICENSE */
  .license-sec { background:#fff; }
  .lic-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:20px; margin-top:48px; }
  @media(max-width:768px){.lic-grid{grid-template-columns:repeat(2,1fr);}}
  @media(max-width:480px){.lic-grid{grid-template-columns:1fr;}}
  .lic-card { border:2px solid #e0e7f3; border-radius:14px; padding:24px; display:flex; flex-direction:column; gap:8px; }
  .lic-card .lic-year { font-size:0.72rem; font-weight:700; color:#fff; background:#0f3460; padding:3px 10px; border-radius:20px; display:inline-block; width:fit-content; }
  .lic-card h4 { font-size:0.88rem; font-weight:800; color:#0f3460; }
  .lic-card p { font-size:0.82rem; color:#6b7280; }
</style>
</head>
<body>
%(NAV)s

<div class="pg-hero">
  <div class="pg-hero-bg"></div>
  <div class="pg-hero-inner">
    <h1>会社概要</h1>
    <p>有限会社ギグスについてご紹介します。</p>
  </div>
</div>

<section class="message-sec" id="message">
  <div class="si">
    <span class="tag tag-navy">CEO MESSAGE</span>
    <h2 class="h2">代表者メッセージ</h2>
    <div class="msg-grid">
      <div>
        <div class="msg-photo">
          <img src="/static/images/ceo.png" onerror="this.parentElement.style.background='linear-gradient(135deg,#0f3460,#16534a)';this.style.display='none'" alt="代表取締役 高田裕行">
        </div>
        <div class="msg-name">
          <div class="name">高田 裕行</div>
          <div class="role">代表取締役</div>
        </div>
      </div>
      <div class="msg-text">
        <blockquote><p>「不動産は人生の基盤です。その基盤を守り、活かすことが私たちの使命です。」</p></blockquote>
        <p>有限会社ギグスは2006年の創業以来、不動産売買仲介・コンサルティング・M&A仲介を通じて、多くのお客様の資産形成・保全をお手伝いしてまいりました。</p>
        <p>近年、全国で深刻化する空き家問題に取り組むため、最先端のAI技術（Claude Vision API）を活用した現地調査システムを導入しました。迅速・正確・低コストな調査報告で、空き家オーナー様の意思決定を強力にサポートします。</p>
        <p>私たちが大切にしているのは、お客様との長期的な信頼関係です。一時的な取引ではなく、生涯のパートナーとして、不動産に関するあらゆる課題に真摯に向き合い続けます。</p>
        <p>空き家・不動産・M&Aのことなら、ぜひギグスにご相談ください。</p>
      </div>
    </div>
  </div>
</section>

<section class="philosophy" id="philosophy">
  <div class="ph-inner">
    <h2>経営理念</h2>
    <div class="ph-grid">
      <div class="ph-card">
        <div class="ph-icon">🤝</div>
        <h3>信頼</h3>
        <p>お客様の大切な資産に向き合う誠実さと透明性を第一に、長期的な信頼関係を築きます。</p>
      </div>
      <div class="ph-card">
        <div class="ph-icon">💡</div>
        <h3>革新</h3>
        <p>AI・テクノロジーを積極的に活用し、不動産業界に新しい価値と可能性をもたらします。</p>
      </div>
      <div class="ph-card">
        <div class="ph-icon">🌱</div>
        <h3>貢献</h3>
        <p>空き家問題の解決など、社会課題に向き合いながら地域と社会の持続的な発展に貢献します。</p>
      </div>
    </div>
  </div>
</section>

<section class="info-sec">
  <div class="si">
    <span class="tag tag-gray">COMPANY INFO</span>
    <h2 class="h2">会社概要</h2>
    <table class="info-table">
      <tr><th>会社名</th><td>有限会社ギグス（GIGS CORP.）</td></tr>
      <tr><th>代表取締役</th><td>高田 裕行</td></tr>
      <tr><th>設立</th><td>2006年1月4日</td></tr>
      <tr><th>所在地</th><td>〒113-0021 東京都文京区本駒込二丁目5番3号</td></tr>
      <tr><th>電話番号</th><td>070-8394-3791（平日9:00〜18:00）</td></tr>
      <tr><th>メール</th><td>info@gigscorp.jp</td></tr>
      <tr><th>ウェブサイト</th><td>https://gigscorp.jp</td></tr>
      <tr><th>事業内容</th><td>不動産売買仲介・賃貸仲介 / 不動産コンサルティング / 空き家ビジネス（調査・管理・売却仲介） / M&A仲介 / ホームページ制作・システム開発</td></tr>
    </table>
  </div>
</section>

<section class="license-sec" id="license">
  <div class="si">
    <span class="tag tag-navy">LICENSE &amp; QUALIFICATION</span>
    <h2 class="h2">代表者 保有資格</h2>
    <p class="lead" style="margin-bottom:0;">代表取締役 高田裕行が保有する専門資格です。</p>
    <div class="lic-grid">
      <div class="lic-card">
        <span class="lic-year">1995年取得</span>
        <h4>1級建築施工管理技士</h4>
        <p>国家資格。建築工事の施工管理における最上位資格。</p>
      </div>
      <div class="lic-card">
        <span class="lic-year">2001年取得</span>
        <h4>宅地建物取引士</h4>
        <p>国家資格。不動産取引の専門家として法的に認定。</p>
      </div>
      <div class="lic-card">
        <span class="lic-year">2009年取得</span>
        <h4>不動産コンサルティングマスター</h4>
        <p>公益財団法人不動産流通推進センター認定。不動産の高度なコンサルティング能力を証明。</p>
      </div>
      <div class="lic-card">
        <span class="lic-year">2010年取得</span>
        <h4>AFP（Affiliated Financial Planner）</h4>
        <p>日本FP協会認定。資産運用・相続・税務など総合的なファイナンシャルプランニング資格。</p>
      </div>
      <div class="lic-card">
        <span class="lic-year">2021年取得</span>
        <h4>住宅ローンアドバイザー</h4>
        <p>住宅金融普及協会認定。住宅ローンに関する専門知識と相談対応能力を証明。</p>
      </div>
      <div class="lic-card">
        <span class="lic-year">2022年取得</span>
        <h4>賃貸不動産経営管理士</h4>
        <p>国家資格。賃貸住宅の管理に関する専門的知識・技能を証明。</p>
      </div>
    </div>
  </div>
</section>

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

@app.route('/')
def home():
    return render(HOME_HTML, "ホーム")

@app.route('/akiya')
def akiya():
    return render(AKIYA_HTML, "空き家ビジネス")

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
