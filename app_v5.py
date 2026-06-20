# ═══════════════════════════════════════════════════════════════════════════════
# 📈  AI Trading Assistant IHSG — Versi 5.0
#     NEW: Claude AI Discussion + Intraday (5m/15m) + Fundamental Analysis
#     Semua fitur v4 dipertahankan.
# ═══════════════════════════════════════════════════════════════════════════════

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, date
import warnings
warnings.filterwarnings("ignore")

# Anthropic (optional - only if API key provided)
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

st.set_page_config(page_title="📈 IHSG Assistant v5", page_icon="📈",
                   layout="wide", initial_sidebar_state="collapsed")

LQ45 = sorted(list(set([
    "ADRO","AKRA","AMRT","ANTM","ASII","BBCA","BBNI","BBRI","BBTN","BMRI",
    "BREN","BSDE","CPIN","CTRA","EMTK","EXCL","GGRM","GOTO","HMSP","ICBP",
    "INCO","INDF","INTP","ITMG","JPFA","KLBF","LPPF","MDKA","MEDC","MYOR",
    "PGAS","PTBA","PWON","SIDO","SMGR","SMRA","TBIG","TLKM","TOWR","TPIA",
    "UNTR","UNVR","WSKT","BNGA","PANI",
])))

st.markdown("""<style>
.rec-card{border-radius:14px;padding:20px;text-align:center;color:#fff;margin:8px 0;}
.beli-kuat{background:linear-gradient(135deg,#00701a,#00e676);}
.beli{background:linear-gradient(135deg,#0d47a1,#42a5f5);}
.tahan{background:linear-gradient(135deg,#b45309,#fbbf24);}
.jual{background:linear-gradient(135deg,#9a3412,#fb923c);}
.jual-kuat{background:linear-gradient(135deg,#450a0a,#b91c1c);}
.rec-label{font-size:.8em;font-weight:700;letter-spacing:2px;text-transform:uppercase;opacity:.85;}
.rec-action{font-size:2.2em;font-weight:900;margin:4px 0;}
.rec-score{font-size:1em;opacity:.9;}
.rec-desc{font-size:.9em;margin-top:8px;}
.rec-price{font-size:1em;margin-top:8px;}
.tf-box{border-radius:10px;padding:14px;text-align:center;border:1px solid rgba(255,255,255,.1);background:rgba(255,255,255,.03);}
.tf-title{font-size:.75em;color:#9e9e9e;font-weight:700;letter-spacing:1px;text-transform:uppercase;}
.tf-signal{font-size:1.25em;font-weight:800;margin:5px 0;}
.tf-detail{font-size:.78em;color:#bbb;line-height:1.5;}
.conf-bar{border-radius:10px;padding:12px 16px;text-align:center;margin:8px 0;border:1px solid rgba(255,255,255,.1);}
.tp-card{border-radius:12px;padding:16px 18px;margin:8px 0;background:rgba(66,165,245,.07);border:1px solid rgba(66,165,245,.2);}
.tp-exit{background:rgba(255,152,0,.07);border:1px solid rgba(255,152,0,.2);}
.tp-title{font-size:.85em;font-weight:700;color:#9e9e9e;letter-spacing:1px;text-transform:uppercase;margin-bottom:10px;}
.tp-row{display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px solid rgba(255,255,255,.05);font-size:.9em;}
.tp-row:last-child{border-bottom:none;}
.tp-lbl{color:#9e9e9e;} .tp-val{font-weight:700;}
.tp-entry{color:#42a5f5!important;} .tp-sl{color:#ef5350!important;}
.tp-tp1{color:#66bb6a!important;} .tp-tp2{color:#4caf50!important;}
.tp-note{font-size:.82em;color:#bbb;margin-top:8px;font-style:italic;}
.override-box{background:rgba(255,152,0,.08);border-left:4px solid #ff9800;border-radius:8px;padding:10px 12px;margin:4px 0;font-size:.9em;}
.boost-box{background:rgba(76,175,80,.08);border-left:4px solid #4caf50;border-radius:8px;padding:10px 12px;margin:4px 0;font-size:.9em;}
.phase-card{border-radius:8px;padding:12px 14px;margin:6px 0;border-left:4px solid;background:rgba(255,255,255,.03);}
.div-warn{background:rgba(244,67,54,.07);border-left:4px solid #f44336;border-radius:6px;padding:10px 12px;margin:4px 0;}
.div-bull{background:rgba(76,175,80,.07);border-left:4px solid #4caf50;border-radius:6px;padding:10px 12px;margin:4px 0;}
.sr-r{display:inline-block;background:rgba(244,67,54,.15);border:1px solid rgba(244,67,54,.4);color:#ef9a9a;border-radius:5px;padding:2px 8px;margin:2px;font-size:.82em;font-weight:600;}
.sr-s{display:inline-block;background:rgba(76,175,80,.15);border:1px solid rgba(76,175,80,.4);color:#a5d6a7;border-radius:5px;padding:2px 8px;margin:2px;font-size:.82em;font-weight:600;}
.fib-badge{display:inline-block;border-radius:4px;padding:2px 7px;margin:2px;font-size:.8em;font-weight:600;border:1px solid rgba(255,255,255,.15);}
.pos-card{border-radius:12px;padding:14px 16px;margin:6px 0;border:1px solid;background:rgba(255,255,255,.03);}
.pos-profit{border-color:rgba(76,175,80,.4);} .pos-loss{border-color:rgba(244,67,54,.4);} .pos-even{border-color:rgba(158,158,158,.3);}
.decision-card{border-radius:12px;padding:16px;margin:10px 0;border-left:5px solid;}
.decision-cutloss{background:rgba(244,67,54,.1);border-color:#f44336;}
.decision-profit{background:rgba(76,175,80,.1);border-color:#4caf50;}
.decision-avgdown{background:rgba(66,165,245,.1);border-color:#42a5f5;}
.decision-hold{background:rgba(158,158,158,.1);border-color:#9e9e9e;}
.decision-warn{background:rgba(255,152,0,.1);border-color:#ff9800;}
.ai-badge{display:inline-block;background:rgba(171,71,188,.2);border:1px solid rgba(171,71,188,.5);color:#ce93d8;border-radius:10px;padding:2px 8px;font-size:.75em;font-weight:700;margin-left:6px;}
.rule-badge{display:inline-block;background:rgba(97,97,97,.2);border:1px solid rgba(97,97,97,.5);color:#9e9e9e;border-radius:10px;padding:2px 8px;font-size:.75em;font-weight:700;margin-left:6px;}
.fund-card{border-radius:10px;padding:14px 16px;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.08);margin:6px 0;}
.fund-good{color:#4caf50;font-weight:700;} .fund-bad{color:#f44336;font-weight:700;} .fund-neutral{color:#9e9e9e;font-weight:700;}
</style>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# FUNGSI TEKNIKAL DASAR
# ════════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=180)
def fetch_tf(ticker, period, interval="1d"):
    try:
        df=yf.download(ticker,period=period,interval=interval,progress=False,auto_adjust=True)
        if df.empty: return None
        if isinstance(df.columns,pd.MultiIndex): df.columns=df.columns.get_level_values(0)
        df.index=pd.to_datetime(df.index)
        if hasattr(df.index,'tz') and df.index.tz is not None: df.index=df.index.tz_localize(None)
        return df.dropna(how="all")
    except: return None

def calc_rsi(s,p=14):
    d=s.diff();g=d.clip(lower=0);l=(-d).clip(lower=0)
    ag=g.ewm(com=p-1,min_periods=p).mean();al=l.ewm(com=p-1,min_periods=p).mean()
    return (100-100/(1+ag/al.replace(0,np.nan))).fillna(50)

def calc_macd(s,f=12,sl_=26,sig=9):
    m=s.ewm(span=f,adjust=False).mean()-s.ewm(span=sl_,adjust=False).mean()
    sg=m.ewm(span=sig,adjust=False).mean();return m,sg,m-sg

def calc_bb(s,p=20,k=2):
    sma=s.rolling(p).mean();std=s.rolling(p).std();return sma+k*std,sma,sma-k*std

def calc_vwap(df):
    tp=(df['High']+df['Low']+df['Close'])/3
    return (tp*df['Volume']).cumsum()/df['Volume'].cumsum()

def calc_fibonacci(df,lookback=120):
    d=df.tail(min(lookback,len(df)));sh=float(d['High'].max());sl=float(d['Low'].min());diff=sh-sl
    return {"0%":sh,"23.6%":sh-0.236*diff,"38.2%":sh-0.382*diff,"50%":sh-0.500*diff,
            "61.8%":sh-0.618*diff,"78.6%":sh-0.786*diff,"100%":sl},sh,sl

def fmt_idr(n):
    for d,sfx in [(1e12,"T"),(1e9,"M"),(1e6,"jt"),(1e3,"rb")]:
        if n>=d: return f"{n/d:.1f}{sfx}"
    return str(int(n))


# ════════════════════════════════════════════════════════════════════════════════
# ANALISIS TEKNIKAL (LAGGING + LEADING — sama seperti v4)
# ════════════════════════════════════════════════════════════════════════════════

def analyze_trend(df):
    c=df["Close"];price=float(c.iloc[-1]);ma20=float(c.rolling(20).mean().iloc[-1])
    ma50=float(c.rolling(50).mean().iloc[-1]) if len(c)>=50 else None
    ma200=float(c.rolling(200).mean().iloc[-1]) if len(c)>=200 else None
    raw,sigs=0,[]
    if price>ma20: raw+=10;sigs.append(("✅",f"Harga > MA20 (Rp{ma20:,.0f}) — Tren Pendek: **NAIK**"))
    else: raw-=5;sigs.append(("❌",f"Harga < MA20 (Rp{ma20:,.0f}) — Tren Pendek: **TURUN**"))
    if ma50:
        if price>ma50: raw+=15;sigs.append(("✅",f"Harga > MA50 (Rp{ma50:,.0f}) — Tren Menengah: **NAIK**"))
        else: raw-=10;sigs.append(("❌",f"Harga < MA50 (Rp{ma50:,.0f}) — Tren Menengah: **TURUN**"))
    else: sigs.append(("ℹ️","MA50 belum tersedia"))
    if ma200:
        if price>ma200: raw+=15;sigs.append(("✅",f"Harga > MA200 (Rp{ma200:,.0f}) — Tren Panjang: **NAIK**"))
        else: raw-=15;sigs.append(("❌",f"Harga < MA200 (Rp{ma200:,.0f}) — Tren Panjang: **TURUN**"))
    else: sigs.append(("ℹ️","MA200 belum tersedia — gunakan periode 1-2 Tahun"))
    if ma50 and ma200:
        if ma50>ma200: raw+=10;sigs.append(("⭐","**Golden Cross** aktif!"))
        else: raw-=10;sigs.append(("💀","**Death Cross** aktif!"))
    return dict(score=float(np.clip(((raw+40)/80)*40,0,40)),price=price,ma20=ma20,ma50=ma50,ma200=ma200,signals=sigs)

def analyze_rsi(df):
    rsi_s=calc_rsi(df["Close"]);rsi=float(rsi_s.iloc[-1])
    buckets=[(25,22,"SANGAT OVERSOLD 🔥",f"RSI {rsi:.1f} — sangat murah, potensi reversal."),
             (35,18,"OVERSOLD",f"RSI {rsi:.1f} — oversold, tunggu konfirmasi."),
             (45,11,"LEMAH",f"RSI {rsi:.1f} — momentum lemah."),
             (55,16,"NETRAL",f"RSI {rsi:.1f} — netral."),
             (65,24,"BULLISH 📈",f"RSI {rsi:.1f} — momentum positif."),
             (75,15,"OVERBOUGHT ⚠️",f"RSI {rsi:.1f} — mendekati overbought."),
             (999,5,"SANGAT OB 🚨",f"RSI {rsi:.1f} — overbought!")]
    for thr,sc,lbl,msg in buckets:
        if rsi<thr: return dict(score=sc,rsi=rsi,label=lbl,signals=[("📊",msg)],series=rsi_s)
    return dict(score=15,rsi=rsi,label="N/A",signals=[],series=rsi_s)

def analyze_volume(df):
    vol=df["Volume"];cur=float(vol.iloc[-1]);avg=float(vol.rolling(20).mean().iloc[-1])
    ratio=cur/avg if avg>0 else 1.0;pchg=(float(df["Close"].iloc[-1])/float(df["Close"].iloc[-2])-1)*100
    if ratio>=3.0: sc,lbl=27,f"SANGAT TINGGI ({ratio:.1f}×)"
    elif ratio>=2.0: sc,lbl=21,f"TINGGI ({ratio:.1f}×)"
    elif ratio>=1.5: sc,lbl=16,f"DI ATAS RATA-RATA ({ratio:.1f}×)"
    elif ratio>=1.0: sc,lbl=11,f"NORMAL ({ratio:.1f}×)"
    else: sc,lbl=5,f"RENDAH ({ratio:.2f}×)"
    sigs=[("📊",f"Volume: **{lbl}** dari rata-rata 20 hari")]
    if ratio>=1.5 and pchg>0: sigs.append(("💚",f"+{pchg:.1f}% dg vol tinggi → Konfirmasi BULLISH"));sc=min(30,sc+3)
    elif ratio>=1.5 and pchg<0: sigs.append(("🔴",f"{pchg:.1f}% dg vol tinggi → Tekanan JUAL"));sc=max(3,sc-4)
    elif ratio<1.0: sigs.append(("💛",f"Volume rendah ({pchg:+.1f}%) — pergerakan kurang meyakinkan."))
    return dict(score=sc,ratio=ratio,label=lbl,signals=sigs,pchg=pchg)

def get_rec(trend,rsi_d,vol):
    total=float(np.clip(trend["score"]+rsi_d["score"]+vol["score"],0,100));rsi=rsi_d["rsi"]
    if total>=72: r,e,c="BELI KUAT","🟢","beli-kuat";d="Semua lampu hijau!"
    elif total>=58: r,e,c="BELI","🔵","beli";d="Kondisi mendukung, masuk bertahap."
    elif total>=43: r,e,c="TAHAN","🟡","tahan";d="Sinyal campur, tunggu konfirmasi."
    elif total>=28: r,e,c="JUAL","🟠","jual";d="Tekanan jual mulai dominan."
    else: r,e,c="JUAL KUAT","🔴","jual-kuat";d="Semua lampu merah."
    if rsi>76 and total>=58: r,e,c="TAHAN","⚠️","tahan";d=f"RSI {rsi:.1f} — overbought parah!"
    elif rsi<24 and total<=43: r,e,c="BELI","🔥","beli";d=f"RSI {rsi:.1f} — oversold parah!"
    return dict(rec=r,emoji=e,css=c,desc=d,score=total)

def find_sr_zones(df,pivot_w=5,cluster_pct=0.015):
    high=df["High"].values;low=df["Low"].values;price=float(df["Close"].iloc[-1]);n,w=len(high),pivot_w
    sh,sl=[],[]
    for i in range(w,n-w):
        if high[i]==max(high[i-w:i+w+1]): sh.append(float(high[i]))
        if low[i]==min(low[i-w:i+w+1]): sl.append(float(low[i]))
    def cluster(lvs,pct):
        if not lvs: return []
        lvs=sorted(set(lvs));res,cur=[],[lvs[0]]
        for lv in lvs[1:]:
            if (lv-cur[0])/cur[0]<=pct: cur.append(lv)
            else: res.append(float(np.mean(cur)));cur=[lv]
        res.append(float(np.mean(cur)));return res
    resistance=sorted([l for l in cluster(sh,cluster_pct) if l>price*1.002])[:4]
    support=sorted([l for l in cluster(sl,cluster_pct) if l<price*0.998],reverse=True)[:4]
    rd=[(r-price)/price*100 for r in resistance];sd=[(price-s)/price*100 for s in support]
    return dict(resistance=resistance,support=support,res_dist=rd,sup_dist=sd,
                nearest_res=resistance[0] if resistance else None,nearest_sup=support[0] if support else None,
                nearest_res_dist=rd[0] if rd else None,nearest_sup_dist=sd[0] if sd else None)

def detect_divergence(df,rsi_series,lookback=60,min_gap=6):
    if len(df)<lookback+5: return dict(bullish=False,bearish=False,bull_desc="",bear_desc="")
    close=df["Close"].values[-lookback:];rsi=rsi_series.values[-lookback:];n=len(close)
    li,hi=[],[]
    for i in range(3,n-3):
        if close[i]<close[i-1] and close[i]<close[i-2] and close[i]<close[i+1] and close[i]<close[i+2]:
            if not li or i-li[-1]>=min_gap: li.append(i)
        if close[i]>close[i-1] and close[i]>close[i-2] and close[i]>close[i+1] and close[i]>close[i+2]:
            if not hi or i-hi[-1]>=min_gap: hi.append(i)
    bull,bear=False,False;bd,brd="",""
    if len(li)>=2:
        i1,i2=li[-2],li[-1]
        if close[i2]<close[i1] and rsi[i2]>rsi[i1]:
            bull=True;bd=f"Harga Rp{close[i1]:,.0f}→Rp{close[i2]:,.0f} (lower low) | RSI {rsi[i1]:.0f}→{rsi[i2]:.0f} (higher low)"
    if len(hi)>=2:
        i1,i2=hi[-2],hi[-1]
        if close[i2]>close[i1] and rsi[i2]<rsi[i1]:
            bear=True;brd=f"Harga Rp{close[i1]:,.0f}→Rp{close[i2]:,.0f} (higher high) | RSI {rsi[i1]:.0f}→{rsi[i2]:.0f} (lower high)"
    return dict(bullish=bull,bearish=bear,bull_desc=bd,bear_desc=brd)

def detect_candle_patterns(df):
    if len(df)<4: return [("➡️","Data candle kurang.")]
    patterns=[]
    def props(c):
        o,h,l,cl=float(c["Open"]),float(c["High"]),float(c["Low"]),float(c["Close"])
        b=abs(cl-o);rng=max(h-l,0.001);return o,h,l,cl,b,rng,h-max(o,cl),min(o,cl)-l,(cl>=o)
    o0,h0,l0,cl0,b0,r0,uw0,lw0,bull0=props(df.iloc[-1])
    o1,h1,l1,cl1,b1,r1,uw1,lw1,bull1=props(df.iloc[-2])
    o2,h2,l2,cl2,b2,r2,uw2,lw2,bull2=props(df.iloc[-3])
    if lw0>=2*b0 and uw0<=0.4*b0: patterns.append(("🔨","**HAMMER** — Sinyal reversal bullish."))
    if bull0 and not bull1 and cl0>=o1 and o0<=cl1 and b0>=b1*0.7: patterns.append(("🟢","**BULLISH ENGULFING** — Candle hijau menelan merah."))
    if not bull2 and b2>r2*0.4 and b1<r1*0.3 and bull0 and cl0>(o2+cl2)/2: patterns.append(("🌅","**MORNING STAR** — Pola 3-candle reversal ke atas!"))
    if uw0>=2*b0 and lw0<=0.4*b0 and not bull0: patterns.append(("🌠","**SHOOTING STAR** — Sinyal reversal bearish."))
    if not bull0 and bull1 and o0>=cl1 and cl0<=o1 and b0>=b1*0.7: patterns.append(("🔴","**BEARISH ENGULFING** — Candle merah menelan hijau."))
    if bull2 and b2>r2*0.4 and b1<r1*0.3 and not bull0 and cl0<(o2+cl2)/2: patterns.append(("🌆","**EVENING STAR** — Pola 3-candle reversal ke bawah!"))
    if b0<=r0*0.07 and r0>0: patterns.append(("🔄","**DOJI** — Pasar ragu-ragu."))
    if not patterns: patterns.append(("➡️","Tidak ada pola candle reversal signifikan hari ini."))
    return patterns

def detect_market_phase(df,trend,rsi_d):
    close=df["Close"];price=trend["price"];ma50,ma200=trend["ma50"],trend["ma200"];rsi=rsi_d["rsi"]
    chg_20d=(price/float(close.iloc[-20])-1)*100 if len(close)>=20 else 0
    above50=ma50 is not None and price>ma50;above200=ma200 is not None and price>ma200
    gc=ma50 is not None and ma200 is not None and ma50>ma200
    dc=ma50 is not None and ma200 is not None and ma50<ma200
    if above50 and above200 and gc:
        if rsi>=65 and chg_20d>5: return dict(phase="DISTRIBUSI 🔔",color="#ff9800",desc="Rally matang, RSI tinggi.",action="⚠️ Take profit sebagian! Lagging hijau tapi itu justru tandanya waspada.")
        elif rsi<50 and chg_20d<0: return dict(phase="PULLBACK dalam UPTREND 🔄",color="#42a5f5",desc="Tren panjang bullish, koreksi sementara.",action="✅ Peluang entry lebih bagus — beli di dip dalam uptrend!")
        else: return dict(phase="MARKUP (UPTREND) 📈",color="#4caf50",desc="Semua MA bullish, Golden Cross aktif.",action="📈 Ikuti tren, gunakan SL, perhatikan resistance terdekat.")
    elif not above50 and not above200 and dc:
        if rsi<=35 and chg_20d>-5: return dict(phase="AKUMULASI 🌱",color="#00e676",desc="RSI oversold, penurunan melambat.",action="🔥 Zona cicil beli (DCA)! Ini yang dicari investor sabar.")
        else: return dict(phase="MARKDOWN (DOWNTREND) 📉",color="#f44336",desc="Harga di bawah MA50 & MA200, Death Cross aktif.",action="🚫 Jangan lawan tren turun. Tunggu reversal nyata.")
    elif above50 and not above200: return dict(phase="RECOVERY ↗️",color="#ffb300",desc="Di atas MA50 tapi di bawah MA200.",action="⚡ MA200 = resistance besar. Beli bertahap.")
    elif not above50 and above200: return dict(phase="KOREKSI dalam UPTREND ⚠️",color="#ff9800",desc="Di bawah MA50 tapi masih di atas MA200.",action="⚡ Kalau MA200 hold = titik entry bagus.")
    else: return dict(phase="KONSOLIDASI ↔️",color="#9e9e9e",desc="Sideways, belum ada tren jelas.",action="⏸️ Tunggu breakout dengan volume tinggi.")

def apply_smart_override(base_rec,sr,div,phase,candles):
    smart={k:v for k,v in base_rec.items()};overrides,boosts=[],[];changed=False;base=base_rec["rec"]
    nr,nrd=sr.get("nearest_res"),sr.get("nearest_res_dist")
    ns,nsd=sr.get("nearest_sup"),sr.get("nearest_sup_dist");phase_name=phase.get("phase","")
    msgs=[m for _,m in candles]
    has_bull=any(k in m for m in msgs for k in ["HAMMER","BULLISH ENGUL","MORNING STAR"])
    has_bear=any(k in m for m in msgs for k in ["SHOOTING","BEARISH ENGUL","EVENING STAR"])
    if nr and nrd is not None and nrd<=3.5:
        overrides.append(f"⛔ Hanya **{nrd:.1f}%** dari Resistance **Rp{nr:,.0f}** — area berbahaya beli baru!")
        if base in ["BELI KUAT","BELI"] and not changed:
            smart.update(rec="TAHAN",emoji="⚠️",css="tahan",desc=f"Dekat resistance Rp{nr:,.0f}. Tunggu breakout!");changed=True
    if div.get("bearish"):
        overrides.append(f"📉 **Bearish Divergence**: {div.get('bear_desc','')} — sinyal puncak!")
        if base in ["BELI KUAT","BELI"] and not changed:
            smart.update(rec="TAHAN",emoji="⚠️",css="tahan",desc="Bearish divergence terdeteksi!");changed=True
    if "DISTRIBUSI" in phase_name: overrides.append("🔔 **Fase Distribusi** — Lagging hijau tapi justru bahayanya!")
    if ns and nsd is not None and nsd<=3.5:
        boosts.append(f"💚 **Di zona Support Rp{ns:,.0f}** ({nsd:.1f}%) — buyer historis masuk di sini!")
        if base in ["TAHAN"] and not changed:
            smart.update(rec="BELI",emoji="🔥",css="beli",desc=f"Di zona support Rp{ns:,.0f}. Cicil beli dengan SL di bawah support.");changed=True
    if div.get("bullish"):
        boosts.append(f"📈 **Bullish Divergence**: {div.get('bull_desc','')} — leading signal reversal!")
        if base in ["JUAL","TAHAN"] and not changed:
            smart.update(rec="BELI",emoji="🔥",css="beli",desc="Bullish divergence! Seller kehabisan tenaga.");changed=True
    if "AKUMULASI" in phase_name: boosts.append("🌱 **Fase Akumulasi** — zona terbaik cicil beli!")
    smart["was_changed"]=changed
    return dict(smart_rec=smart,overrides=overrides,boosts=boosts)

def analyze_weekly(df_w):
    if df_w is None or len(df_w)<8: return dict(signal="N/A",color="#9e9e9e",rsi=50,desc="Data tidak tersedia.",bull_pts=2,price=0,ma20=0,wchg=0)
    c=df_w["Close"];price=float(c.iloc[-1]);ma20=float(c.rolling(min(20,len(c))).mean().iloc[-1])
    ma50=float(c.rolling(min(50,len(c))).mean().iloc[-1]);rsi=float(calc_rsi(c).iloc[-1])
    macd,sig,_=calc_macd(c);mb=float(macd.iloc[-1])>float(sig.iloc[-1])
    wchg=(price/float(c.iloc[-2])-1)*100 if len(c)>=2 else 0
    bp=sum([price>ma20,price>ma50,rsi>50,mb])
    if bp>=3: signal,color="BULLISH 📈","#4caf50";desc=f"Tren Weekly naik. RSI: {rsi:.0f}."
    elif bp<=1: signal,color="BEARISH 📉","#f44336";desc=f"Tren Weekly turun. RSI: {rsi:.0f}."
    else: signal,color="SIDEWAYS ↔️","#9e9e9e";desc=f"Tren Weekly belum jelas. RSI: {rsi:.0f}."
    return dict(signal=signal,color=color,rsi=rsi,desc=desc,price=price,ma20=ma20,ma50=ma50,bull_pts=bp,wchg=wchg)

def analyze_hourly(df_h):
    if df_h is None or len(df_h)<20: return dict(signal="N/A",color="#9e9e9e",rsi=50,desc="Data tidak tersedia.",vwap=None,vwap_val=0,bull_pts=2,hchg=0)
    c=df_h["Close"];price=float(c.iloc[-1]);rsi=float(calc_rsi(c).iloc[-1])
    macd,sig,_=calc_macd(c);mb=float(macd.iloc[-1])>float(sig.iloc[-1])
    vwap=calc_vwap(df_h);vv=float(vwap.iloc[-1]);av=price>vv
    hchg=(price/float(c.iloc[-2])-1)*100 if len(c)>=2 else 0
    bp=sum([rsi>50,mb,av]);vwap_pct=(price-vv)/vv*100
    if bp>=3: signal,color="BULLISH 📈","#4caf50";desc=f"RSI: {rsi:.0f} · {'Di atas' if av else 'Di bawah'} VWAP Rp{vv:,.0f} ({vwap_pct:+.1f}%)"
    elif bp<=1: signal,color="BEARISH 📉","#f44336";desc=f"RSI: {rsi:.0f} · {'Di atas' if av else 'Di bawah'} VWAP Rp{vv:,.0f} ({vwap_pct:+.1f}%)"
    else: signal,color="NETRAL ↔️","#9e9e9e";desc=f"RSI: {rsi:.0f} · VWAP Rp{vv:,.0f} ({vwap_pct:+.1f}%)"
    return dict(signal=signal,color=color,rsi=rsi,desc=desc,vwap=vwap,vwap_val=vv,above_vwap=av,price=price,bull_pts=bp,hchg=hchg)

def get_confluence(w,d_rec,h):
    wb=w.get("bull_pts",2)>=3;wbr=w.get("bull_pts",2)<=1
    db=d_rec.get("rec","") in ["BELI","BELI KUAT"];dbr=d_rec.get("rec","") in ["JUAL","JUAL KUAT"]
    hb=h.get("bull_pts",2)>=3;hbr=h.get("bull_pts",2)<=1
    bc=sum([wb,db,hb]);brc=sum([wbr,dbr,hbr])
    if bc==3: conf,cc,q="SANGAT BULLISH 🟢🟢🟢","#00e676","3/3 TF bullish — SINYAL TERKUAT!"
    elif bc==2: conf,cc,q="BULLISH 🟢🟢","#42a5f5","2/3 TF bullish — sinyal bagus"
    elif brc==3: conf,cc,q="SANGAT BEARISH 🔴🔴🔴","#f44336","3/3 TF bearish — HINDARI!"
    elif brc==2: conf,cc,q="BEARISH 🔴🔴","#ff9800","2/3 TF bearish — hati-hati"
    else: conf,cc,q="MIXED ↔️","#9e9e9e","sinyal campur — tunggu kejelasan"
    return dict(confluence=conf,color=cc,quality=q,bull_count=bc,bear_count=brc)

def generate_trade_plan(price,sr,daily_rec,confluence):
    resistance=sr.get("resistance",[]);nr=sr.get("nearest_res");ns=sr.get("nearest_sup")
    rec=daily_rec.get("rec","TAHAN");bc=confluence.get("bull_count",0);brc=confluence.get("bear_count",0)
    if (rec in ["BELI","BELI KUAT"] or bc>=2) and ns and nr:
        entry_mid=(price+ns*1.003)/2;sl=ns*0.984;tp1=nr
        tp2=resistance[1] if len(resistance)>=2 else nr+(nr-entry_mid)*1.5
        risk=entry_mid-sl
        if risk<=0: return None
        rr1=(tp1-entry_mid)/risk;rr2=(tp2-entry_mid)/risk
        return dict(type="BUY",valid=rr1>=1.0,entry_low=ns*1.003,entry_high=price*1.008,entry_mid=entry_mid,
                    sl=sl,tp1=tp1,tp2=tp2,rr1=rr1,rr2=rr2,
                    sl_pct=(entry_mid-sl)/entry_mid*100,tp1_pct=(tp1-entry_mid)/entry_mid*100,tp2_pct=(tp2-entry_mid)/entry_mid*100)
    elif (rec in ["JUAL","JUAL KUAT"] or brc>=2) and nr:
        return dict(type="EXIT",valid=True,exit_target=nr*0.995,note=f"Take profit posisi long di sekitar Rp{nr*0.995:,.0f}.")
    return None

def quick_screen(ticker_jk):
    try:
        df=fetch_tf(ticker_jk,"3mo","1d")
        if df is None or len(df)<20: return None
        c=df['Close'];price=float(c.iloc[-1]);prev=float(c.iloc[-2]);chg=(price/prev-1)*100
        rsi=float(calc_rsi(c).iloc[-1]);ma20=float(c.rolling(20).mean().iloc[-1])
        ma50=float(c.rolling(min(50,len(c))).mean().iloc[-1])
        vol=df['Volume'];vr=float(vol.iloc[-1])/float(vol.rolling(20).mean().iloc[-1])
        macd,sig,_=calc_macd(c);mb=float(macd.iloc[-1])>float(sig.iloc[-1])
        sc=50
        if price>ma20: sc+=8
        else: sc-=8
        if price>ma50: sc+=12
        else: sc-=10
        if 45<=rsi<=65: sc+=10
        elif rsi<35: sc+=6
        elif rsi>70: sc-=10
        if vr>=2.0: sc+=8
        elif vr>=1.5: sc+=4
        if mb: sc+=7
        else: sc-=5
        sc=max(0,min(100,sc))
        if price>ma50: phase="Uptrend ↑" if rsi>50 else "Pullback 🔄"
        elif rsi<35: phase="Oversold 🔥"
        else: phase="Downtrend ↓"
        sig_txt="🟢 BELI" if sc>=65 else ("🟡 TAHAN" if sc>=50 else "🔴 JUAL")
        return dict(ticker=ticker_jk.replace(".JK",""),price=price,chg=round(chg,2),score=sc,
                    rsi=round(rsi,1),phase=phase,vol_ratio=round(vr,1),signal=sig_txt,vs_ma50=round((price/ma50-1)*100,1))
    except: return None


# ════════════════════════════════════════════════════════════════════════════════
# FUNGSI BARU v5 — AI + INTRADAY + FUNDAMENTAL
# ════════════════════════════════════════════════════════════════════════════════

def build_ai_context(position_metrics, R):
    """Build comprehensive context for Claude AI."""
    ticker=R["ticker"]; trend=R["trend"]; rsi_d=R["rsi_d"]; vol=R["vol"]
    sr=R["sr"]; div=R["div"]; phase=R["phase"]; conf=R["conf"]
    smart_rec=R["smart"]["smart_rec"]; fib=R["fib"]
    price=trend["price"]

    res_str=" | ".join([f"Rp{r:,.0f}(+{d:.1f}%)" for r,d in zip(sr["resistance"][:3],sr["res_dist"][:3])]) if sr["resistance"] else "tidak terdeteksi"
    sup_str=" | ".join([f"Rp{s:,.0f}(-{d:.1f}%)" for s,d in zip(sr["support"][:3],sr["sup_dist"][:3])]) if sr["support"] else "tidak terdeteksi"
    div_str="BULLISH DIVERGENCE (potensi reversal naik)" if div.get("bullish") else ("BEARISH DIVERGENCE (potensi reversal turun)" if div.get("bearish") else "tidak ada")

    pos_section=""
    m=position_metrics
    if m:
        pos_section=f"""
POSISI AKTIF USER:
- Masuk: Rp{m['entry']:,.0f} x {m['lots']} lot ({m['lembar']:,} lembar) | Modal: Rp{m['modal']:,.0f}
- Sekarang: Rp{m['current_price']:,.0f} → P&L: {m['pnl_pct']:+.1f}% = Rp{abs(m['pnl_rp']):,.0f} {'PROFIT' if m['pnl_pct']>=0 else 'LOSS'}
- Durasi hold: {m['days_held']} hari
- Support terdekat: {'Rp'+f"{m['ns']:,.0f} ({m['nsd']:.1f}% di bawah harga)" if m['ns'] else 'tidak terdeteksi'}
- STATUS SUPPORT: {'⚠️ SUDAH TEMBUS — BAHAYA!' if m['sup_broken'] else '✅ Masih holding'}"""
    else:
        pos_section="\nPOSISI: User tidak memiliki posisi aktif di saham ini."

    return f"""Kamu adalah AI Trading Assistant pribadi untuk trader saham Indonesia yang berpengalaman. 
Kamu berbicara dengan seorang trader yang menggunakan gaya swing trading + scalping dengan max hold 2 minggu.

═══ DATA TEKNIKAL {ticker} — {datetime.now().strftime('%d %b %Y %H:%M WIB')} ═══
Harga: Rp{price:,.0f} ({vol['pchg']:+.1f}% hari ini) | Volume: {vol['label']} ({vol['ratio']:.1f}x rata-rata)
Smart Signal: {smart_rec['emoji']} {smart_rec['rec']} | Skor Teknikal: {smart_rec['score']:.0f}/100
RSI Daily: {rsi_d['rsi']:.1f} → {rsi_d['label']}
Fase Pasar: {phase['phase']} | Saran fase: {phase['action']}
Confluence 3-TF: {conf['confluence']} ({conf['bull_count']}/3 TF bullish, {conf['bear_count']}/3 bearish)
Divergence RSI: {div_str}
MA20: Rp{trend['ma20']:,.0f} ({'✅ di atas' if price>trend['ma20'] else '❌ di bawah'}) | MA50: {'Rp'+f"{trend['ma50']:,.0f}"+(' ✅' if trend['ma50'] and price>trend['ma50'] else ' ❌') if trend['ma50'] else 'N/A (perlu data lebih panjang)'} | MA200: {'Rp'+f"{trend['ma200']:,.0f}"+(' ✅' if trend['ma200'] and price>trend['ma200'] else ' ❌') if trend['ma200'] else 'N/A'}
Resistance: {res_str}
Support: {sup_str}
Fibonacci: 23.6%=Rp{fib.get('23.6%',0):,.0f} | 38.2%=Rp{fib.get('38.2%',0):,.0f} | 50%=Rp{fib.get('50%',0):,.0f} | 61.8%=Rp{fib.get('61.8%',0):,.0f}
{pos_section}

═══ INSTRUKSI ═══
• Jawab dalam bahasa Indonesia yang natural — seperti teman trader yang jujur
• SELALU gunakan angka konkret dari data di atas (jangan jawaban umum/template)
• Berikan saran yang actionable — tidak hanya analisis
• Jika ada posisi aktif, jadikan itu fokus utama analisis  
• Maksimum 300 kata, to-the-point
• Di akhir: "⚠️ Bukan saran investasi profesional — selalu gunakan judgment sendiri."
• Boleh bertanya balik jika butuh info tambahan (misalnya tujuan investasi, toleransi risiko)
"""


def get_ai_response(api_key, question, position_metrics, analysis_data, chat_history):
    """Get response from Claude AI with full trading context."""
    if not ANTHROPIC_AVAILABLE:
        return "❌ Library 'anthropic' belum terinstal. Jalankan Cell 1 ulang dengan: `!pip install streamlit yfinance plotly pandas numpy anthropic -q`"
    try:
        client = anthropic.Anthropic(api_key=api_key)
        system  = build_ai_context(position_metrics, analysis_data)
        # Format history for Claude (user/assistant roles, max 8 messages)
        messages = []
        for msg in chat_history[-8:]:
            role = "user" if msg["role"] == "user" else "assistant"
            messages.append({"role": role, "content": msg["content"]})
        messages.append({"role": "user", "content": question})
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=700,
            system=system,
            messages=messages,
        )
        return response.content[0].text
    except Exception as e:
        err = str(e)
        if "auth" in err.lower() or "api_key" in err.lower():
            return "❌ API key tidak valid. Pastikan key sudah benar (format: sk-ant-api03-...)."
        elif "credit" in err.lower() or "billing" in err.lower():
            return "❌ Credit Anthropic habis. Tambah credit di console.anthropic.com → Billing."
        else:
            return f"❌ Error: {err}"


def get_fundamental_data(ticker):
    """Ambil data fundamental dari Yahoo Finance."""
    try:
        info = yf.Ticker(ticker).info
        pe   = info.get("trailingPE")
        pb   = info.get("priceToBook")
        roe  = info.get("returnOnEquity")
        der  = info.get("debtToEquity")
        div_y= info.get("dividendYield")
        rev_g= info.get("revenueGrowth")
        earn_g=info.get("earningsGrowth")
        margin=info.get("grossMargins")
        yr52  =info.get("52WeekChange")
        mktcap=info.get("marketCap")
        beta  =info.get("beta")
        return dict(pe=pe,pb=pb,roe=roe,der=der,div_yield=div_y,
                    rev_growth=rev_g,earn_growth=earn_g,margin=margin,
                    yr52=yr52,mktcap=mktcap,beta=beta)
    except:
        return {}


def score_fundamental(fund):
    """Buat skor investasi sederhana dari data fundamental."""
    if not fund: return 50, "DATA KURANG"
    score = 50
    notes = []
    pe=fund.get("pe"); pb=fund.get("pb"); roe=fund.get("roe"); der=fund.get("der")

    if pe:
        if pe < 10:   score += 15; notes.append(f"P/E {pe:.1f}x — sangat murah ✅")
        elif pe < 20: score += 8;  notes.append(f"P/E {pe:.1f}x — wajar ✅")
        elif pe < 35: score -= 5;  notes.append(f"P/E {pe:.1f}x — agak mahal ⚠️")
        else:         score -= 15; notes.append(f"P/E {pe:.1f}x — mahal sekali ❌")

    if pb:
        if pb < 1:    score += 12; notes.append(f"P/BV {pb:.2f}x — di bawah nilai buku, sangat murah ✅")
        elif pb < 2:  score += 6;  notes.append(f"P/BV {pb:.2f}x — wajar ✅")
        elif pb < 4:  score -= 5;  notes.append(f"P/BV {pb:.2f}x — premium ⚠️")
        else:         score -= 10; notes.append(f"P/BV {pb:.2f}x — sangat premium ❌")

    if roe:
        roe_pct = roe * 100
        if roe_pct > 20:  score += 10; notes.append(f"ROE {roe_pct:.1f}% — sangat profitable ✅")
        elif roe_pct > 12: score += 5;  notes.append(f"ROE {roe_pct:.1f}% — cukup baik ✅")
        elif roe_pct > 0:  score -= 3;  notes.append(f"ROE {roe_pct:.1f}% — lemah ⚠️")
        else:              score -= 10; notes.append(f"ROE {roe_pct:.1f}% — negatif! ❌")

    if der:
        if der < 50:   score += 5;  notes.append(f"DER {der:.0f}% — utang rendah ✅")
        elif der < 150: score += 0;  notes.append(f"DER {der:.0f}% — utang sedang")
        elif der < 300: score -= 8;  notes.append(f"DER {der:.0f}% — utang tinggi ⚠️")
        else:           score -= 15; notes.append(f"DER {der:.0f}% — utang sangat tinggi ❌")

    score = max(0, min(100, score))
    if score >= 70:   rating = "LAYAK INVESTASI ✅"
    elif score >= 55: rating = "CUKUP BAIK"
    elif score >= 40: rating = "RATA-RATA"
    else:             rating = "HINDARI ❌"
    return score, rating, notes


def calc_position_metrics(pos,current_price,sr,fib,conf):
    entry=pos["entry_price"];lots=pos["lots"];lembar=lots*100
    modal=entry*lembar;nilai=current_price*lembar;pnl_rp=nilai-modal
    pnl_pct=(current_price/entry-1)*100
    ns=sr.get("nearest_sup");nrd=sr.get("nearest_res_dist");nsd=sr.get("nearest_sup_dist")
    nr=sr.get("nearest_res")
    sup_broken=ns is not None and current_price<ns*0.99
    near_sup=ns is not None and nsd is not None and nsd<3.0
    near_res=nr is not None and nrd is not None and nrd<3.0
    try:
        entry_date=datetime.strptime(pos["entry_date"],"%Y-%m-%d"); days_held=(datetime.now()-entry_date).days
    except: days_held=0
    return dict(entry=entry,lots=lots,lembar=lembar,modal=modal,nilai=nilai,
                pnl_rp=pnl_rp,pnl_pct=pnl_pct,current_price=current_price,
                sup_broken=sup_broken,near_sup=near_sup,near_res=near_res,
                days_held=days_held,ns=ns,nr=nr,nsd=nsd,nrd=nrd)

def get_position_decision(m,signal,bull_count,bear_count,rsi,div,phase_name):
    pnl=m["pnl_pct"];ns=m["ns"];nr=m["nr"];nsd=m["nsd"];nrd=m["nrd"]
    if pnl>=15:
        if m["near_res"] or bear_count>=2: return "💰 TAKE PROFIT PENUH","decision-profit",f"Profit {pnl:.1f}% sudah sangat bagus. {'Harga dekat resistance.' if m['near_res'] else 'Sinyal memburuk.'} Realisir sekarang."
        else: return "💰 TAKE PROFIT SEBAGIAN","decision-profit",f"Profit {pnl:.1f}%. Ambil 50-70%, sisanya trailing stop di Rp{max(m['entry'],m['current_price']*0.97):,.0f}."
    elif pnl>=5:
        if m["near_res"]: return "💰 AMBIL SEBAGIAN PROFIT","decision-profit",f"Profit {pnl:.1f}% dan hanya {nrd:.1f}% dari resistance Rp{nr:,.0f}. Ambil 50%, sisanya naikkan SL ke breakeven."
        elif bull_count>=2: return "✅ HOLD — NAIKKAN SL","decision-hold",f"Profit {pnl:.1f}% dan sinyal masih bullish. Naikkan SL ke Rp{max(m['entry']*1.01,m['current_price']*0.97):,.0f}."
        else: return "⚠️ PERTIMBANGKAN KELUAR","decision-warn",f"Profit {pnl:.1f}% tapi sinyal mulai melemah ({bull_count}/3 TF bullish). Ambil profit."
    elif pnl>=0:
        if bear_count>=2: return "⚠️ KELUAR BREAKEVEN","decision-warn",f"Hampir breakeven ({pnl:.1f}%) tapi {bear_count}/3 TF sudah bearish. Keluar sekarang."
        else: return "📊 HOLD — MONITOR KETAT","decision-hold",f"Breakeven area ({pnl:.1f}%). Pasang SL di Rp{ns*0.985:,.0f if ns else m['entry']*0.95:,.0f}."
    elif pnl>=-5:
        if m["sup_broken"]: return "🚨 PERTIMBANGKAN CUT LOSS","decision-cutloss",f"Loss {abs(pnl):.1f}% DAN support Rp{ns:,.0f} sudah tembus! Ini sinyal serius."
        elif div.get("bullish") and ns and nsd<3: return "🔄 HOLD — ADA SINYAL REVERSAL","decision-avgdown",f"Loss kecil {abs(pnl):.1f}%, bullish divergence aktif, dekat support. Hold dengan SL ketat."
        else: return "📊 HOLD — PASANG SL KETAT","decision-hold",f"Loss kecil {abs(pnl):.1f}%. Hard SL di Rp{ns*0.982:,.0f if ns else m['entry']*0.95:,.0f}."
    elif pnl>=-10:
        if m["sup_broken"]: return "🚨 CUT LOSS — SUPPORT TEMBUS","decision-cutloss",f"Loss {abs(pnl):.1f}% dan support sudah tembus. Ini bukan dip normal. Cut loss sekarang."
        elif div.get("bullish") and rsi<35: return "🔄 TAHAN — KONDISI OVERSOLD","decision-avgdown",f"Loss {abs(pnl):.1f}% tapi RSI {rsi:.0f} sangat oversold + bullish divergence. SL di Rp{ns*0.982:,.0f if ns else m['entry']*0.93:,.0f}."
        else: return "⚠️ EVALUASI — JANGAN AVERAGE DOWN","decision-warn",f"Loss {abs(pnl):.1f}%. Sinyal belum mendukung reversal. Tentukan: kapan kamu akan cut loss?"
    else:
        return "🚨 CUT LOSS SANGAT DISARANKAN","decision-cutloss",f"Loss {abs(pnl):.1f}% sudah cukup dalam. {'Support sudah tembus!' if m['sup_broken'] else 'Support masih holding tipis.'} Pertimbangkan cut loss."

def rule_based_response(question, m, smart_rec, conf, rsi_d, phase, div, sr):
    """Fallback rule-based response jika tidak ada API key."""
    q=question.lower(); pnl=m["pnl_pct"]; price=m["current_price"]; entry=m["entry"]
    ns=m["ns"]; nr=m["nr"]; nsd=m["nsd"]; nrd=m["nrd"]; rsi=rsi_d.get("rsi",50)
    bull_c=conf.get("bull_count",0); bear_c=conf.get("bear_count",0)
    action,dec_css,advice=get_position_decision(m,smart_rec.get("rec",""),bull_c,bear_c,rsi,div,phase.get("phase",""))

    if any(k in q for k in ["cut","stop loss","keluar","rugi"]):
        sup_break="⚠️ Support sudah tembus — ini sinyal cut loss!" if m["sup_broken"] else f"Support Rp{ns:,.0f} masih holding ({nsd:.1f}% di bawah)." if ns else ""
        return f"""**Analisis Cut Loss:**

P&L: {pnl:+.1f}% (Rp{abs(m['pnl_rp']):,.0f} {'loss' if pnl<0 else 'profit'}) | Hold {m['days_held']} hari

{sup_break}
RSI: {rsi:.0f} ({rsi_d.get('label','')}) | Sinyal: {smart_rec.get('rec','?')} ({bull_c}/3 TF bullish)

**Saran: {action}**
{advice}

SL yang disarankan: **Rp{ns*0.982:,.0f if ns else entry*0.95:,.0f}** — jika tembus, exit tanpa nego.

*⚠️ Aktifkan Claude AI dengan memasukkan Anthropic API key di sidebar untuk diskusi yang lebih mendalam.*"""

    elif any(k in q for k in ["average","nambah","tambah","dca"]):
        return f"""**Analisis Average Down:**

P&L saat ini: {pnl:+.1f}% | RSI: {rsi:.0f} | Support: {'Rp'+f"{ns:,.0f} ({nsd:.1f}%)" if ns else 'N/A'}
Bullish divergence: {'✅ Ada' if div.get('bullish') else '❌ Tidak ada'}

{'⚠️ Loss sudah cukup dalam — average down tidak disarankan tanpa konfirmasi reversal.' if pnl<-10 else '💡 Kondisi: '+('mendukung untuk average down kecil.' if ns and nsd<3 and rsi<40 else 'belum ideal untuk average down.')}

Syarat minimum: RSI < 35, dekat support < 3%, bullish divergence, 2+ TF bullish.

*⚠️ Aktifkan Claude AI di sidebar untuk analisis yang lebih detail.*"""

    else:
        ticker_name = smart_rec.get('ticker','').replace('.JK','') if smart_rec.get('ticker') else ''
        return f"""**Review Posisi {ticker_name}:**

Posisi: masuk Rp{entry:,.0f} x {m['lots']} lot → P&L: **{pnl:+.1f}%** (Rp{abs(m['pnl_rp']):,.0f})
Sinyal: {smart_rec.get('emoji','')} {smart_rec.get('rec','?')} | RSI: {rsi:.0f} | Confluence: {bull_c}/3 TF bullish
Support: {'Rp'+f"{ns:,.0f}" if ns else 'N/A'} | Resistance: {'Rp'+f"{nr:,.0f}" if nr else 'N/A'}

**Saran: {action}**
{advice}

*💡 Untuk diskusi AI yang sesungguhnya, masukkan Anthropic API key di sidebar.*"""


# ════════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ════════════════════════════════════════════════════════════════════════════════
defaults=[("result",None),("run_flag",False),("cur_ticker","BBCA.JK"),
          ("screener_results",None),("screen_ticker",None),
          ("portfolio",{}),("chat_history",{}),("api_key","")]
for k,v in defaults:
    if k not in st.session_state: st.session_state[k]=v


# ════════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### ⚙️ Panel Kontrol")
    st.divider()

    # ── API KEY — support Streamlit Cloud Secrets & manual input ──
    st.markdown("**🤖 Claude AI**")

    # Coba ambil dari Streamlit Cloud Secrets (jika di-deploy di cloud)
    _secret_key = ""
    try:
        _secret_key = st.secrets.get("ANTHROPIC_API_KEY", "")
    except Exception:
        pass

    if _secret_key:
        if st.session_state["api_key"] != _secret_key:
            st.session_state["api_key"] = _secret_key
        st.success("🤖 Claude AI aktif (Cloud Secrets)")
        st.caption("API key tersimpan otomatis di Streamlit Cloud.")
    else:
        # Manual input (Google Colab atau belum set secrets)
        api_key_input = st.text_input(
            "Anthropic API Key:",
            value=st.session_state["api_key"],
            type="password",
            placeholder="sk-ant-api03-...",
            help="Dapatkan di console.anthropic.com → API Keys"
        )
        if api_key_input != st.session_state["api_key"]:
            st.session_state["api_key"] = api_key_input
        if st.session_state["api_key"]:
            st.success("🤖 Claude AI aktif!")
        else:
            st.caption("Tanpa API key → menggunakan rule-based.")

    st.divider()
    POPULAR={"BBCA":"BCA","BBRI":"BRI","BMRI":"Mandiri","GOTO":"GoTo","TLKM":"Telkom",
             "ASII":"Astra","ANTM":"Antam","ITMG":"ITM","BREN":"Barito","UNVR":"Unilever"}
    st.markdown("**🔥 Quick Pick:**")
    cols=st.columns(2)
    for i,(code,name) in enumerate(POPULAR.items()):
        if cols[i%2].button(code,key=f"q_{code}",help=name,use_container_width=True):
            st.session_state["cur_ticker"]=code+".JK"; st.session_state["run_flag"]=True
    st.divider()
    raw=st.text_input("🔍 Kode:",value=st.session_state["cur_ticker"]).upper().strip()
    if raw: st.session_state["cur_ticker"]=raw if raw.endswith(".JK") else raw+".JK"
    if st.button("🚀 ANALISIS",use_container_width=True,type="primary"): st.session_state["run_flag"]=True
    st.divider()
    if st.session_state["portfolio"]:
        st.markdown("**💼 Posisi:**")
        for tk,pos in st.session_state["portfolio"].items():
            df_q=fetch_tf(tk,"5d","1d")
            if df_q is not None and len(df_q)>0:
                cur=float(df_q["Close"].iloc[-1]); pnl=(cur/pos["entry_price"]-1)*100
                c_pnl="#4caf50" if pnl>=0 else "#f44336"
                st.markdown(f"<span style='font-size:.9em'><b>{tk.replace('.JK','')}</b> <span style='color:{c_pnl}'>{pnl:+.1f}%</span></span>",unsafe_allow_html=True)
    st.caption("⚠️ Alat bantu edukasi, bukan saran investasi.")


# ════════════════════════════════════════════════════════════════════════════════
# HEADER & TABS
# ════════════════════════════════════════════════════════════════════════════════
ai_status = '<span class="ai-badge">🤖 Claude AI ON</span>' if st.session_state["api_key"] else '<span class="rule-badge">⚙️ Rule-based</span>'
st.markdown(f"""<div style="text-align:center;padding:14px 0 6px">
  <h1 style="color:#e8eaf6;font-size:1.9em;margin:0">📈 IHSG Trading Assistant {ai_status}</h1>
  <p style="color:#9e9e9e;margin:3px 0 0;font-size:.85em">v5.0 · Claude AI · Intraday 5m/15m · Fundamental · 3-Timeframe · Portfolio</p>
</div>""",unsafe_allow_html=True)

tab_analisis,tab_intraday,tab_fundamental,tab_portfolio,tab_screener = st.tabs([
    "🔍 Analisis","⚡ Intraday","💹 Fundamental","💼 Posisi & AI Chat","📊 Screener LQ45"
])


# ════════════════════════════════════════════════════════════════════════════════
# TAB 1 — ANALISIS (Weekly + Daily + 1H)
# ════════════════════════════════════════════════════════════════════════════════
with tab_analisis:
    if st.session_state.get("screen_ticker"):
        st.session_state["cur_ticker"]=st.session_state["screen_ticker"]
        st.session_state["screen_ticker"]=None; st.session_state["run_flag"]=True

    if st.session_state["run_flag"]:
        st.session_state["run_flag"]=False; ticker=st.session_state["cur_ticker"]
        with st.spinner(f"⏳ Mengambil data {ticker}..."):
            df_w=fetch_tf(ticker,"2y","1wk"); df_d=fetch_tf(ticker,"6mo","1d"); df_h=fetch_tf(ticker,"60d","1h")
        if df_d is None or len(df_d)<25: st.error(f"❌ Data {ticker} tidak ditemukan."); st.stop()
        trend=analyze_trend(df_d); rsi_d=analyze_rsi(df_d); vol=analyze_volume(df_d); rec=get_rec(trend,rsi_d,vol)
        sr=find_sr_zones(df_d); div=detect_divergence(df_d,rsi_d["series"]); candles=detect_candle_patterns(df_d)
        phase=detect_market_phase(df_d,trend,rsi_d); smart=apply_smart_override(rec,sr,div,phase,candles)
        w_data=analyze_weekly(df_w); h_data=analyze_hourly(df_h); conf=get_confluence(w_data,rec,h_data)
        fib,fib_sh,fib_sl=calc_fibonacci(df_d); trade_plan=generate_trade_plan(trend["price"],sr,rec,conf)
        macd_l,sig_l,hist_l=calc_macd(df_d["Close"]); bb_u,bb_m,bb_l=calc_bb(df_d["Close"])
        st.session_state["result"]=dict(
            df_d=df_d,df_w=df_w,df_h=df_h,ticker=ticker,trend=trend,rsi_d=rsi_d,vol=vol,rec=rec,
            sr=sr,div=div,candles=candles,phase=phase,smart=smart,w_data=w_data,h_data=h_data,
            conf=conf,fib=fib,fib_sh=fib_sh,fib_sl=fib_sl,trade_plan=trade_plan,
            macd_l=macd_l,sig_l=sig_l,hist_l=hist_l,bb_u=bb_u,bb_m=bb_m,bb_l=bb_l)

    if st.session_state["result"]:
        R=st.session_state["result"]; ticker=R["ticker"]
        trend=R["trend"]; rsi_d=R["rsi_d"]; vol=R["vol"]; rec=R["rec"]
        sr=R["sr"]; div=R["div"]; candles=R["candles"]; phase=R["phase"]; smart=R["smart"]
        w_data=R["w_data"]; h_data=R["h_data"]; conf=R["conf"]
        fib=R["fib"]; trade_plan=R["trade_plan"]
        macd_l=R["macd_l"]; sig_l=R["sig_l"]; hist_l=R["hist_l"]
        bb_u=R["bb_u"]; bb_m=R["bb_m"]; bb_l=R["bb_l"]; smart_rec=smart["smart_rec"]
        has_pos=ticker in st.session_state["portfolio"]

        try:
            info=yf.Ticker(ticker).info; cname=info.get("longName",ticker); sector=info.get("sector","-")
            mktcap=info.get("marketCap"); wk52h=info.get("fiftyTwoWeekHigh"); wk52l=info.get("fiftyTwoWeekLow")
        except: cname,sector,mktcap,wk52h,wk52l=ticker,"-",None,None,None

        ca,cb=st.columns([4,1])
        with ca:
            badge=""
            if has_pos:
                pos_d=st.session_state["portfolio"][ticker]
                m_tmp=calc_position_metrics(pos_d,trend["price"],sr,fib,conf)
                pc="#4caf50" if m_tmp["pnl_pct"]>=0 else "#f44336"
                badge=f' <span style="background:{pc}22;border:1px solid {pc}55;color:{pc};padding:2px 8px;border-radius:10px;font-size:.75em">💼 POSISI {m_tmp["pnl_pct"]:+.1f}%</span>'
            st.markdown(f"### 🏢 {cname}{badge}",unsafe_allow_html=True)
            st.caption(f"**{ticker}** · {sector} · {len(R['df_d'])} bar Daily")
        with cb:
            if mktcap: st.metric("Market Cap",f"Rp{fmt_idr(mktcap)}")

        if has_pos:
            pos_d=st.session_state["portfolio"][ticker]
            m_p=calc_position_metrics(pos_d,trend["price"],sr,fib,conf)
            action,dec_css,advice=get_position_decision(m_p,smart_rec.get("rec",""),conf.get("bull_count",0),conf.get("bear_count",0),rsi_d["rsi"],div,phase.get("phase",""))
            st.markdown(f"""<div class="decision-card {dec_css}">
            <div style="font-size:.85em;color:#9e9e9e;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px">💼 ANALISIS POSISI AKTIF</div>
            <div style="display:flex;gap:16px;flex-wrap:wrap;margin-bottom:8px;font-size:.9em">
              <span>Masuk: <b>Rp{m_p['entry']:,.0f}</b></span>
              <span>Sekarang: <b>Rp{m_p['current_price']:,.0f}</b></span>
              <span>P&L: <b style="color:{'#4caf50' if m_p['pnl_pct']>=0 else '#f44336'}">{m_p['pnl_pct']:+.1f}% (Rp{abs(m_p['pnl_rp']):,.0f})</b></span>
              <span>Hold: <b>{m_p['days_held']} hari</b></span>
            </div>
            <div style="font-weight:700">{action}</div>
            <div style="font-size:.9em;margin-top:4px;opacity:.9">{advice}</div>
            <div style="margin-top:8px;font-size:.8em;color:#9e9e9e">→ Tab <b>💼 Posisi & AI Chat</b> untuk diskusi mendalam dengan Claude AI</div>
            </div>""",unsafe_allow_html=True)
            st.divider()

        # 3-TF
        st.markdown("#### 🕐 Konfluensi 3 Timeframe")
        c1,c2,c3=st.columns(3)
        with c1: st.markdown(f"""<div class="tf-box"><div class="tf-title">📅 WEEKLY — Arah Arus</div><div class="tf-signal" style="color:{w_data['color']}">{w_data['signal']}</div><div class="tf-detail">{w_data['desc']}<br>Perubahan: {w_data.get('wchg',0):+.2f}%</div></div>""",unsafe_allow_html=True)
        with c2:
            rc=smart_rec;sc_col="#4caf50" if rc['rec'] in ["BELI","BELI KUAT"] else "#f44336" if rc['rec'] in ["JUAL","JUAL KUAT"] else "#9e9e9e"
            st.markdown(f"""<div class="tf-box"><div class="tf-title">📊 DAILY — Setup Swing</div><div class="tf-signal" style="color:{sc_col}">{rc['emoji']} {rc['rec']}</div><div class="tf-detail">Skor: {rc['score']:.0f}/100<br>RSI: {rsi_d['rsi']:.0f} · {rsi_d['label']}</div></div>""",unsafe_allow_html=True)
        with c3: st.markdown(f"""<div class="tf-box"><div class="tf-title">⏰ 1-JAM — Entry Scalp</div><div class="tf-signal" style="color:{h_data['color']}">{h_data['signal']}</div><div class="tf-detail">{h_data['desc']}</div></div>""",unsafe_allow_html=True)
        st.markdown(f"""<div class="conf-bar" style="background:rgba(255,255,255,.03);border-color:{conf['color']}30"><span style="color:{conf['color']};font-size:1.1em;font-weight:700">{conf['confluence']}</span><span style="color:#9e9e9e;font-size:.85em;margin-left:12px">— {conf['quality']}</span></div>""",unsafe_allow_html=True)
        st.divider()

        cs,ct=st.columns([1,1]); price=trend["price"]; pchg=vol["pchg"]
        pdir="▲" if pchg>=0 else "▼"; pcol="#4caf50" if pchg>=0 else "#f44336"
        with cs:
            ctag=' <span style="font-size:.55em;background:rgba(255,255,255,.2);padding:1px 6px;border-radius:10px">🧠 OVERRIDE</span>' if smart_rec.get("was_changed") else ""
            st.markdown(f"""<div class="rec-card {smart_rec['css']}"><div class="rec-label">🧠 Smart Signal</div><div class="rec-action">{smart_rec['emoji']} {smart_rec['rec']}{ctag}</div><div class="rec-score">Skor: <b>{smart_rec['score']:.0f}</b>/100</div><div class="rec-desc">{smart_rec['desc']}</div><div class="rec-price">Rp{price:,.0f} <span style="color:{pcol}">{pdir}{abs(pchg):.2f}%</span></div></div>""",unsafe_allow_html=True)
        with ct:
            if trade_plan:
                tp=trade_plan
                if tp["type"]=="BUY":
                    rrc="tp-tp2" if tp["rr1"]>=1.5 else "tp-sl"
                    st.markdown(f"""<div class="tp-card"><div class="tp-title">📋 Auto Trade Plan — BUY</div><div class="tp-row"><span class="tp-lbl">Entry Zone</span><span class="tp-val tp-entry">Rp{tp['entry_low']:,.0f}–Rp{tp['entry_high']:,.0f}</span></div><div class="tp-row"><span class="tp-lbl">Entry Ideal</span><span class="tp-val tp-entry">Rp{tp['entry_mid']:,.0f}</span></div><div class="tp-row"><span class="tp-lbl">Stop Loss</span><span class="tp-val tp-sl">Rp{tp['sl']:,.0f} (-{tp['sl_pct']:.1f}%)</span></div><div class="tp-row"><span class="tp-lbl">Target 1</span><span class="tp-val tp-tp1">Rp{tp['tp1']:,.0f} (+{tp['tp1_pct']:.1f}%)</span></div><div class="tp-row"><span class="tp-lbl">Target 2</span><span class="tp-val tp-tp2">Rp{tp['tp2']:,.0f} (+{tp['tp2_pct']:.1f}%)</span></div><div class="tp-row"><span class="tp-lbl">R:R ke TP1</span><span class="tp-val {rrc}">1:{tp['rr1']:.1f} {'✅' if tp['rr1']>=1.5 else '⚠️'}</span></div><div class="tp-note">💡 Ambil 50% di TP1, trailing sisanya ke TP2.</div></div>""",unsafe_allow_html=True)
                else:
                    st.markdown(f"""<div class="tp-card tp-exit"><div class="tp-title">📋 Trade Plan — EXIT</div><div class="tp-row"><span class="tp-lbl">Exit Target</span><span class="tp-val" style="color:#ff9800">Rp{tp.get('exit_target',0):,.0f}</span></div><div class="tp-note">{tp.get('note','')}</div></div>""",unsafe_allow_html=True)
            else:
                st.info("📋 Trade Plan membutuhkan zona S/R yang jelas di kedua sisi. Gunakan periode 1-2 Tahun.")

        if smart["overrides"]:
            for msg in smart["overrides"]: st.markdown(f'<div class="override-box">⚠️ {msg}</div>',unsafe_allow_html=True)
        if smart["boosts"]:
            for msg in smart["boosts"]: st.markdown(f'<div class="boost-box">{msg}</div>',unsafe_allow_html=True)

        ph=phase
        st.markdown(f"""<div class="phase-card" style="border-color:{ph['color']}"><b style="color:{ph['color']}">📍 Fase: {ph['phase']}</b><br><span style="color:#bbb;font-size:.88em">{ph['desc']}</span><br><span style="font-size:.9em">{ph['action']}</span></div>""",unsafe_allow_html=True)

        cr_col,cs_col=st.columns(2)
        with cr_col:
            st.markdown("**🔴 Resistance**")
            if sr["resistance"]:
                for rv,rd in zip(sr["resistance"],sr["res_dist"]):
                    st.markdown(f'<span class="sr-r">Rp{rv:,.0f} +{rd:.1f}%{"⚠️" if rd<3 else ""}</span>',unsafe_allow_html=True)
        with cs_col:
            st.markdown("**🟢 Support**")
            if sr["support"]:
                for sv,sd in zip(sr["support"],sr["sup_dist"]):
                    st.markdown(f'<span class="sr-s">Rp{sv:,.0f} -{sd:.1f}%{"✅" if sd<3 else ""}</span>',unsafe_allow_html=True)

        st.markdown("**📐 Fibonacci**")
        fib_colors={"0%":"#f44336","23.6%":"#ff9800","38.2%":"#ffb300","50%":"#ffee58","61.8%":"#aed581","78.6%":"#4caf50","100%":"#26a69a"}
        fib_html=""
        for pct,level in fib.items():
            near=abs(level-price)/price<0.02
            border="2px solid white" if near else "1px solid rgba(255,255,255,.15)"
            fib_html+=f'<span class="fib-badge" style="background:{fib_colors.get(pct,"#555")}22;color:{fib_colors.get(pct,"#aaa")};border:{border}">{pct}: Rp{level:,.0f}{"←" if near else ""}</span>'
        st.markdown(fib_html,unsafe_allow_html=True)

        if wk52h and wk52l and wk52h!=wk52l:
            pos52=(price-wk52l)/(wk52h-wk52l)*100
            st.markdown(f"<div style='margin:6px 0;font-size:.88em;color:#9e9e9e'>📏 52W: <span style='color:#f44336'>Rp{wk52l:,.0f}</span> ─── <span style='color:#42a5f5'><b>Rp{price:,.0f}</b> ({pos52:.0f}%)</span> ─── <span style='color:#4caf50'>Rp{wk52h:,.0f}</span></div>",unsafe_allow_html=True)

        st.divider()
        st.markdown("#### 📈 Grafik — 3 Timeframe")
        ct_w,ct_d,ct_h=st.tabs(["📅 Weekly","📊 Daily","⏰ 1-Jam"])

        def add_pos_line(fig,row,pos_entry,has_pos):
            if has_pos and pos_entry:
                fig.add_hline(y=pos_entry,line_dash="solid",line_color="rgba(255,255,255,.7)",line_width=2,row=row,col=1,annotation_text=f"Entry Rp{pos_entry:,.0f}",annotation_font_size=9,annotation_font_color="white")

        pos_entry=st.session_state["portfolio"].get(ticker,{}).get("entry_price") if has_pos else None

        with ct_w:
            df_w=R["df_w"]
            if df_w is not None and len(df_w)>=10:
                cw=df_w["Close"];dw=df_w.index;wma20=cw.rolling(min(20,len(cw))).mean();wma50=cw.rolling(min(50,len(cw))).mean()
                fig_w=make_subplots(rows=2,cols=1,shared_xaxes=True,vertical_spacing=0.04,row_heights=[0.7,0.3],subplot_titles=["Harga Weekly + MA + Fibonacci","RSI Weekly"])
                fig_w.add_trace(go.Candlestick(x=dw,open=df_w["Open"],high=df_w["High"],low=df_w["Low"],close=df_w["Close"],name="W-Harga",increasing_line_color="#26a69a",decreasing_line_color="#ef5350",increasing_fillcolor="#26a69a",decreasing_fillcolor="#ef5350"),row=1,col=1)
                fig_w.add_trace(go.Scatter(x=dw,y=wma20,mode="lines",line=dict(color="#FFA726",width=2),name="WMA20"),row=1,col=1)
                fig_w.add_trace(go.Scatter(x=dw,y=wma50,mode="lines",line=dict(color="#42A5F5",width=2),name="WMA50"),row=1,col=1)
                add_pos_line(fig_w,1,pos_entry,has_pos)
                for pct,level in fib.items():
                    if pct in {"38.2%","50%","61.8%"}:
                        fig_w.add_hline(y=level,line_dash="dot",line_color="rgba(255,238,88,.3)",line_width=1,row=1,col=1,annotation_text=f"Fib {pct}",annotation_font_size=7)
                fig_w.add_trace(go.Scatter(x=dw,y=calc_rsi(cw),mode="lines",line=dict(color="#CE93D8",width=1.5),showlegend=False),row=2,col=1)
                fig_w.add_hrect(y0=70,y1=100,fillcolor="rgba(239,83,80,.1)",line_width=0,row=2,col=1)
                fig_w.add_hrect(y0=0,y1=30,fillcolor="rgba(38,166,154,.1)",line_width=0,row=2,col=1)
                fig_w.add_hline(y=70,line_dash="dash",line_color="rgba(239,83,80,.6)",line_width=1,row=2,col=1)
                fig_w.add_hline(y=30,line_dash="dash",line_color="rgba(38,166,154,.6)",line_width=1,row=2,col=1)
                fig_w.update_layout(height=550,template="plotly_dark",paper_bgcolor="rgba(14,17,23,1)",plot_bgcolor="rgba(14,17,23,1)",xaxis_rangeslider_visible=False,margin=dict(l=0,r=10,t=30,b=0),font=dict(color="#e0e0e0"),legend=dict(orientation="h",y=1.02,xanchor="right",x=1))
                fig_w.update_xaxes(gridcolor="rgba(255,255,255,0.04)"); fig_w.update_yaxes(gridcolor="rgba(255,255,255,0.04)")
                st.plotly_chart(fig_w,use_container_width=True)

        with ct_d:
            close=R["df_d"]["Close"]; dates=R["df_d"].index
            ma20=close.rolling(20).mean(); ma50=close.rolling(50).mean() if len(close)>=50 else None
            ma200=close.rolling(200).mean() if len(close)>=200 else None
            fig_d=make_subplots(rows=4,cols=1,shared_xaxes=True,vertical_spacing=0.03,row_heights=[0.46,0.20,0.17,0.17],subplot_titles=["Harga Daily + MA + S/R + Fibonacci","RSI","Volume","MACD"])
            fig_d.add_trace(go.Candlestick(x=dates,open=R["df_d"]["Open"],high=R["df_d"]["High"],low=R["df_d"]["Low"],close=R["df_d"]["Close"],name="Harga",increasing_line_color="#26a69a",decreasing_line_color="#ef5350",increasing_fillcolor="#26a69a",decreasing_fillcolor="#ef5350"),row=1,col=1)
            fig_d.add_trace(go.Scatter(x=dates,y=bb_u,mode="lines",line=dict(width=0),showlegend=False),row=1,col=1)
            fig_d.add_trace(go.Scatter(x=dates,y=bb_l,mode="lines",line=dict(width=0),fill="tonexty",fillcolor="rgba(120,120,220,0.07)",showlegend=True,name="BB"),row=1,col=1)
            fig_d.add_trace(go.Scatter(x=dates,y=ma20,mode="lines",line=dict(color="#FFA726",width=1.5),name="MA20"),row=1,col=1)
            if ma50 is not None: fig_d.add_trace(go.Scatter(x=dates,y=ma50,mode="lines",line=dict(color="#42A5F5",width=1.8),name="MA50"),row=1,col=1)
            if ma200 is not None: fig_d.add_trace(go.Scatter(x=dates,y=ma200,mode="lines",line=dict(color="#EF5350",width=2,dash="dash"),name="MA200"),row=1,col=1)
            for rv,rd in zip(sr["resistance"][:3],sr["res_dist"][:3]): fig_d.add_hline(y=rv,line_dash="dot",line_color="rgba(244,67,54,.55)",line_width=1.5,row=1,col=1,annotation_text=f"R +{rd:.1f}%",annotation_font_size=8,annotation_font_color="rgba(244,67,54,.8)")
            for sv,sd in zip(sr["support"][:3],sr["sup_dist"][:3]): fig_d.add_hline(y=sv,line_dash="dot",line_color="rgba(76,175,80,.55)",line_width=1.5,row=1,col=1,annotation_text=f"S -{sd:.1f}%",annotation_font_size=8,annotation_font_color="rgba(76,175,80,.8)")
            for pct,level in fib.items():
                if pct in {"38.2%","50%","61.8%"}: fig_d.add_hline(y=level,line_dash="dot",line_color="rgba(255,238,88,.3)",line_width=1,row=1,col=1,annotation_text=f"Fib {pct}",annotation_font_size=7,annotation_position="right")
            add_pos_line(fig_d,1,pos_entry,has_pos)
            fig_d.add_trace(go.Scatter(x=dates,y=rsi_d["series"],mode="lines",line=dict(color="#CE93D8",width=2),showlegend=False),row=2,col=1)
            fig_d.add_hrect(y0=70,y1=100,fillcolor="rgba(239,83,80,.1)",line_width=0,row=2,col=1)
            fig_d.add_hrect(y0=0,y1=30,fillcolor="rgba(38,166,154,.1)",line_width=0,row=2,col=1)
            for yv,lbl,clr in [(70,"OB","rgba(239,83,80,.7)"),(50,"","rgba(200,200,200,.2)"),(30,"OS","rgba(38,166,154,.7)")]: fig_d.add_hline(y=yv,line_dash="dash",line_color=clr,line_width=1,row=2,col=1,annotation_text=lbl,annotation_font_size=8)
            vcol=["#26a69a" if c>=o else "#ef5350" for c,o in zip(R["df_d"]["Close"],R["df_d"]["Open"])]
            fig_d.add_trace(go.Bar(x=dates,y=R["df_d"]["Volume"],marker_color=vcol,showlegend=False,opacity=0.8),row=3,col=1)
            fig_d.add_trace(go.Scatter(x=dates,y=R["df_d"]["Volume"].rolling(20).mean(),mode="lines",line=dict(color="#FFA726",width=1.5,dash="dash"),showlegend=False),row=3,col=1)
            hcol=["#26a69a" if h>=0 else "#ef5350" for h in hist_l]
            fig_d.add_trace(go.Bar(x=dates,y=hist_l,marker_color=hcol,showlegend=False,opacity=0.7),row=4,col=1)
            fig_d.add_trace(go.Scatter(x=dates,y=macd_l,mode="lines",line=dict(color="#42A5F5",width=1.5),showlegend=False),row=4,col=1)
            fig_d.add_trace(go.Scatter(x=dates,y=sig_l,mode="lines",line=dict(color="#EF5350",width=1.5),showlegend=False),row=4,col=1)
            fig_d.update_layout(height=900,template="plotly_dark",paper_bgcolor="rgba(14,17,23,1)",plot_bgcolor="rgba(14,17,23,1)",showlegend=True,legend=dict(orientation="h",y=1.02,xanchor="right",x=1,bgcolor="rgba(30,33,40,.8)"),xaxis_rangeslider_visible=False,margin=dict(l=0,r=80,t=30,b=0),font=dict(color="#e0e0e0"))
            fig_d.update_xaxes(gridcolor="rgba(255,255,255,0.04)"); fig_d.update_yaxes(gridcolor="rgba(255,255,255,0.04)")
            fig_d.update_yaxes(title_text="Harga (Rp)",row=1,col=1); fig_d.update_yaxes(title_text="RSI",row=2,col=1,range=[0,100])
            fig_d.update_yaxes(title_text="Volume",row=3,col=1); fig_d.update_yaxes(title_text="MACD",row=4,col=1)
            st.plotly_chart(fig_d,use_container_width=True)

        with ct_h:
            df_h=R["df_h"]
            if df_h is not None and len(df_h)>=20:
                ch=df_h["Close"];dh=df_h.index;vwap=h_data.get("vwap");vv=h_data.get("vwap_val",0)
                rsi_h=calc_rsi(ch); ma20h=ch.rolling(20).mean()
                fig_h=make_subplots(rows=2,cols=1,shared_xaxes=True,vertical_spacing=0.04,row_heights=[0.65,0.35],subplot_titles=["Harga 1H + VWAP + MA20","RSI 1H"])
                fig_h.add_trace(go.Candlestick(x=dh,open=df_h["Open"],high=df_h["High"],low=df_h["Low"],close=df_h["Close"],name="1H",increasing_line_color="#26a69a",decreasing_line_color="#ef5350",increasing_fillcolor="#26a69a",decreasing_fillcolor="#ef5350"),row=1,col=1)
                fig_h.add_trace(go.Scatter(x=dh,y=ma20h,mode="lines",line=dict(color="#FFA726",width=1.5),name="MA20"),row=1,col=1)
                if vwap is not None: fig_h.add_trace(go.Scatter(x=dh,y=vwap,mode="lines",line=dict(color="#E040FB",width=2.5),name="VWAP"),row=1,col=1)
                for rv,rd in zip(sr["resistance"][:2],sr["res_dist"][:2]): fig_h.add_hline(y=rv,line_dash="dot",line_color="rgba(244,67,54,.4)",line_width=1,row=1,col=1)
                for sv,sd in zip(sr["support"][:2],sr["sup_dist"][:2]): fig_h.add_hline(y=sv,line_dash="dot",line_color="rgba(76,175,80,.4)",line_width=1,row=1,col=1)
                add_pos_line(fig_h,1,pos_entry,has_pos)
                fig_h.add_trace(go.Scatter(x=dh,y=rsi_h,mode="lines",line=dict(color="#CE93D8",width=1.5),showlegend=False),row=2,col=1)
                for yv,clr in [(70,"rgba(239,83,80,.6)"),(50,"rgba(200,200,200,.2)"),(30,"rgba(38,166,154,.6)")]: fig_h.add_hline(y=yv,line_dash="dash",line_color=clr,line_width=1,row=2,col=1)
                fig_h.update_layout(height=600,template="plotly_dark",paper_bgcolor="rgba(14,17,23,1)",plot_bgcolor="rgba(14,17,23,1)",showlegend=True,legend=dict(orientation="h",y=1.02,xanchor="right",x=1,bgcolor="rgba(30,33,40,.8)"),xaxis_rangeslider_visible=False,margin=dict(l=0,r=10,t=30,b=0),font=dict(color="#e0e0e0"))
                fig_h.update_xaxes(gridcolor="rgba(255,255,255,0.04)"); fig_h.update_yaxes(gridcolor="rgba(255,255,255,0.04)")
                fig_h.update_yaxes(title_text="Harga",row=1,col=1); fig_h.update_yaxes(title_text="RSI 1H",row=2,col=1,range=[0,100])
                st.plotly_chart(fig_h,use_container_width=True)
                st.caption("💡 VWAP (ungu) = acuan scalping intraday. Di atas VWAP = bias beli, di bawah = bias jual.")

        st.divider()
        c1,c2=st.columns(2)
        with c1:
            st.markdown("**〰️ RSI Divergence**")
            if div["bullish"]: st.markdown(f'<div class="div-bull">📈 <b>BULLISH DIVERGENCE!</b><br><small>{div["bull_desc"]}</small></div>',unsafe_allow_html=True)
            elif div["bearish"]: st.markdown(f'<div class="div-warn">📉 <b>BEARISH DIVERGENCE!</b><br><small>{div["bear_desc"]}</small></div>',unsafe_allow_html=True)
            else: st.markdown("➡️ Tidak ada divergence RSI signifikan.")
        with c2:
            st.markdown("**🕯️ Pola Candlestick**")
            for e,m_c in candles: st.markdown(f"{e} {m_c}")
    else:
        st.markdown("""<div style="text-align:center;padding:50px 20px"><div style="font-size:4em">📊</div><h3 style="color:#e0e0e0">Pilih saham di panel kiri → 🚀 ANALISIS</h3></div>""",unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# TAB 2 — INTRADAY (5m, 15m) — BARU v5
# ════════════════════════════════════════════════════════════════════════════════
with tab_intraday:
    st.markdown("### ⚡ Analisis Intraday — Scalping & Day Trading")
    st.caption("Data 5m dan 15m dari Yahoo Finance. Optimal untuk trading intraday dan scalping.")

    if not st.session_state["result"]:
        st.info("Pilih saham di tab Analisis dulu, lalu kembali ke sini.")
    else:
        R=st.session_state["result"]; ticker=R["ticker"]; sr=R["sr"]
        has_pos=ticker in st.session_state["portfolio"]
        pos_entry=st.session_state["portfolio"].get(ticker,{}).get("entry_price") if has_pos else None

        tf_choice=st.radio("Pilih Timeframe Intraday:",["15 Menit (Scalp Setup)","5 Menit (Entry Presisi)"],horizontal=True)
        interval="15m" if "15" in tf_choice else "5m"
        period="5d" if "15" in tf_choice else "2d"

        with st.spinner(f"⏳ Mengambil data {interval}..."):
            df_intra=fetch_tf(ticker,period,interval)

        if df_intra is None or len(df_intra)<20:
            st.warning(f"Data {interval} tidak tersedia untuk {ticker}. Yahoo Finance menyediakan data 5m (2 hari) dan 15m (5 hari) terakhir.")
        else:
            ci=df_intra["Close"]; di=df_intra.index
            rsi_i=calc_rsi(ci); vwap_i=calc_vwap(df_intra)
            macd_i,sig_i,hist_i=calc_macd(ci)
            ma9_i=ci.ewm(span=9,adjust=False).mean()
            ma20_i=ci.rolling(20).mean()

            price_now=float(ci.iloc[-1]); vwap_now=float(vwap_i.iloc[-1]); rsi_now=float(rsi_i.iloc[-1])
            above_vwap=price_now>vwap_now; macd_bull=float(macd_i.iloc[-1])>float(sig_i.iloc[-1])
            vwap_pct=(price_now-vwap_now)/vwap_now*100

            # Intraday signal
            bp=sum([rsi_now>50, macd_bull, above_vwap, price_now>float(ma9_i.iloc[-1])])
            if bp>=3: intra_sig,intra_col="BULLISH 📈 — Bias beli intraday","#4caf50"
            elif bp<=1: intra_sig,intra_col="BEARISH 📉 — Bias jual intraday","#f44336"
            else: intra_sig,intra_col="NETRAL ↔️ — Tunggu breakout","#9e9e9e"

            # Summary
            c1,c2,c3,c4=st.columns(4)
            with c1: st.metric(f"Sinyal {interval}",intra_sig[:7],delta=f"{bp}/4 bullish",delta_color="normal" if bp>=3 else "inverse")
            with c2: st.metric("vs VWAP",f"{'Di atas' if above_vwap else 'Di bawah'}",delta=f"{vwap_pct:+.2f}%",delta_color="normal" if above_vwap else "inverse")
            with c3: st.metric("RSI Intraday",f"{rsi_now:.0f}",delta="Bullish" if rsi_now>50 else "Bearish",delta_color="normal" if rsi_now>50 else "inverse")
            with c4: st.metric("MACD","Bullish" if macd_bull else "Bearish",delta_color="normal" if macd_bull else "inverse")

            st.markdown(f"<div style='text-align:center;padding:8px;border-radius:8px;background:rgba(255,255,255,.03);border:1px solid {intra_col}44;margin:8px 0'><b style='color:{intra_col};font-size:1.05em'>{intra_sig}</b> | VWAP: Rp{vwap_now:,.0f} ({vwap_pct:+.2f}%)</div>",unsafe_allow_html=True)

            # Chart
            fig_i=make_subplots(rows=3,cols=1,shared_xaxes=True,vertical_spacing=0.03,row_heights=[0.55,0.25,0.20],subplot_titles=[f"Harga {interval} + VWAP + MA9/MA20","RSI","MACD"])
            fig_i.add_trace(go.Candlestick(x=di,open=df_intra["Open"],high=df_intra["High"],low=df_intra["Low"],close=df_intra["Close"],name=f"{interval} Harga",increasing_line_color="#26a69a",decreasing_line_color="#ef5350",increasing_fillcolor="#26a69a",decreasing_fillcolor="#ef5350"),row=1,col=1)
            fig_i.add_trace(go.Scatter(x=di,y=vwap_i,mode="lines",line=dict(color="#E040FB",width=2.5),name="VWAP"),row=1,col=1)
            fig_i.add_trace(go.Scatter(x=di,y=ma9_i,mode="lines",line=dict(color="#FFA726",width=1.5),name="EMA9"),row=1,col=1)
            fig_i.add_trace(go.Scatter(x=di,y=ma20_i,mode="lines",line=dict(color="#42A5F5",width=1.5),name="MA20"),row=1,col=1)
            for rv,rd in zip(sr["resistance"][:2],sr["res_dist"][:2]): fig_i.add_hline(y=rv,line_dash="dot",line_color="rgba(244,67,54,.5)",line_width=1.5,row=1,col=1,annotation_text=f"R +{rd:.1f}%",annotation_font_size=8)
            for sv,sd in zip(sr["support"][:2],sr["sup_dist"][:2]): fig_i.add_hline(y=sv,line_dash="dot",line_color="rgba(76,175,80,.5)",line_width=1.5,row=1,col=1,annotation_text=f"S -{sd:.1f}%",annotation_font_size=8)
            if has_pos and pos_entry: fig_i.add_hline(y=pos_entry,line_dash="solid",line_color="rgba(255,255,255,.7)",line_width=2,row=1,col=1,annotation_text=f"Entry Rp{pos_entry:,.0f}",annotation_font_size=9)
            fig_i.add_trace(go.Scatter(x=di,y=rsi_i,mode="lines",line=dict(color="#CE93D8",width=1.5),showlegend=False),row=2,col=1)
            fig_i.add_hrect(y0=70,y1=100,fillcolor="rgba(239,83,80,.1)",line_width=0,row=2,col=1)
            fig_i.add_hrect(y0=0,y1=30,fillcolor="rgba(38,166,154,.1)",line_width=0,row=2,col=1)
            for yv,clr in [(70,"rgba(239,83,80,.6)"),(50,"rgba(200,200,200,.2)"),(30,"rgba(38,166,154,.6)")]: fig_i.add_hline(y=yv,line_dash="dash",line_color=clr,line_width=1,row=2,col=1)
            hcol_i=["#26a69a" if h>=0 else "#ef5350" for h in hist_i]
            fig_i.add_trace(go.Bar(x=di,y=hist_i,marker_color=hcol_i,showlegend=False,opacity=0.7),row=3,col=1)
            fig_i.add_trace(go.Scatter(x=di,y=macd_i,mode="lines",line=dict(color="#42A5F5",width=1.5),showlegend=False),row=3,col=1)
            fig_i.add_trace(go.Scatter(x=di,y=sig_i,mode="lines",line=dict(color="#EF5350",width=1.5),showlegend=False),row=3,col=1)
            fig_i.update_layout(height=700,template="plotly_dark",paper_bgcolor="rgba(14,17,23,1)",plot_bgcolor="rgba(14,17,23,1)",showlegend=True,legend=dict(orientation="h",y=1.02,xanchor="right",x=1,bgcolor="rgba(30,33,40,.8)"),xaxis_rangeslider_visible=False,margin=dict(l=0,r=80,t=30,b=0),font=dict(color="#e0e0e0"))
            fig_i.update_xaxes(gridcolor="rgba(255,255,255,0.04)"); fig_i.update_yaxes(gridcolor="rgba(255,255,255,0.04)")
            st.plotly_chart(fig_i,use_container_width=True)

            st.markdown("""**💡 Panduan Scalping dengan VWAP:**
- **Di atas VWAP** = bias intraday bullish → cari setup beli saat harga pullback ke VWAP
- **Di bawah VWAP** = bias intraday bearish → hindari beli, atau wait and see
- **EMA9 memotong MA20 ke atas** = momentum intraday positif → bisa masuk
- **RSI intraday > 70** = overbought jangka pendek → jangan beli baru
- **MACD histogram berbalik** = early warning perubahan arah intraday""")


# ════════════════════════════════════════════════════════════════════════════════
# TAB 3 — FUNDAMENTAL — BARU v5
# ════════════════════════════════════════════════════════════════════════════════
with tab_fundamental:
    st.markdown("### 💹 Analisis Fundamental — Untuk Keputusan Investasi")
    st.caption("Data dari Yahoo Finance. Cocok untuk swing trading jangka panjang dan investasi.")

    if not st.session_state["result"]:
        st.info("Pilih saham di tab Analisis dulu.")
    else:
        R=st.session_state["result"]; ticker=R["ticker"]
        try: cname=yf.Ticker(ticker).info.get("longName",ticker)
        except: cname=ticker

        with st.spinner("⏳ Mengambil data fundamental..."):
            fund=get_fundamental_data(ticker)

        if not fund or all(v is None for v in fund.values()):
            st.warning("Data fundamental tidak tersedia untuk saham ini. Yahoo Finance mungkin belum memiliki data lengkap.")
        else:
            try: fund_score,fund_rating,fund_notes=score_fundamental(fund)
            except: fund_score,fund_rating,fund_notes=50,"N/A",[]

            # Score card
            fc_col="#4caf50" if fund_score>=65 else "#f44336" if fund_score<45 else "#ff9800"
            st.markdown(f"""<div style="border-radius:12px;padding:16px;background:{fc_col}22;border:1px solid {fc_col}44;margin:8px 0">
            <div style="font-size:.85em;color:#9e9e9e;font-weight:700;letter-spacing:1px;text-transform:uppercase">💹 Skor Investasi</div>
            <div style="font-size:2em;font-weight:900;color:{fc_col}">{fund_score}/100 — {fund_rating}</div>
            <div style="font-size:.9em;margin-top:6px;color:#bbb">Berdasarkan P/E, P/BV, ROE, DER dari Yahoo Finance</div>
            </div>""",unsafe_allow_html=True)

            # Metrics grid
            st.markdown("#### 📊 Metrik Fundamental Kunci")
            m1,m2,m3,m4=st.columns(4)
            with m1:
                pe=fund.get("pe")
                if pe: st.metric("P/E Ratio",f"{pe:.1f}x",delta="Murah" if pe<15 else ("Mahal" if pe>30 else "Wajar"),delta_color="normal" if pe<15 else ("inverse" if pe>30 else "off"))
                else: st.metric("P/E Ratio","N/A")
            with m2:
                pb=fund.get("pb")
                if pb: st.metric("P/BV Ratio",f"{pb:.2f}x",delta="Di bawah nilai buku!" if pb<1 else ("Premium" if pb>3 else "Wajar"),delta_color="normal" if pb<1 else ("inverse" if pb>3 else "off"))
                else: st.metric("P/BV Ratio","N/A")
            with m3:
                roe=fund.get("roe")
                if roe: st.metric("ROE",f"{roe*100:.1f}%",delta="Sangat bagus" if roe>0.2 else ("Lemah" if roe<0.08 else "Cukup"),delta_color="normal" if roe>0.15 else ("inverse" if roe<0.08 else "off"))
                else: st.metric("ROE","N/A")
            with m4:
                der=fund.get("der")
                if der: st.metric("DER",f"{der:.0f}%",delta="Utang rendah" if der<80 else ("Utang tinggi" if der>200 else "Sedang"),delta_color="normal" if der<80 else ("inverse" if der>200 else "off"))
                else: st.metric("DER","N/A")

            m5,m6,m7,m8=st.columns(4)
            with m5:
                dy=fund.get("div_yield")
                if dy: st.metric("Dividend Yield",f"{dy*100:.2f}%",delta="Bagus" if dy>0.03 else "Rendah",delta_color="normal" if dy>0.03 else "off")
                else: st.metric("Dividend Yield","0% / N/A")
            with m6:
                rg=fund.get("rev_growth")
                if rg: st.metric("Revenue Growth",f"{rg*100:+.1f}%",delta_color="normal" if rg>0 else "inverse")
                else: st.metric("Revenue Growth","N/A")
            with m7:
                eg=fund.get("earn_growth")
                if eg: st.metric("Earnings Growth",f"{eg*100:+.1f}%",delta_color="normal" if eg>0 else "inverse")
                else: st.metric("Earnings Growth","N/A")
            with m8:
                yr52=fund.get("yr52")
                if yr52: st.metric("Return 1 Tahun",f"{yr52*100:+.1f}%",delta_color="normal" if yr52>0 else "inverse")
                else: st.metric("Return 1 Tahun","N/A")

            st.divider()

            # Detail notes
            st.markdown("#### 📋 Analisis Detail")
            for note in fund_notes:
                if "✅" in note: st.markdown(f'<div class="boost-box">{note}</div>',unsafe_allow_html=True)
                elif "❌" in note: st.markdown(f'<div class="override-box">{note}</div>',unsafe_allow_html=True)
                else: st.markdown(f"- {note}")

            st.divider()
            st.markdown("""#### 💡 Cara Baca untuk Investor
| Metrik | Bagus | Wajar | Mahal/Berbahaya |
|---|---|---|---|
| P/E | < 12× | 12–25× | > 35× |
| P/BV | < 1× | 1–3× | > 5× |
| ROE | > 20% | 10–20% | < 8% |
| DER | < 80% | 80–200% | > 300% |
| Dividend Yield | > 4% | 2–4% | 0% |

*Data fundamental Yahoo Finance mungkin tidak selalu akurat untuk saham IDX. Selalu cross-check dengan laporan keuangan resmi di IDX.co.id atau siakap.ojk.go.id.*""")


# ════════════════════════════════════════════════════════════════════════════════
# TAB 4 — POSISI & AI CHAT
# ════════════════════════════════════════════════════════════════════════════════
with tab_portfolio:
    api_key=st.session_state.get("api_key","")
    ai_on=bool(api_key)

    st.markdown(f"### 💼 Posisi & {'🤖 Claude AI Chat' if ai_on else '⚙️ Analisis Rule-based'}")
    if ai_on:
        st.success("🤖 Claude AI aktif — diskusi dijawab oleh AI sungguhan dengan konteks penuh.")
    else:
        st.info("💡 Masukkan Anthropic API key di sidebar untuk mengaktifkan Claude AI. Tanpa key, menggunakan analisis rule-based.")

    with st.expander("➕ Tambah / Edit Posisi",expanded=not bool(st.session_state["portfolio"])):
        with st.form("add_pos"):
            fc1,fc2=st.columns(2)
            with fc1:
                f_ticker=st.text_input("Kode Saham:",placeholder="Contoh: ANTM").upper().strip()
                f_entry=st.number_input("Harga Masuk (Rp):",min_value=1,max_value=100000,value=3200,step=10)
                f_lots=st.number_input("Jumlah Lot:",min_value=1,max_value=10000,value=10)
            with fc2:
                f_date=st.date_input("Tanggal Masuk:",value=date.today())
                f_sl=st.number_input("Stop Loss (Rp, 0 jika belum):",min_value=0,max_value=100000,value=0,step=10)
                f_notes=st.text_area("Catatan/Tesis:",placeholder="Beli di support, target 3500",height=80)
            if st.form_submit_button("💾 Simpan",use_container_width=True,type="primary") and f_ticker:
                tk=f_ticker+".JK" if not f_ticker.endswith(".JK") else f_ticker
                st.session_state["portfolio"][tk]=dict(ticker=tk,entry_price=float(f_entry),lots=int(f_lots),entry_date=str(f_date),sl_price=float(f_sl) if f_sl>0 else None,notes=f_notes)
                if tk not in st.session_state["chat_history"]: st.session_state["chat_history"][tk]=[]
                st.success(f"✅ Posisi {f_ticker} disimpan!"); st.rerun()

    if not st.session_state["portfolio"]:
        st.info("Belum ada posisi. Tambah menggunakan form di atas.")
    else:
        pos_keys=list(st.session_state["portfolio"].keys())
        sel_ticker=st.selectbox("Pilih posisi:",pos_keys,format_func=lambda x:x.replace(".JK",""))
        pos=st.session_state["portfolio"][sel_ticker]

        with st.spinner(f"Mengambil data {sel_ticker}..."):
            df_pos=fetch_tf(sel_ticker,"6mo","1d")

        if df_pos is None: st.error(f"❌ Tidak bisa ambil data {sel_ticker}.")
        else:
            trend_p=analyze_trend(df_pos); rsi_p=analyze_rsi(df_pos); vol_p=analyze_volume(df_pos)
            rec_p=get_rec(trend_p,rsi_p,vol_p); sr_p=find_sr_zones(df_pos)
            div_p=detect_divergence(df_pos,rsi_p["series"]); candles_p=detect_candle_patterns(df_pos)
            phase_p=detect_market_phase(df_pos,trend_p,rsi_p); smart_p=apply_smart_override(rec_p,sr_p,div_p,phase_p,candles_p)
            df_w_p=fetch_tf(sel_ticker,"2y","1wk"); df_h_p=fetch_tf(sel_ticker,"60d","1h")
            w_p=analyze_weekly(df_w_p); h_p=analyze_hourly(df_h_p); conf_p=get_confluence(w_p,rec_p,h_p)
            fib_p,_,_=calc_fibonacci(df_pos); smart_rec_p=smart_p["smart_rec"]

            m=calc_position_metrics(pos,trend_p["price"],sr_p,fib_p,conf_p)
            action,dec_css,advice=get_position_decision(m,smart_rec_p.get("rec",""),conf_p.get("bull_count",0),conf_p.get("bear_count",0),rsi_p["rsi"],div_p,phase_p.get("phase",""))

            # Position card
            pnl_border="pos-profit" if m["pnl_pct"]>=0 else ("pos-loss" if m["pnl_pct"]<-3 else "pos-even")
            pnl_c="#4caf50" if m["pnl_pct"]>=0 else "#f44336"
            st.markdown(f"""<div class="pos-card {pnl_border}">
            <b style="font-size:1.05em">{sel_ticker.replace('.JK','')} — {pos.get('notes','') or 'Posisi Aktif'}</b>
            <div style="display:flex;gap:20px;flex-wrap:wrap;margin:8px 0;font-size:.9em">
              <span>Masuk: <b>Rp{m['entry']:,.0f}</b></span>
              <span>Sekarang: <b>Rp{m['current_price']:,.0f}</b></span>
              <span>P&L: <b style="color:{pnl_c};font-size:1.1em">{m['pnl_pct']:+.1f}%</b></span>
              <span>Rp: <b style="color:{pnl_c}">Rp{abs(m['pnl_rp']):,.0f}</b></span>
              <span>Modal: <b>Rp{m['modal']:,.0f}</b></span>
              <span>Lot: <b>{m['lots']} ({m['lembar']:,} lbr)</b></span>
              <span>Hold: <b>{m['days_held']} hari</b></span>
            </div>
            </div>""",unsafe_allow_html=True)

            st.markdown(f"""<div class="decision-card {dec_css}">
            <div style="font-size:.85em;color:#9e9e9e;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px">🎯 Keputusan</div>
            <div style="font-size:1.1em;font-weight:700">{action}</div>
            <div style="font-size:.9em;margin-top:5px;opacity:.9">{advice}</div>
            </div>""",unsafe_allow_html=True)

            c1,c2,c3,c4=st.columns(4)
            with c1: st.metric("Support",f"Rp{m['ns']:,.0f}" if m['ns'] else "N/A",delta=f"-{m['nsd']:.1f}%" if m['nsd'] else None,delta_color="off")
            with c2: st.metric("Resistance",f"Rp{m['nr']:,.0f}" if m['nr'] else "N/A",delta=f"+{m['nrd']:.1f}%" if m['nrd'] else None,delta_color="off")
            with c3: st.metric("RSI",f"{rsi_p['rsi']:.0f}",delta=rsi_p['label'],delta_color="normal" if rsi_p['rsi']<65 else "inverse")
            with c4: st.metric("Confluence",f"{conf_p['bull_count']}/3 Bullish",delta=conf_p['quality'],delta_color="normal" if conf_p['bull_count']>=2 else "inverse")

            st.divider()

            # CHAT
            ai_label="🤖 Claude AI" if ai_on else "⚙️ Rule-based"
            st.markdown(f"#### {ai_label} Chat — Diskusi Tentang Posisimu")
            if not ai_on:
                st.caption("⬆️ Masukkan API key di sidebar untuk mengaktifkan Claude AI yang jauh lebih pintar.")

            # Preset questions
            st.markdown("**Pertanyaan cepat:**")
            q_presets=["Review posisi saya secara lengkap","Apakah sebaiknya cut loss?",
                       "Apakah bisa average down?","Kapan sebaiknya take profit?",
                       "Haruskah saya hold lebih lama?","Berapa target harga realistis?",
                       "Apa yang perlu saya pantau selanjutnya?","Berapa risiko jika saya hold 1 minggu lagi?"]
            pq_cols=st.columns(4)
            preset_q=None
            for i,q in enumerate(q_presets):
                if pq_cols[i%4].button(q,key=f"pq_{i}",use_container_width=True,help=q):
                    preset_q=q

            user_input=st.chat_input(f"Tanya tentang posisi {sel_ticker.replace('.JK','')} kamu...")
            question=preset_q or user_input

            if question:
                if sel_ticker not in st.session_state["chat_history"]: st.session_state["chat_history"][sel_ticker]=[]
                analysis_data=dict(ticker=sel_ticker,trend=trend_p,rsi_d=rsi_p,vol=vol_p,rec=rec_p,sr=sr_p,div=div_p,phase=phase_p,conf=conf_p,smart=smart_p,fib=fib_p)
                history=st.session_state["chat_history"][sel_ticker]

                if ai_on:
                    with st.spinner("🤖 Claude AI sedang berpikir..."):
                        response=get_ai_response(api_key,question,m,analysis_data,history)
                else:
                    response=rule_based_response(question,m,smart_rec_p,conf_p,rsi_p,phase_p,div_p,sr_p)

                st.session_state["chat_history"][sel_ticker].append({"role":"user","content":question})
                st.session_state["chat_history"][sel_ticker].append({"role":"ai","content":response})

            # Display chat
            history=st.session_state["chat_history"].get(sel_ticker,[])
            if history:
                st.markdown("**Riwayat Diskusi:**")
                for msg in history[-12:]:
                    if msg["role"]=="user":
                        st.markdown(f"""<div style="background:rgba(66,165,245,.1);border-radius:10px 10px 0 10px;padding:10px 14px;margin:6px 0;font-size:.9em;text-align:right">👤 {msg['content']}</div>""",unsafe_allow_html=True)
                    else:
                        role_icon="🤖" if ai_on else "⚙️"
                        st.markdown(f"""<div style="background:rgba(255,255,255,.05);border-radius:10px 10px 10px 0;padding:12px 14px;margin:6px 0;font-size:.9em">{role_icon} {msg['content']}</div>""",unsafe_allow_html=True)
                if st.button("🗑️ Hapus Riwayat Chat",key="clr_chat"): st.session_state["chat_history"][sel_ticker]=[]; st.rerun()
            else:
                st.info("Klik pertanyaan cepat di atas untuk mulai diskusi.")

            st.divider()
            c_rem,c_go=st.columns(2)
            with c_rem:
                if st.button(f"🗑️ Hapus Posisi {sel_ticker.replace('.JK','')}"): del st.session_state["portfolio"][sel_ticker]; st.rerun()
            with c_go:
                if st.button(f"🔍 Analisis Mendalam {sel_ticker.replace('.JK','')} →",type="primary"):
                    st.session_state["cur_ticker"]=sel_ticker; st.session_state["run_flag"]=True; st.rerun()


# ════════════════════════════════════════════════════════════════════════════════
# TAB 5 — SCREENER LQ45
# ════════════════════════════════════════════════════════════════════════════════
with tab_screener:
    st.markdown("### 📊 LQ45 Screener")
    c_s,c_i=st.columns([1,2])
    with c_s:
        scan_btn=st.button("🔍 SCAN SEMUA LQ45",use_container_width=True,type="primary")
        st.caption("⏱️ ~30-60 detik")
    with c_i:
        st.info("Scan 45 saham paling likuid IHSG → ranking otomatis berdasarkan kekuatan sinyal.")
    if scan_btn:
        st.session_state["screener_results"]=None; results=[]
        prog=st.progress(0); stat=st.empty()
        for i,code in enumerate(LQ45):
            stat.markdown(f"⏳ **{code}**... ({i+1}/{len(LQ45)})")
            prog.progress((i+1)/len(LQ45)); r=quick_screen(code+".JK")
            if r: results.append(r)
        prog.empty(); stat.empty()
        st.session_state["screener_results"]=sorted(results,key=lambda x:x["score"],reverse=True)
        st.success(f"✅ {len(results)} saham dianalisis.")
    if st.session_state["screener_results"]:
        results=st.session_state["screener_results"]
        top3=[r for r in results if "BELI" in r["signal"]][:3]
        if top3:
            st.markdown("**🏆 Top 3 Peluang Beli:**")
            for col,r in zip(st.columns(3),top3):
                with col:
                    st.markdown(f"""<div style="background:rgba(76,175,80,.1);border:1px solid rgba(76,175,80,.3);border-radius:8px;padding:10px;text-align:center"><b style="color:#4caf50;font-size:1.1em">{r['ticker']}</b><br><span style="font-size:.85em;color:#9e9e9e">Rp{r['price']:,.0f} ({r['chg']:+.1f}%)</span><br><b>Skor: {r['score']}/100</b><br><small>{r['phase']}</small></div>""",unsafe_allow_html=True)
                    if st.button(f"→ Analisis",key=f"tp_{r['ticker']}",use_container_width=True):
                        st.session_state["screen_ticker"]=r["ticker"]+".JK"; st.rerun()
        st.divider()
        fc,fs=st.columns([1,2])
        with fc: fsig=st.selectbox("Filter:",["Semua","🟢 BELI","🟡 TAHAN","🔴 JUAL"])
        with fs: msc=st.slider("Skor Min:",0,100,0)
        filtered=[r for r in results if (fsig=="Semua" or fsig.split()[-1] in r["signal"]) and r["score"]>=msc]
        for r in filtered:
            cc="#4caf50" if r["chg"]>=0 else "#f44336"; ic="▲" if r["chg"]>=0 else "▼"
            in_p=" 💼" if r["ticker"]+".JK" in st.session_state["portfolio"] else ""
            ct,cp,cch,cs,crsi,cph,cv,cb=st.columns([1.2,1.5,1,1,1,1.5,1,1.5])
            with ct: st.markdown(f"**{r['ticker']}**{in_p}")
            with cp: st.markdown(f"Rp{r['price']:,.0f}")
            with cch: st.markdown(f"<span style='color:{cc}'>{ic}{abs(r['chg']):.1f}%</span>",unsafe_allow_html=True)
            with cs: st.markdown(f"**{r['score']}**/100")
            with crsi: st.markdown(f"RSI {r['rsi']:.0f}")
            with cph: st.markdown(f"<small>{r['phase']}</small>",unsafe_allow_html=True)
            with cv: st.markdown(f"Vol {r['vol_ratio']}×")
            with cb:
                if st.button(f"→ Analisis",key=f"scr_{r['ticker']}",use_container_width=True):
                    st.session_state["screen_ticker"]=r["ticker"]+".JK"; st.rerun()
