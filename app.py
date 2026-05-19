from flask import Flask, render_template, request, jsonify
import random
import math
import uuid
import copy

app = Flask(__name__, template_folder='templates')
app.secret_key = 'startup-game-secret'

# ==================== DỮ LIỆU CỐ ĐỊNH ====================
SCENARIOS = [
    {"id":1,"name":"Market Liquidity Improves","cat":"Market","delta":{"price":0.03,"cogs":0,"hype":10,"sentiment":8,"transparency":0,"reg_risk":0}},
    {"id":2,"name":"Investor Risk Appetite Rises","cat":"Market","delta":{"price":0.08,"cogs":-0.02,"hype":22,"sentiment":15,"transparency":0,"reg_risk":0}},
    {"id":3,"name":"Capital Moves to Safer Assets","cat":"Market","delta":{"price":-0.05,"cogs":0.02,"hype":-12,"sentiment":-8,"transparency":0,"reg_risk":0}},
    {"id":4,"name":"Interest Rates Increase","cat":"Market","delta":{"price":-0.08,"cogs":0.04,"hype":-18,"sentiment":-15,"transparency":-3,"reg_risk":3}},
    {"id":5,"name":"Startup Funding Market Slows Down","cat":"Market","delta":{"price":-0.15,"cogs":0.05,"hype":-30,"sentiment":-25,"transparency":-8,"reg_risk":8}},
    {"id":6,"name":"Capital Market Liquidity Crisis","cat":"Market","delta":{"price":-0.25,"cogs":0.1,"hype":-40,"sentiment":-35,"transparency":-15,"reg_risk":15}},
    {"id":7,"name":"Operating Costs Exceed the Budget","cat":"Internal","delta":{"cogs":0.05,"hype":-5,"transparency":-5,"trust_all":-5,"runway":-1}},
    {"id":8,"name":"Product Quality Issues Appear","cat":"Internal","delta":{"cogs":0.1,"hype":-10,"transparency":-10,"trust_all":-10,"runway":-2}},
    {"id":9,"name":"Data leak","cat":"Internal","delta":{"cogs":0,"hype":-15,"transparency":-20,"trust_all":-15,"runway":0}},
    {"id":10,"name":"Key Team Member Leaves","cat":"Internal","delta":{"cogs":0.03,"hype":-10,"transparency":-5,"trust_all":-5,"runway":0}},
    {"id":11,"name":"Important Business Milestone Achieved","cat":"Internal","delta":{"cogs":-0.05,"hype":15,"transparency":10,"trust_all":10,"runway":0}},
    {"id":12,"name":"Internal Control Improves","cat":"Internal","delta":{"cogs":0,"hype":5,"transparency":15,"trust_all":10,"runway":0}},
    {"id":13,"name":"Competitor Cuts Prices","cat":"External","delta":{"price":-0.05,"marketing_eff":-0.1,"hype":-5,"transparency":0}},
    {"id":14,"name":"Competitor Launches a Better Product","cat":"External","delta":{"price":-0.1,"marketing_eff":-0.2,"hype":-15,"transparency":-5}},
    {"id":15,"name":"Strategic Partnership Announced","cat":"External","delta":{"price":0.05,"marketing_eff":0.15,"hype":15,"transparency":5}},
    {"id":16,"name":"Intellectual Property Dispute","cat":"External","delta":{"price":-0.08,"marketing_eff":-0.15,"hype":-20,"transparency":-10}},
    {"id":17,"name":"Industry Recognition Received","cat":"External","delta":{"price":0.1,"marketing_eff":0.1,"hype":10,"transparency":5}},
    {"id":18,"name":"Rumor of Interest from a Major Investor","cat":"External","delta":{"price":0.15,"marketing_eff":0.05,"hype":25,"transparency":-5}},
    {"id":19,"name":"Regulator Requests Additional Documents","cat":"Regulatory","delta":{"reg_risk":25,"transparency":-10,"trust_all":-10,"legal_cost_percent":5}},
    {"id":20,"name":"The company is approved for regulatory Sandbox testing","cat":"Regulatory","delta":{"reg_risk":-30,"transparency":15,"trust_all":15,"legal_cost_percent":-3}},
    {"id":21,"name":"New Policy Supports Financial Innovation","cat":"Regulatory","delta":{"reg_risk":-15,"transparency":5,"trust_all":5,"legal_cost_percent":0}},
    {"id":22,"name":"New Regulation Tightens Fundraising Rules","cat":"Regulatory","delta":{"reg_risk":25,"transparency":-10,"trust_all":-10,"legal_cost_percent":5}},
    {"id":23,"name":"Tax and Reporting Review","cat":"Regulatory","delta":{"reg_risk":10,"transparency":-5,"trust_all":-5,"legal_cost_percent":2}},
    {"id":24,"name":"Independent Compliance Certification","cat":"Regulatory","delta":{"reg_risk":-10,"transparency":10,"trust_all":10,"legal_cost_percent":-2}},
]

