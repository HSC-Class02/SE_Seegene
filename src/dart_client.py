import io, time, zipfile
import requests

BASE = 'https://opendart.fss.or.kr/api'

class DartError(RuntimeError): pass

class DartClient:
    def __init__(self, key):
        if not key or len(key.strip()) != 40:
            raise DartError('DART_API_KEY가 없거나 40자 API 키가 아닙니다.')
        self.key = key.strip()
        self.s = requests.Session()

    def json_api(self, endpoint, **params):
        r = self.s.get(f'{BASE}/{endpoint}', params={'crtfc_key': self.key, **params}, timeout=90)
        r.raise_for_status()
        d = r.json()
        if d.get('status') not in ('000', '013'):
            raise DartError(f"{endpoint}: {d.get('status')} {d.get('message')}")
        return d

    def corp_code(self, name='씨젠', stock_code='096530'):
        r = self.s.get(f'{BASE}/corpCode.xml', params={'crtfc_key': self.key}, timeout=120)
        r.raise_for_status()
        zdata = io.BytesIO(r.content)
        if not zipfile.is_zipfile(zdata): raise DartError('corpCode.xml 응답이 ZIP이 아닙니다. API 키/호출 한도를 확인하세요.')
        import xml.etree.ElementTree as ET
        with zipfile.ZipFile(zdata) as z:
            xml = next(n for n in z.namelist() if n.lower().endswith('.xml'))
            root = ET.fromstring(z.read(xml))
        for n in root.findall('.//list'):
            if (n.findtext('stock_code') or '').strip() == stock_code: return (n.findtext('corp_code') or '').strip()
        for n in root.findall('.//list'):
            if (n.findtext('corp_name') or '').strip() == name: return (n.findtext('corp_code') or '').strip()
        raise DartError(f'{name}({stock_code}) 기업코드를 찾지 못했습니다.')

    def disclosures(self, corp_code, start, end):
        out=[]; page=1
        while True:
            d=self.json_api('list.json', corp_code=corp_code, bgn_de=start, end_de=end,
                            page_no=page, page_count=100, sort='date', sort_mth='asc')
            out.extend(d.get('list', []))
            if page >= int(d.get('total_page', 1) or 1): break
            page += 1; time.sleep(.15)
        return out

    def financials(self, corp_code, year, code, fs_div):
        return self.json_api('fnlttSinglAcntAll.json', corp_code=corp_code, bsns_year=str(year),
                             reprt_code=code, fs_div=fs_div).get('list', [])

    def original(self, rcept_no):
        r=self.s.get(f'{BASE}/document.xml', params={'crtfc_key':self.key,'rcept_no':rcept_no}, timeout=120)
        r.raise_for_status()
        if not zipfile.is_zipfile(io.BytesIO(r.content)):
            raise DartError(f'원문 ZIP 응답이 아닙니다: {r.text[:200]}')
        return r.content
