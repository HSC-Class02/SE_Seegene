
company:
  name: 씨젠
  corp_code: ""
  stock_code: "096530"
  start_year: 2010
reports:
  download_originals: true
  max_original_zip_mb: 80
financials:
  prefer_consolidated: true
  fallback_to_separate: true
peer_firms:
  - {name: 에스디바이오센서, ticker: "137310", business: 체외진단·분자진단·신속진단}
  - {name: 바이오니아, ticker: "064550", business: 분자진단·분자생물학 제품}
  - {name: 랩지노믹스, ticker: "084650", business: 분자진단·유전체 분석}
  - {name: 바디텍메드, ticker: "206640", business: 체외진단·면역진단}
  - {name: 수젠텍, ticker: "253840", business: 체외진단·진단키트}

<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta http-equiv="refresh" content="0; url=dashboard/"></head><body><a href="dashboard/">씨젠 재무 분석 대시보드 바로가기</a></body></html>

# 씨젠 OpenDART 재무 분석 Agent

[![🔗 대시보드 바로가기](https://img.shields.io/badge/%F0%9F%94%97-%EB%8C%80%EC%8B%9C%EB%B3%B4%EB%93%9C%20%EB%B0%94%EB%A1%9C%EA%B0%80%EA%B8%B0-2457A7?style=for-the-badge)](https://HSC-Class02.github.io/SE_Seegene/)

OpenDART API로 씨젠의 사업보고서·반기보고서·분기보고서와 재무제표를 수집하고 주요 재무비율을 계산해 GitHub Pages 대시보드로 표시합니다. RSS는 사용하지 않습니다.

## 최초 설정 및 배포
1. OpenDART에서 발급한 40자리 인증키를 GitHub 저장소의 **Settings → Secrets and variables → Actions → New repository secret**에 추가합니다. Secret 이름은 정확히 `DART_API_KEY`입니다.
2. **Settings → Actions → General → Workflow permissions**에서 `Read and write permissions`를 선택합니다.
3. **Settings → Pages → Build and deployment → Source**에서 `GitHub Actions`를 선택합니다.
4. **Actions → Update DART financial data → Run workflow**로 최초 수집을 시작합니다.
5. `Deploy GitHub Pages`가 성공하면 대시보드는 [여기](https://HSC-Class02.github.io/SE_Seegene/)에서 확인합니다. 저장소 소유자/이름이 다르거나 Pages 설정이 다르면 주소를 조정하세요.
6. 저장소 메인 페이지 오른쪽 **About → 톱니바퀴 → Website**에 대시보드 URL을 붙여 넣고 저장합니다.

## API 키 보안
- API 키를 코드나 파일에 직접 입력하지 말고 GitHub Actions Secret에만 저장하세요.
- 로컬에서 실행할 때는 환경변수 `DART_API_KEY`를 설정한 뒤 `python scripts/update.py`를 실행합니다.

## 수집/분석
- 시작 연도: 2010년
- 보고서: 사업보고서, 반기보고서, 분기보고서
- 매월 1일(한국시간 약 06:15) GitHub Actions 실행. GitHub cron은 UTC 기준이므로 매월 28~31일에 실행한 뒤 KST 날짜가 1일인 경우에만 수집합니다.
- OpenDART `list.json`, `fnlttSinglAcntAll.json`, `document.xml` API를 사용합니다. 씨젠의 RSS 주소는 사용하지 않습니다.
- 가능한 경우 공시 원문 ZIP을 `reports/raw/`에 보관합니다. 기본적으로 80MB 이하 파일만 저장하며 초과/실패 사유는 공시 메타데이터에 기록됩니다.
- 재무계정: 매출액, 매출원가/매출총이익, 영업이익, 법인세차감전순이익, 당기순이익, 자산, 현금, 매출채권, 재고자산, 유형자산, 부채, 차입금, 자본, 영업·투자·재무현금흐름, CAPEX 등.
- 계산 가능한 비율: 매출증가율, 매출총이익률, 영업이익률, 순이익률, 유동비율, 부채비율, 자기자본비율, ROA/ROE(기말 잔액 기준 근사치), CFO/순이익, FCF, 이자보상배율, 순차입금/EBITDA(필요 계정 확보 시).
- 당좌비율·ROIC·DSO/DIO/DPO/CCC와 PER/PBR/EV/EBITDA는 필요한 계정·평균잔액·시장가격이 부족하면 임의로 계산하지 않고 공란으로 둡니다.
- 연결(CFS)을 우선하고 자료가 없으면 별도(OFS)를 사용하며 행마다 기준을 표시합니다. 서로 다른 기준을 혼합 비교하지 마세요. 반기/분기 금액은 누적값일 수 있습니다.

## 국내 Peer Firms (비교 후보)
| 기업 | 종목코드 | 관련 사업 영역(요약) |
|---|---:|---|
| 에스디바이오센서 | 137310 | 체외진단·분자진단·신속진단 |
| 바이오니아 | 064550 | 분자진단·분자생물학 제품 |
| 랩지노믹스 | 084650 | 분자진단·유전체 분석 |
| 바디텍메드 | 206640 | 체외진단·면역진단 |
| 수젠텍 | 253840 | 체외진단·진단키트 |

위 기업은 사업 영역이 일부 겹치는 비교 후보이며, 모든 제품군에서 직접 경쟁한다는 의미는 아닙니다.

## 주요 파일
```text
.github/workflows/update.yml       # 월간 DART 수집/분석
.github/workflows/deploy-pages.yml # GitHub Pages 배포
src/dart_client.py                 # OpenDART API 클라이언트
src/analyzer.py                    # 계정 추출 및 비율 계산
scripts/update.py                  # 전체 업데이트 실행
config.yml                         # 기업/기간/원문 저장 옵션
reports/raw/                       # 원문 ZIP
reports/metadata/filings.json      # 공시 목록과 메타데이터
data/financials.json               # 전체 데이터
 data/latest.json                  # 대시보드 데이터
 dashboard/index.html              # 대시보드
```

## 오류 확인
`Actions`에서 실패한 workflow를 열고 로그를 확인하세요. `DART_API_KEY` 누락/오타, OpenDART 호출 제한, 저장소 쓰기 권한, Pages source 설정을 먼저 점검합니다. API 원문 안내: https://opendart.fss.or.kr/

requests>=2.31,<3
PyYAML>=6,<7