ACTIVE_CARDS_FULL = [
    {"id":"A1","name":"Marketing Blitz","cost":2,"type":"hotpink","desc":"Tăng Hype 25, giảm Transparency 5","effect":{"hype":25,"transparency":-5,"cost_percent":3}},
    {"id":"A2","name":"Viral Campaign","cost":3,"type":"hotpink","desc":"Tăng Hype 40, giảm Transparency 10","effect":{"hype":40,"transparency":-10,"cost_percent":5}},
    {"id":"A3","name":"Flash Sale","cost":2,"type":"hotpink","desc":"Giảm giá 15%, tăng Hype 15","effect":{"price_percent":-15,"hype":15}},
    {"id":"A4","name":"Influencer Deal","cost":2,"type":"hotpink","desc":"Tăng Hype 20, Visibility 15","effect":{"hype":20,"visibility":15,"cost_percent":2}},
    {"id":"A5","name":"Free Trial","cost":3,"type":"hotpink","desc":"Tăng Hype 30, Utility 5","effect":{"hype":30,"utility":5,"cost_percent":4}},
    {"id":"A6","name":"FOMO Campaign","cost":2,"type":"hotpink","desc":"Tăng Hype 20, Funding 5%","effect":{"hype":20,"funding_boost_percent":5}},
    {"id":"A7","name":"Celebrity Endorsement","cost":2,"type":"hotpink","desc":"Tăng Hype 25, giảm Transparency 3","effect":{"hype":25,"transparency":-3,"cost_percent":4}},
    {"id":"A8","name":"Loyalty Program","cost":3,"type":"hotpink","desc":"Tăng Hype 15, Utility 10, Transparency 5","effect":{"hype":15,"utility":10,"transparency":5}},
    {"id":"A9","name":"Limited Offer","cost":1,"type":"hotpink","desc":"Tăng Hype 10, Visibility 5","effect":{"hype":10,"visibility":5}},
    {"id":"A10","name":"Shill Army","cost":2,"type":"hotpink","desc":"Tăng Hype 30, giảm Transparency 15","effect":{"hype":30,"transparency":-15,"cost_percent":2}},
    {"id":"A11","name":"Pre-sale Discount","cost":2,"type":"hotpink","desc":"Giảm giá 10%, tăng Funding 10%","effect":{"price_percent":-10,"funding_boost_percent":10}},
    {"id":"A12","name":"Media Blast","cost":2,"type":"hotpink","desc":"Tăng Hype 20, Visibility 10","effect":{"hype":20,"visibility":10,"cost_percent":1}},
    {"id":"A13","name":"Meme Marketing","cost":1,"type":"hotpink","desc":"Tăng Hype 15, giảm Transparency 2","effect":{"hype":15,"transparency":-2}},
    {"id":"A14","name":"Aggressive Pricing","cost":2,"type":"hotpink","desc":"Giảm giá 20%, tăng Hype 10","effect":{"price_percent":-20,"hype":10}},
    {"id":"D1","name":"Cost Cutting","cost":1,"type":"babyblue","desc":"Giảm COGS 3%, tăng Transparency 5","effect":{"cogs_percent":-3,"transparency":5}},
    {"id":"D2","name":"Community Update","cost":1,"type":"babyblue","desc":"Tăng Hype 5, Transparency 3","effect":{"hype":5,"transparency":3}},
    {"id":"D3","name":"Third Party Audit","cost":2,"type":"babyblue","desc":"Tăng Transparency 15, giảm rủi ro","effect":{"transparency":15,"reg_risk":-10,"cost_percent":5}},
    {"id":"D4","name":"Vesting Pledge","cost":1,"type":"babyblue","desc":"Tăng Transparency 10, Trust 5","effect":{"transparency":10,"trust_all":5}},
    {"id":"D5","name":"Emergency Fund","cost":2,"type":"babyblue","desc":"Tăng Runway 2 tháng","effect":{"runway":2,"cost_percent":5}},
    {"id":"D6","name":"Open Book","cost":2,"type":"babyblue","desc":"Tăng Transparency 20","effect":{"transparency":20,"cost_percent":2}},
    {"id":"D7","name":"Security Review","cost":1,"type":"babyblue","desc":"Tăng Security 10, Transparency 5","effect":{"security":10,"transparency":5}},
    {"id":"D8","name":"Legal Shield","cost":2,"type":"babyblue","desc":"Giảm rủi ro pháp lý 15","effect":{"reg_risk":-15,"cost_percent":3}},
    {"id":"D9","name":"Slow & Steady","cost":1,"type":"babyblue","desc":"Tăng Transparency 5, Hype 2","effect":{"transparency":5,"hype":2}},
    {"id":"D10","name":"Crisis Management","cost":2,"type":"babyblue","desc":"Giảm 50% delta tiêu cực","effect":{"halve_negative_delta":1,"cost_percent":3}},
    {"id":"D11","name":"Supply Chain Fix","cost":2,"type":"babyblue","desc":"Giảm COGS 5%, tăng Transparency 5","effect":{"cogs_percent":-5,"transparency":5}},
    {"id":"D12","name":"Investor Call","cost":1,"type":"babyblue","desc":"Tăng Trust 10","effect":{"trust_all":10,"cost_percent":1}},
    {"id":"D13","name":"Transparency Report","cost":2,"type":"babyblue","desc":"Tăng Transparency 15, giảm Hype 5","effect":{"transparency":15,"hype":-5}},
    {"id":"D14","name":"Dual Approval","cost":1,"type":"babyblue","desc":"Tăng Security 15, Transparency 5","effect":{"security":15,"transparency":5}},
    {"id":"C1","name":"Whale Discount","cost":3,"type":"lavender","desc":"Tăng Funding 15%, giảm trust Whale","effect":{"funding_boost_percent":15,"trust_whale":-10,"cost_percent":2}},
    {"id":"C2","name":"Investor Protection","cost":2,"type":"lavender","desc":"Tăng Trust 15, Utility 10","effect":{"funding_boost_percent":-10,"trust_all":15,"utility":10,"cost_percent":10}},
    {"id":"C3","name":"Secondary Offering","cost":3,"type":"lavender","desc":"Tăng Funding 20%, giảm trust","effect":{"funding_boost_percent":20,"trust_all":-15}},
    {"id":"C4","name":"DAO Vote","cost":2,"type":"lavender","desc":"Tăng Transparency 5, Trust 5","effect":{"transparency":5,"trust_all":5}},
    {"id":"C5","name":"Customer Retention","cost":2,"type":"lavender","desc":"Tăng Utility 15","effect":{"utility":15,"velocity":-0.2}},
    {"id":"C6","name":"Treasury Diversify","cost":2,"type":"lavender","desc":"Giảm rủi ro 10, tăng Trust 10","effect":{"reg_risk":-10,"trust_all":10}},
    {"id":"C7","name":"Token Split","cost":2,"type":"lavender","desc":"Tăng Funding 5%, Hype 10","effect":{"funding_boost_percent":5,"hype":10}},
    {"id":"C8","name":"Governance Proposal","cost":1,"type":"lavender","desc":"Tăng Transparency 5, Trust 5","effect":{"transparency":5,"trust_all":5}},
    {"id":"C9","name":"Vesting Extension","cost":2,"type":"lavender","desc":"Tăng Trust 20, Transparency 10","effect":{"trust_all":20,"transparency":10,"cost_percent":2}},
    {"id":"C10","name":"Customer Incentive","cost":3,"type":"lavender","desc":"Tăng Utility 20","effect":{"utility":20,"velocity":-0.3,"cost_percent":5}},
    {"id":"C11","name":"Strategic Partnership","cost":2,"type":"lavender","desc":"Tăng Trust 15, giảm rủi ro","effect":{"trust_all":15,"reg_risk":-5,"cost_percent":3}},
    {"id":"C12","name":"Product Upgrade","cost":2,"type":"lavender","desc":"Tăng Utility 15, Hype 10","effect":{"utility":15,"hype":10,"cost_percent":2}},
    {"id":"C13","name":"Airdrop","cost":2,"type":"lavender","desc":"Tăng Trust 10, Hype 15","effect":{"trust_all":10,"hype":15,"cost_percent":4}},
    {"id":"C14","name":"Equity Swap","cost":3,"type":"lavender","desc":"Tăng Funding 30%, giảm trust","effect":{"funding_boost_percent":30,"trust_all":-20}},
]

