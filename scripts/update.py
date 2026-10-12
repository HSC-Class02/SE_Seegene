import os, sys, json, yaml
from pathlib import Path
from datetime import date, datetime
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.dart_client import DartClient
from src.analyzer import extract, analyze
ROOT=Path(__file__).resolve().parents[1]
def save(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
def main():
    cfg=yaml.safe_load((ROOT/'config.yml').read_text(encoding='utf-8')); co=cfg['company']
    api=DartClient(os.getenv('DART_API_KEY','')); corp=co.get('corp_code') or api.corp_code(co['name'],co['stock_code'])
    today=date.today(); start=int(co.get('start_year',2010))
    all_filings=api.disclosures(corp,f'{start}0101',today.strftime('%Y%m%d'))
    wanted=('사업보고서','반기보고서','분기보고서'); filings=[]
    for x in all_filings:
        title=x.get('report_nm','')
        if any(t in title for t in wanted) and x.get('rcept_no'):
            filings.append({'rcept_no':x['rcept_no'],'rcept_dt':x.get('rcept_dt',''),'report_nm':title,
                            'corp_name':x.get('corp_name',co['name']),'url':'https://dart.fss.or.kr/dsaf001/main.do?rcpNo='+x['rcept_no']})
    raw=ROOT/'reports/raw'; raw.mkdir(parents=True,exist_ok=True); known={p.stem for p in raw.glob('*.zip')}; new=0
    for f in filings:
        if f['rcept_no'] in known or not cfg['reports'].get('download_originals',True): continue
        try:
            b=api.original(f['rcept_no']); limit=int(cfg['reports'].get('max_original_zip_mb',80))*1024*1024
            if len(b)<=limit: (raw/(f['rcept_no']+'.zip')).write_bytes(b); new+=1
            else: f['original_note']='원문 ZIP이 설정 용량 한도를 초과해 메타데이터만 저장'
        except Exception as e: f['original_note']=str(e)[:250]
    save(ROOT/'reports/metadata/filings.json',{'company':co['name'],'corp_code':corp,'updated_at':datetime.now().astimezone().isoformat(),'count':len(filings),'filings':filings})
    # Annual, half-year, Q1 and Q3 financial statement endpoints. DART values may be cumulative.
    periods=[('annual','11011'),('half-year','11012'),('quarterly-Q1','11013'),('quarterly-Q3','11014')]
    records=[]; errors=[]
    for year in range(start,today.year+1):
        for period,code in periods:
            rows=[]; chosen=None
            for fs in (['CFS','OFS'] if cfg['financials'].get('prefer_consolidated',True) else ['OFS','CFS']):
                try:
                    rows=api.financials(corp,year,code,fs)
                    if rows: chosen=fs; break
                except Exception as e: errors.append({'year':year,'period':period,'fs_div':fs,'error':str(e)[:180]})
            if rows:
                values=extract(rows)
                filing=next((f for f in reversed(filings) if str(year) in f.get('rcept_dt','')),None)
                records.append({'year':year,'period':period,'reprt_code':code,'fs_div':chosen,'filing':filing,'values':values})
    records.sort(key=lambda r:(r['year'],r['period']))
    lookup={(r['year'],r['period']):r for r in records}
    for r in records: r['ratios']=analyze(r['values'],lookup.get((r['year']-1,r['period']),{}).get('values'))
    payload={'company':co['name'],'corp_code':corp,'stock_code':co['stock_code'],'updated_at':datetime.now().astimezone().isoformat(),
      'source':'OpenDART API','source_url':'https://opendart.fss.or.kr/','start_year':start,'report_count':len(filings),
      'original_zip_new_count':new,'records':records,'filings':filings,'errors':errors[-100:],
      'notes':['금액은 DART 원본 단위(원)입니다.','CFS 연결 기준 우선, 없으면 OFS 별도 기준으로 저장하며 fs_div를 표시합니다.',
      'ROA/ROE는 현재 구현에서 기말 잔액 기준 근사치입니다. 평균 잔액이 필요한 엄밀한 계산과 다를 수 있습니다.',
      '당좌비율·ROIC·DSO/DIO/DPO/CCC는 필수 입력 계정이 충분하지 않아 공란으로 둡니다.',
      'PER/PBR/EV/EBITDA는 시장가격 데이터가 필요하므로 DART 재무 API만으로 산출하지 않습니다.']}
    save(ROOT/'data/financials.json',payload); save(ROOT/'data/latest.json',payload)
    print(f"완료: {co['name']} corp_code={corp}, filings={len(filings)}, records={len(records)}, new_zip={new}")
if __name__=='__main__':
    try: main()
    except Exception as e: print(f'ERROR: {e}',file=sys.stderr); sys.exit(1)
