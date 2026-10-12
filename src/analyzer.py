ALIASES = {
'revenue':['매출액','수익(매출액)','영업수익','매출'], 'cost_of_sales':['매출원가','수익원가'],
'gross_profit':['매출총이익','매출총손익'], 'operating_income':['영업이익','영업이익(손실)','영업손익'],
'profit_before_tax':['법인세비용차감전순이익','법인세비용차감전순이익(손실)'],
'net_income':['당기순이익','당기순이익(손실)','분기순이익','반기순이익'],
'assets':['자산총계'],'current_assets':['유동자산'],'cash':['현금및현금성자산','현금 및 현금성자산'],
'receivables':['매출채권','매출채권및기타채권','매출채권 및 기타채권'],'inventory':['재고자산'],
'ppe':['유형자산'],'liabilities':['부채총계'],'current_liabilities':['유동부채'],
'payables':['매입채무','매입채무및기타채무','매입채무 및 기타채무'],'equity':['자본총계'],
'interest_expense':['이자비용','금융원가','금융비용'],'depreciation':['감가상각비'],
'amortization':['무형자산상각비','상각비'],'cfo':['영업활동현금흐름'],'cfi':['투자활동현금흐름'],
'cff':['재무활동현금흐름'],'capex':['유형자산의 취득','유형자산 취득'],
'short_debt':['단기차입금'],'long_debt':['장기차입금','유동성장기차입금']}

def norm(x): return ''.join(str(x or '').split())
def extract(rows):
    out={}
    for key, aliases in ALIASES.items():
        for a in aliases:
            hit=next((r for r in rows if norm(r.get('account_nm'))==norm(a)),None)
            if hit:
                try: out[key]=float(str(hit.get('thstrm_amount','')).replace(',',''))
                except (ValueError,TypeError): pass
                if key in out: break
    return out

def div(a,b): return a/b if a is not None and b not in (None,0) else None
def analyze(v, prev=None):
    rev=v.get('revenue'); op=v.get('operating_income'); ni=v.get('net_income')
    gross=v.get('gross_profit')
    if gross is None and rev is not None and v.get('cost_of_sales') is not None: gross=rev-v['cost_of_sales']
    debt=v.get('liabilities'); eq=v.get('equity'); assets=v.get('assets'); cfo=v.get('cfo')
    borrow=(v.get('short_debt') or 0)+(v.get('long_debt') or 0) if ('short_debt' in v or 'long_debt' in v) else None
    ebitda=op+(v.get('depreciation') or 0)+(v.get('amortization') or 0) if op is not None and v.get('depreciation') is not None else None
    out={'gross_margin':div(gross,rev),'operating_margin':div(op,rev),'net_margin':div(ni,rev),
         'current_ratio':div(v.get('current_assets'),v.get('current_liabilities')),
         'debt_to_equity':div(debt,eq),'equity_ratio':div(eq,assets),'debt_dependency':div(debt,assets),
         'roa':div(ni,assets),'roe':div(ni,eq),'cfo_to_net_income':div(cfo,ni),
         'fcf':cfo-abs(v.get('capex') or 0) if cfo is not None else None,
         'interest_coverage':div(op,v.get('interest_expense')),'interest_bearing_debt':borrow,
         'net_debt':borrow-v.get('cash') if borrow is not None and v.get('cash') is not None else None,
         'ebitda_estimate':ebitda}
    out['net_debt_to_ebitda']=div(out['net_debt'],ebitda)
    out['revenue_growth']=div(rev,prev.get('revenue'))-1 if prev and rev is not None and prev.get('revenue') not in (None,0) else None
    # Do not fabricate metrics requiring average balances, purchases, market price or WACC.
    for k in ('quick_ratio','roic','dso','dio','dpo','ccc','per','pbr','ev_ebitda'): out[k]=None
    return out