REACTION_CARDS = [
    {"id":"R1","name":"Lock-up Extension","trigger":"on_bot_withdraw","condition":{"event":"bot_withdraw"},"desc":"Giảm bán tháo 50%","cost_percent":2,"effect":{"sell_pressure_reduce":0.5}},
    {"id":"R2","name":"Emergency PR","trigger":"on_scenario_market_bad","condition":{"event":"market_bad"},"desc":"Giảm 50% delta xấu","cost_percent":3,"effect":{"halve_negative_delta":1}},
    {"id":"R3","name":"Whale Whisperer","trigger":"on_whale_trust_low","condition":{"metric":"whale_trust","operator":"<","value":30},"desc":"Tăng trust Whale 10","cost_percent":5,"effect":{"whale_trust":10}},
    {"id":"R4","name":"Damage Control","trigger":"on_transparency_low","condition":{"metric":"transparency","operator":"<","value":30},"desc":"Tăng Transparency 10, giảm Hype 5","cost_percent":2,"effect":{"transparency":10,"hype":-5}},
    {"id":"R5","name":"Liquidity Injection","trigger":"on_circuit_breaker","condition":{"metric":"circuit_breaker_active","operator":"==","value":True},"desc":"Rút ngắn circuit breaker","cost_percent":8,"effect":{"circuit_breaker_reduce":1}},
    {"id":"R6","name":"Legal Emergency","trigger":"on_reg_risk_high","condition":{"metric":"reg_risk","operator":">","value":70},"desc":"Giảm rủi ro pháp lý 20","cost_percent":4,"effect":{"reg_risk":-20}},
    {"id":"R7","name":"Security Patch","trigger":"on_security_low","condition":{"metric":"security","operator":"<","value":30},"desc":"Tăng Security 15","cost_percent":3,"effect":{"security":15}},
    {"id":"R8","name":"FOMO Suppression","trigger":"on_hype_high","condition":{"metric":"hype","operator":">","value":80},"desc":"Giảm Hype 15, tăng Transparency 5","cost_percent":1,"effect":{"hype":-15,"transparency":5}},
    {"id":"R9","name":"Investor Assurance","trigger":"on_trust_low","condition":{"metric":"min_bot_trust","operator":"<","value":20},"desc":"Tăng trust 5","cost_percent":2,"effect":{"trust_all":5}},
    {"id":"R10","name":"Runway Boost","trigger":"on_runway_low","condition":{"metric":"runway","operator":"<","value":3},"desc":"Thêm 3 tháng runway","cost_percent":10,"effect":{"runway":3}},
]

# ==================== BOT & TÍNH TOÁN ====================
random.seed(42)
BOTS = []
for i in range(1, 201):
    bot_type = random.choices(["FOMO","Value Hunter","Whale","Random"], weights=[50,30,10,10])[0]
    wealth_class = random.choices(["small","medium","large"], weights=[40,40,20])[0]
    wealth = {"small":random.randint(1000,5000), "medium":random.randint(10000,50000), "large":random.randint(50000,200000)}[wealth_class]
    hype_sens = round(random.uniform(0.5,2.5),2)
    trans_sens = round(random.uniform(0.5,1.2),2)
    decay = round(random.uniform(0.05,0.6),2)
    if bot_type == "FOMO":
        weights = {"intrinsic":0.1,"valuation":0.1,"roi_norm":0.1,"scalability":0.05,"transparency":0.05,"hype":0.42,"visibility":0.09,"funding_prog":0.09}
    elif bot_type == "Value Hunter":
        weights = {"intrinsic":0.43,"valuation":0.2,"roi_norm":0.15,"scalability":0.03,"transparency":0.14,"hype":0,"visibility":0,"funding_prog":0.05}
    elif bot_type == "Whale":
        weights = {"intrinsic":0.17,"valuation":0.42,"roi_norm":0.15,"scalability":0.03,"transparency":0.18,"hype":0,"visibility":0,"funding_prog":0.05}
    else:
        weights = {"intrinsic":0.1,"valuation":0.1,"roi_norm":0.1,"scalability":0.05,"transparency":0.05,"hype":0.46,"visibility":0.05,"funding_prog":0.09}
    BOTS.append({"id":i,"type":bot_type,"wealth_class":wealth_class,"wealth":wealth,"hype_sens":hype_sens,"trans_sens":trans_sens,"memory_decay_rate":decay,"weights":weights})

def clamp(x,lo,hi): return max(lo, min(hi, x))

def calculate_metrics(proj):
    proj.setdefault('fee_ecom',0); proj.setdefault('fee_retail',0); proj.setdefault('fee_direct',0)
    proj.setdefault('material',0); proj.setdefault('packaging',0); proj.setdefault('labor',0)
    proj.setdefault('defect_rate',0); proj.setdefault('fixed_cost',0); proj.setdefault('marketing_cost',0)
    proj.setdefault('loan',0); proj.setdefault('interest_rate',0); proj.setdefault('units_m6',1)
    proj.setdefault('units_m1',1); proj.setdefault('target_funding',1); proj.setdefault('owner_equity',0)
    proj.setdefault('total_invested',0); proj.setdefault('available_cash',0); proj.setdefault('transparency',50)
    proj.setdefault('legal_cost_spent',0); proj.setdefault('price',35); proj.setdefault('hype',50)
    proj.setdefault('visibility',50); proj.setdefault('has_license',False)
    total_fees = proj['fee_ecom']+proj['fee_retail']+proj['fee_direct']
    price_real = proj['price']*(1 - total_fees/100)
    cogs_unit = (proj['material']+proj['packaging']+proj['labor'])*(1+proj['defect_rate']/100)
    gm = (price_real-cogs_unit)/price_real if price_real>0 else 0
    monthly_burn = proj['fixed_cost']+proj['marketing_cost'] + (proj['loan']*proj['interest_rate']/100/12)
    burn_rate = monthly_burn/proj['target_funding'] if proj['target_funding']>0 else 0
    growth = (proj['units_m6']/proj['units_m1'])-1 if proj['units_m1']>0 else 0
    gm_score = clamp(20+10*(1-math.exp(-5*(gm-0.2)/0.6)),0,30) if gm>0.2 else clamp(20*(gm/0.2),0,30)
    burn_score = clamp(15+5*(1-math.exp(-4*(0.3-burn_rate)/0.25)),0,20) if burn_rate<0.3 else clamp(15*(1-(burn_rate-0.3)/0.7),0,20)
    growth_score = clamp(10+10*(1-math.exp(-3*growth/0.5)),0,20) if growth>0 else clamp(10*(1+growth/0.5),0,20)
    revenue_year = proj['units_m6']*12*price_real
    revenue_score = min(10, max(0, math.log10(max(1,revenue_year/100000))/2*10))
    total_capital = proj['owner_equity']+proj['loan']+proj['total_invested']
    annual_profit = (price_real-cogs_unit)*proj['units_m6']*12 - monthly_burn*12
    efficiency_score = clamp(min(10, annual_profit/total_capital*10),0,10) if total_capital>0 and annual_profit>0 else 0
    debt_ratio = proj['loan']/proj['owner_equity'] if proj['owner_equity']>0 else 999
    leverage_score = clamp(5+debt_ratio*10,0,10) if debt_ratio<0.5 else clamp(10-(debt_ratio-0.5)*5,0,10) if debt_ratio<=1.5 else clamp(max(0,5-(debt_ratio-1.5)*3),0,10)
    intrinsic = gm_score+burn_score+growth_score+revenue_score+efficiency_score+leverage_score
    ps_ratio = 5 + (2 if proj['hype']>70 else -1 if proj['hype']<30 else 0) + (1.5 if growth>0.5 else -1 if growth<-0.2 else 0)
    ps_ratio = max(1.5, min(15, ps_ratio))
    estimated_valuation = revenue_year * ps_ratio
    raw_roi = max(0, ((estimated_valuation-proj['total_invested'])/proj['total_invested'])*100) if proj['total_invested']>0 else 0
    roi_norm = min(100, 20*math.log10(raw_roi+1))
    mult = estimated_valuation/revenue_year if revenue_year>0 else 1000
    if mult<1: val_score = 30 - (1-mult)/1*30
    elif mult<=3: val_score = 80 + (mult-1)/2*20
    elif mult<=5: val_score = 80 - (mult-3)/2*40
    else: val_score = max(0,40 - (mult-5)/2*40)
    val_score = clamp(val_score,0,100)
    base_reg = 20 if proj['has_license'] else 80
    if proj['legal_cost_spent'] >= 0.05*proj['target_funding']: base_reg += 20
    reg_risk = clamp(base_reg - proj['transparency']/10, 0, 100)
    avail_cash = proj['available_cash']
    runway = math.floor(avail_cash/monthly_burn) if monthly_burn>0 else 999
    funding_progress = min(1.0, proj['total_invested']/proj['target_funding']) if proj['target_funding']>0 else 0
    return {"intrinsic":intrinsic,"valuation_sanity":val_score,"roi_norm":roi_norm,"growth":growth,"monthly_burn":monthly_burn,"available_cash":avail_cash,"runway":runway,"funding_progress":funding_progress,"estimated_valuation":estimated_valuation,"raw_roi":raw_roi,"reg_risk":reg_risk}

def attractiveness(project, bot, metrics):
    raw=0; total_w=0
    for key,w in bot['weights'].items():
        if key=='intrinsic': val=metrics['intrinsic']
        elif key=='valuation': val=metrics['valuation_sanity']
        elif key=='roi_norm': val=metrics['roi_norm']
        elif key=='scalability': val=clamp(metrics['growth']*100,0,100)
        elif key=='transparency': val=project['transparency']
        elif key=='hype': val=project['hype']
        elif key=='visibility': val=project.get('visibility',50)
        elif key=='funding_prog': val=metrics['funding_progress']*100
        else: continue
        sens = bot['hype_sens'] if key=='hype' else (bot['trans_sens'] if key=='transparency' else 1.0)
        raw += val * w * sens
        total_w += w
    if total_w==0: return 0
    raw_A = (raw/total_w)*100
    if metrics['valuation_sanity']<40: raw_A = max(0, raw_A - (40-metrics['valuation_sanity'])*1.5)
    trust = project['trust_scores'].get(bot['id'],50)
    noise = random.uniform(-5,5) if bot['type']!='Random' else random.uniform(-10,10)
    return raw_A*(trust/100)+noise

def get_bots_for_phase(phase, total_bots=200):
    count = int(total_bots * min(1.0, phase*0.2))
    return BOTS[:count]

def process_phase(room, phase, players, logs):
    active_bots = get_bots_for_phase(phase)
    logs.append(f"Phase {phase}: {len(active_bots)} bots active")
    bot_alloc = room['bot_alloc']
    A = {}
    for bot in active_bots:
        for idx,proj in enumerate(players):
            if not proj or proj.get('status')!='active' or proj.get('funding_progress',0)>=1 or proj.get('current_phase',0)>=proj.get('max_phase',5):
                A[(bot['id'],idx)] = -1e9
            else:
                metrics = calculate_metrics(proj)
                hist = room['bot_memory'][bot['id']]['attractiveness_history'][idx]
                current_attr = attractiveness(proj, bot, metrics)
                if hist:
                    weighted_avg = sum((i+1)*val for i,val in enumerate(hist))/sum(range(1,len(hist)+1))
                    final_attr = (1-bot['memory_decay_rate'])*current_attr + bot['memory_decay_rate']*weighted_avg
                else:
                    final_attr = current_attr
                hist.append(current_attr)
                if len(hist)>5: hist.pop(0)
                A[(bot['id'],idx)] = final_attr
    for bot in active_bots:
        best_idx = max(range(len(players)), key=lambda i: A.get((bot['id'],i),-1e9))
        alloc_entry = next(e for e in bot_alloc if e['bot_id']==bot['id'])
        for idx in range(len(players)):
            invested = alloc_entry['perProject'][idx]
            if invested==0: continue
            if players[idx].get('status')!='active' or players[idx].get('current_phase',0)>=players[idx].get('max_phase',5):
                if invested>0:
                    players[idx]['available_cash'] = max(0, players[idx].get('available_cash',0)-invested)
                    alloc_entry['idle'] += invested
                    alloc_entry['perProject'][idx]=0
                    logs.append(f"Bot {bot['type']} rút {invested:.0f} từ dự án {idx+1} (kết thúc)")
                continue
            diff = A.get((bot['id'],best_idx),-1e9) - A.get((bot['id'],idx),-1e9)
            if diff>15: withdraw_ratio=1.0
            elif diff>5: withdraw_ratio=0.3
            else: withdraw_ratio=0.0
            max_ratio = min(0.6, 0.2+(phase-1)*0.05)
            actual = min(invested*withdraw_ratio, invested*max_ratio)
            if actual>0:
                if actual <= players[idx].get('available_cash',0):
                    players[idx]['available_cash'] -= actual
                    alloc_entry['perProject'][idx] -= actual
                    alloc_entry['idle'] += actual
                    logs.append(f"Bot {bot['type']} rút {actual:.0f} từ dự án {idx+1}")
                else:
                    players[idx]['status']='bankrupt'
                    players[idx]['funding_progress']=0
                    logs.append(f"💀 Dự án {idx+1} PHÁ SẢN!")
    for bot in active_bots:
        alloc_entry = next(e for e in bot_alloc if e['bot_id']==bot['id'])
        idle = alloc_entry['idle']
        if idle<=0: continue
        candidates = [i for i,p in enumerate(players) if p and p.get('status')=='active' and p.get('funding_progress',0)<1 and p.get('current_phase',0)<p.get('max_phase',5)]
        if not candidates: continue
        attrs = [A.get((bot['id'],i),-1e9) for i in candidates]
        min_a = min(attrs)
        shifted = [max(0,a-min_a+0.01) for a in attrs]
        sum_exp = sum(math.exp(a/20) for a in shifted)
        probs = [math.exp(a/20)/sum_exp for a in shifted]
        remaining = idle
        for _ in range(5):
            if remaining<=0: break
            for j,idx in enumerate(candidates):
                invest = remaining * probs[j]
                max_per_bot = players[idx]['target_funding'] * (0.2 if phase==1 else 0.25)
                cap = min(invest, max_per_bot - alloc_entry['perProject'][idx])
                if cap>0:
                    players[idx]['total_invested'] = players[idx].get('total_invested',0)+cap
                    players[idx]['available_cash'] = players[idx].get('available_cash',0)+cap
                    players[idx]['funding_progress'] = min(1.0, players[idx]['total_invested']/players[idx]['target_funding'])
                    alloc_entry['perProject'][idx] += cap
                    remaining -= cap
                    logs.append(f"Bot {bot['type']} đầu tư {cap:.0f} vào dự án {idx+1}")
        alloc_entry['idle'] = remaining

# ==================== FLASK APP & ROOMS ====================
rooms = {}

@app.route('/')
def index():
    return render_template('host.html')

@app.route('/play/<room_id>/<int:player_index>')
def play_page(room_id, player_index):
    if room_id not in rooms:
        return "Phòng không tồn tại", 404
    room = rooms[room_id]
    if player_index < 0 or player_index >= room['num_players']:
        return "Số người chơi không hợp lệ", 400
    return render_template('play.html', room_id=room_id, player_index=player_index)

@app.route('/api/rooms', methods=['POST'])
def create_room():
    data = request.json
    name = data.get('name', 'Startup Game')
    max_players = int(data.get('maxPlayers', 4))
    if not 2 <= max_players <= 10:
        return jsonify({'error': 'Số người chơi từ 2 đến 10'}), 400
    room_id = str(uuid.uuid4())[:8]
    base_url = request.host_url.rstrip('/')
    rooms[room_id] = {
        'name': name,
        'num_players': max_players,
        'players': [None]*max_players,
        'phase': 0,
        'max_phase': 0,
        'status': 'waiting_for_projects',
        'bot_alloc': None,
        'logs': ["Phòng tạo, chờ submit dự án..."],
        'player_ready': [False]*max_players,
        'deck_ready': [False]*max_players,
        'pending_cards': {},
        'phase_energy': [3]*max_players,
        'mulligan_used': [False]*max_players,
        'game_ended': False,
        'player_triggers': [{} for _ in range(max_players)],
        'bot_memory': {bot['id']: {'attractiveness_history': [[] for _ in range(max_players)]} for bot in BOTS},
        'submitted_players': 0,
        'phase_details': []
    }
    join_links = [f"{base_url}/play/{room_id}/{i}" for i in range(max_players)]
    return jsonify({
        'id': room_id,
        'name': name,
        'maxPlayers': max_players,
        'joinLinks': [{'playerIndex': i, 'playerName': f'Player {i+1}', 'realLink': join_links[i]} for i in range(max_players)]
    })

@app.route('/api/rooms/<room_id>', methods=['GET'])
def get_room(room_id):
    if room_id not in rooms:
        return jsonify({'error': 'Room not found'}), 404
    room = rooms[room_id]
    base_url = request.host_url.rstrip('/')
    join_links = [f"{base_url}/play/{room_id}/{i}" for i in range(room['num_players'])]
    players_data = []
    for idx, p in enumerate(room['players']):
        if p:
            metrics = calculate_metrics(p)
            players_data.append({
                'id': idx,
                'name': f"Player {idx+1}",
                'status': p.get('status', 'active'),
                'funding': p.get('funding_progress', 0),
                'hype': p.get('hype', 50),
                'transparency': p.get('transparency', 50),
                'score': 0  # sẽ tính sau
            })
        else:
            players_data.append({'id': idx, 'name': f"Player {idx+1}", 'status': 'not_joined', 'funding': 0, 'score': 0})
    return jsonify({
        'id': room_id,
        'name': room['name'],
        'maxPlayers': room['num_players'],
        'joinedPlayers': sum(1 for p in room['players'] if p),
        'currentPhase': room['phase'],
        'maxPhase': room['max_phase'],
        'ended': room['game_ended'],
        'status': room['status'],
        'players': players_data,
        'logs': room.get('logs', [])[-50:],
        'joinLinks': [{'playerIndex': i, 'playerName': f"Player {i+1}", 'realLink': join_links[i]} for i in range(room['num_players'])]
    })

@app.route('/api/submit_project', methods=['POST'])
def submit_project():
    data = request.json
    room_id = data['room_id']
    player_index = data['player_index']
    project_data = data['project']
    if room_id not in rooms: return jsonify({'error':'Room not found'}),404
    room = rooms[room_id]
    if room['players'][player_index] is not None: return jsonify({'error':'Already submitted'}),400
    default_fields = {
        'fee_ecom':0,'fee_retail':0,'fee_direct':0,'material':0,'packaging':0,'labor':0,'defect_rate':0,
        'fixed_cost':0,'marketing_cost':0,'loan':0,'interest_rate':0,'units_m6':0,'units_m1':0,
        'owner_equity':50000,'total_invested':0,'available_cash':80000,'legal_cost_spent':0,'current_phase':0,
        'hype':50,'transparency':50,'visibility':50,'active_deck':None,'reaction_hand':None,'current_hand':[],
        'energy_left':3,'trust_scores':{bot['id']:50 for bot in BOTS},'status':'active','funding_progress':0,
        'scale_factor':1.0,'max_phase':project_data.get('max_phase',7),'target_funding':project_data.get('target_funding',150000),
        'price':project_data.get('price',35)
    }
    default_fields.update(project_data)
    room['players'][player_index] = default_fields
    room['submitted_players'] += 1
    room['logs'].append(f"✅ Player {player_index+1} đã submit dự án.")
    # Nếu đủ 2 người, tự động bắt đầu deck phase
    if room['status'] == 'waiting_for_projects' and room['submitted_players'] >= 2:
        room['status'] = 'choosing_deck'
        room['player_ready'] = [False]*room['num_players']
        room['logs'].append(f"🃏 Đã có {room['submitted_players']} người chơi, bắt đầu chọn Deck!")
    return jsonify({'ok':True, 'submitted_count':room['submitted_players']})

@app.route('/api/start_deck_phase', methods=['POST'])
def start_deck_phase():
    data = request.json
    room_id = data['room_id']
    if room_id not in rooms: return jsonify({'error':'Room not found'}),404
    room = rooms[room_id]
    if room['status'] != 'waiting_for_projects': return jsonify({'error':'Invalid status'}),400
    if room['submitted_players'] < 2: return jsonify({'error':'Need at least 2 projects'}),400
    room['status'] = 'choosing_deck'
    room['player_ready'] = [False]*room['num_players']
    room['logs'].append(f"🃏 Bắt đầu chọn Deck với {room['submitted_players']} người chơi.")
    return jsonify({'ok':True})

@app.route('/api/card_lists', methods=['GET'])
def card_lists():
    return jsonify({'active': ACTIVE_CARDS_FULL, 'reaction': REACTION_CARDS})

@app.route('/api/submit_deck', methods=['POST'])
def submit_deck():
    data = request.json
    room_id = data['room_id']
    player_index = data['player_index']
    active_indices = data['active_indices']
    reaction_indices = data.get('reaction_indices', [])
    if room_id not in rooms: return jsonify({'error':'Room not found'}),404
    room = rooms[room_id]
    if room['status'] != 'choosing_deck': return jsonify({'error':'Not in deck selection phase'}),400
    if len(active_indices) != 22: return jsonify({'error':'Must choose exactly 22 active cards'}),400
    proj = room['players'][player_index]
    proj['active_deck'] = [ACTIVE_CARDS_FULL[i] for i in active_indices]
    proj['reaction_hand'] = [REACTION_CARDS[i].copy() for i in reaction_indices]
    room['deck_ready'][player_index] = True
    # Nếu tất cả đã ready, bắt đầu game
    all_ready = all(room['deck_ready'][i] for i in range(room['num_players']) if room['players'][i] is not None)
    if all_ready:
        room['max_phase'] = max(p['max_phase'] for p in room['players'] if p)
        room['bot_alloc'] = [{'bot_id':bot['id'], 'perProject':[0]*room['num_players'], 'idle':bot['wealth']} for bot in BOTS]
        room['phase'] = 1
        room['status'] = 'playing'
        room['logs'].append("🎮 Tất cả đã chọn deck, game bắt đầu!")
        for idx,p in enumerate(room['players']):
            if p and p.get('active_deck'):
                p['current_hand'] = random.sample(p['active_deck'], min(5, len(p['active_deck'])))
                p['energy_left'] = 3
    return jsonify({'ok':True})

@app.route('/api/player_state', methods=['GET'])
def player_state():
    room_id = request.args.get('room_id')
    player_index = int(request.args.get('player_index'))
    if room_id not in rooms: return jsonify({'error':'Room not found'}),404
    room = rooms[room_id]
    if player_index>=len(room['players']) or room['players'][player_index] is None:
        return jsonify({'error':'Player not found'}),404
    proj = room['players'][player_index]
    metrics = calculate_metrics(proj)
    investors = []
    if room.get('bot_alloc'):
        for alloc in room['bot_alloc']:
            amount = alloc['perProject'][player_index] if player_index<len(alloc['perProject']) else 0
            if amount>0:
                bot = next((b for b in BOTS if b['id']==alloc['bot_id']), None)
                if bot: investors.append({'type':bot['type'], 'amount':amount})
    is_ended = proj.get('status') in ['ended','funded','bankrupt'] or proj.get('current_phase',0)>=proj.get('max_phase',5)
    triggers = room.get('player_triggers',[{}])[player_index].get('available_reactions',[])
    return jsonify({
        'status': room['status'],
        'phase': room['phase'],
        'last_scenario': proj.get('last_scenario','Chưa có'),
        'metrics': {
            'intrinsic': metrics['intrinsic'],
            'valuation_sanity': metrics['valuation_sanity'],
            'roi_norm': metrics['roi_norm'],
            'runway': metrics['runway'],
            'funding_progress': proj['funding_progress']
        },
        'hype': proj['hype'],
        'transparency': proj['transparency'],
        'hand': proj.get('current_hand',[]),
        'energy_left': proj.get('energy_left',3),
        'mulligan_used': room['mulligan_used'][player_index],
        'investors': investors,
        'funding_progress': proj['funding_progress'],
        'available_cash': metrics['available_cash'],
        'reaction_hand': proj.get('reaction_hand',[]),
        'game_ended': room['game_ended'],
        'ended': is_ended,
        'final_score': 0,
        'triggers': triggers
    })

@app.route('/api/play_card', methods=['POST'])
def play_card():
    data = request.json
    room_id = data['room_id']; player_index = data['player_index']; card_index = data['card_index']
    if room_id not in rooms: return jsonify({'error':'Room not found'}),404
    room = rooms[room_id]
    if room['status']!='playing': return jsonify({'error':'Not playing'}),400
    proj = room['players'][player_index]
    hand = proj.get('current_hand',[])
    if card_index>=len(hand): return jsonify({'error':'Invalid card'}),400
    card = hand[card_index]
    if proj.get('energy_left',0) < card['cost']: return jsonify({'error':'Not enough energy'}),400
    room['pending_cards'][player_index] = copy.deepcopy(card)
    proj['energy_left'] -= card['cost']
    hand.pop(card_index)
    return jsonify({'ok':True})

@app.route('/api/mulligan', methods=['POST'])
def mulligan():
    data = request.json
    room_id = data['room_id']; player_index = data['player_index']
    if room_id not in rooms: return jsonify({'error':'Room not found'}),404
    room = rooms[room_id]
    if room['status']!='playing': return jsonify({'error':'Not playing'}),400
    proj = room['players'][player_index]
    if room['mulligan_used'][player_index]: return jsonify({'error':'Already used mulligan'}),400
    if proj.get('energy_left',0) < 1: return jsonify({'error':'Need 1 energy'}),400
    proj['current_hand'] = random.sample(proj['active_deck'], min(5, len(proj['active_deck'])))
    proj['energy_left'] -= 1
    proj['transparency'] = max(0, proj['transparency']-2)
    for bid in proj['trust_scores']:
        proj['trust_scores'][bid] = max(0, proj['trust_scores'][bid]-1)
    room['mulligan_used'][player_index] = True
    return jsonify({'ok':True})

@app.route('/api/player_ready_phase', methods=['POST'])
def player_ready_phase():
    data = request.json
    room_id = data['room_id']; player_index = data['player_index']
    if room_id not in rooms: return jsonify({'error':'Room not found'}),404
    room = rooms[room_id]
    if room['status']!='playing': return jsonify({'error':'Not playing'}),400
    room['player_ready'][player_index] = True
    return jsonify({'ok':True})

@app.route('/api/run_phase', methods=['POST'])
def run_phase():
    data = request.json
    room_id = data['room_id']
    if room_id not in rooms: return jsonify({'error':'Room not found'}),404
    room = rooms[room_id]
    if room['status']!='playing': return jsonify({'error':'Not playing'}),400
    # Kiểm tra ready
    for i,p in enumerate(room['players']):
        if p and p.get('status')=='active' and not room['player_ready'][i]:
            return jsonify({'error':'Not all players ready'}),400
    phase = room['phase']
    players = room['players']
    logs = []
    # Xử lý sự kiện và thẻ
    for idx,proj in enumerate(players):
        if not proj or proj.get('status')!='active' or proj.get('current_phase',0)>=proj.get('max_phase',5):
            continue
        scenario = random.choice(SCENARIOS)
        proj['last_scenario'] = scenario['name']
        logs.append(f"Dự án {idx+1}: {scenario['name']}")
        d = scenario['delta']
        if 'price' in d: proj['price'] *= (1+d['price'])
        if 'cogs' in d:
            proj['material'] = proj.get('material',0)*(1+d['cogs'])
            proj['packaging'] = proj.get('packaging',0)*(1+d['cogs'])
            proj['labor'] = proj.get('labor',0)*(1+d['cogs'])
        if 'hype' in d: proj['hype'] = clamp(proj['hype']+d['hype'],0,100)
        if 'transparency' in d: proj['transparency'] = clamp(proj['transparency']+d['transparency'],0,100)
        if 'runway' in d:
            m = calculate_metrics(proj)
            proj['available_cash'] = proj.get('available_cash',0) + d['runway']*m.get('monthly_burn',0)
        if idx in room['pending_cards']:
            card = room['pending_cards'][idx]
            if card:
                eff = card.get('effect',{})
                if 'hype' in eff: proj['hype'] = clamp(proj['hype']+eff['hype'],0,100)
                if 'transparency' in eff: proj['transparency'] = clamp(proj['transparency']+eff['transparency'],0,100)
                if 'price_percent' in eff: proj['price'] *= (1+eff['price_percent']/100)
                if 'cogs_percent' in eff:
                    proj['material'] *= (1+eff['cogs_percent']/100)
                    proj['packaging'] *= (1+eff['cogs_percent']/100)
                    proj['labor'] *= (1+eff['cogs_percent']/100)
                if 'funding_boost_percent' in eff:
                    boost = (eff['funding_boost_percent']/100)*proj['target_funding']
                    proj['total_invested'] += boost
                    proj['available_cash'] += boost
                    proj['funding_progress'] = min(1.0, proj['total_invested']/proj['target_funding'])
                logs.append(f" → Dự án {idx+1} chơi thẻ {card['name']}")
        # Reaction triggers (đơn giản)
        triggers = []
        for rc in proj.get('reaction_hand',[]):
            if rc.get('trigger')=='on_transparency_low' and proj['transparency']<30:
                triggers.append(rc)
            elif rc.get('trigger')=='on_hype_high' and proj['hype']>80:
                triggers.append(rc)
        if triggers:
            room['player_triggers'][idx]['available_reactions'] = triggers
            logs.append(f" → Dự án {idx+1} có {len(triggers)} reaction có thể kích hoạt")
        proj['current_phase'] += 1
        if proj['current_phase'] >= proj['max_phase']:
            proj['status'] = 'ended'
            logs.append(f" → Dự án {idx+1} kết thúc.")
    # Xử lý bot đầu tư
    process_phase(room, phase, players, logs)
    room['pending_cards'] = {}
    room['player_ready'] = [False]*room['num_players']
    room['logs'].extend(logs)
    room['logs'] = room['logs'][-100:]
    room['phase'] += 1
    # Reset hand và energy cho các dự án còn sống
    for idx,proj in enumerate(players):
        if proj and proj.get('status')=='active' and proj.get('current_phase',0)<proj.get('max_phase',5):
            proj['current_hand'] = random.sample(proj['active_deck'], min(5, len(proj['active_deck'])))
            proj['energy_left'] = 3
            room['mulligan_used'][idx] = False
    # Kiểm tra kết thúc
    all_ended = all(p is None or p.get('current_phase',0)>=p.get('max_phase',5) for p in players)
    if room['phase'] > room['max_phase'] or all_ended:
        room['game_ended'] = True
        room['status'] = 'ended'
    return jsonify({'ended': room['game_ended'], 'phase': room['phase']-1, 'logs': logs})

@app.route('/api/rooms/<room_id>/next-phase', methods=['POST'])
def next_phase_route(room_id):
    if room_id not in rooms: return jsonify({'error':'Room not found'}),404
    # Gọi run_phase
    with app.test_request_context(json={'room_id': room_id}):
        return run_phase()

@app.route('/api/rooms/<room_id>/random-event', methods=['POST'])
def random_event_route(room_id):
    if room_id not in rooms: return jsonify({'error':'Room not found'}),404
    room = rooms[room_id]
    if room['status'] != 'playing': return jsonify({'error':'Not playing'}),400
    for proj in room['players']:
        if proj and proj.get('status')=='active':
            scenario = random.choice(SCENARIOS)
            proj['last_scenario'] = scenario['name']
            d = scenario['delta']
            if 'price' in d: proj['price'] *= (1+d['price'])
            if 'cogs' in d:
                proj['material'] *= (1+d['cogs'])
                proj['packaging'] *= (1+d['cogs'])
                proj['labor'] *= (1+d['cogs'])
            if 'hype' in d: proj['hype'] = clamp(proj['hype']+d['hype'],0,100)
            if 'transparency' in d: proj['transparency'] = clamp(proj['transparency']+d['transparency'],0,100)
            if 'runway' in d:
                m = calculate_metrics(proj)
                proj['available_cash'] += d['runway'] * m.get('monthly_burn',0)
    return jsonify({'ok':True})

@app.route('/api/rooms/<room_id>/reset-phase', methods=['POST'])
def reset_phase_route(room_id):
    if room_id not in rooms: return jsonify({'error':'Room not found'}),404
    room = rooms[room_id]
    if room['phase'] > 1:
        room['phase'] -= 1
        for p in room['players']:
            if p: p['current_phase'] = room['phase']
    return jsonify({'ok':True})

@app.route('/api/rooms/<room_id>/end', methods=['POST'])
def end_route(room_id):
    if room_id not in rooms: return jsonify({'error':'Room not found'}),404
    rooms[room_id]['game_ended'] = True
    rooms[room_id]['status'] = 'ended'
    return jsonify({'ok':True})

@app.route('/api/rooms/<room_id>/reset', methods=['POST'])
def reset_route(room_id):
    if room_id not in rooms: return jsonify({'error':'Room not found'}),404
    old = rooms[room_id]
    rooms[room_id] = {
        'name': old['name'],
        'num_players': old['num_players'],
        'players': [None]*old['num_players'],
        'phase': 0,
        'max_phase': 0,
        'status': 'waiting_for_projects',
        'bot_alloc': None,
        'logs': ["Phòng đã reset."],
        'player_ready': [False]*old['num_players'],
        'deck_ready': [False]*old['num_players'],
        'pending_cards': {},
        'phase_energy': [3]*old['num_players'],
        'mulligan_used': [False]*old['num_players'],
        'game_ended': False,
        'player_triggers': [{} for _ in range(old['num_players'])],
        'bot_memory': {bot['id']: {'attractiveness_history': [[] for _ in range(old['num_players'])]} for bot in BOTS},
        'submitted_players': 0,
        'phase_details': []
    }
    return jsonify({'ok':True})

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True, threaded=True)
