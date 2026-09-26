# 광교 출근 집찾기

광교역(경기대) 앞으로 출근하는 5인 가족이 조건(예산·방 개수·출근시간·학군)을 넣으면 후보 아파트를 파랑(적합)·노랑(개선하면 가능)·빨강(부적합)으로 판정하는 단일 HTML 페이지입니다.

- 페이지: `index.html` (데이터 내장, 서버 불필요). GitHub Pages: https://ujuanalyst-ops.github.io/gwanggyo-home-finder/
- 데이터 기준일: 2026-09-25

## 데이터 출처
- 국토교통부 실거래가 공개시스템 (rt.molit.go.kr): 아파트 매매 2024-10~2026-09, 전월세 2025-10~2026-09. 수원 4구, 용인 수지·기흥, 화성 동탄구·병점구, 오산, 평택, 서울 동작구. 계약일 기준, 해제 건 제외.
- 직방 단지 검색 API: 단지 좌표·세대수·사용승인일.
- 네이버 부동산(모바일): 단지 목록·호가(일부 동만 수집됨).
- 학교: OpenStreetMap 학교 위치, 아파트미(apt2.me)가 집계한 학교알리미 중학교 성취도(2025 1학기 2학년 국·영·수 A~E 비율)와 특목·자사고 진학률. 배정은 근거리 기준 예측(같은 시 우선, 4km 내 3개 후보), 등급은 경기 남부 191개교 백분위.
- 행정안전부 행정동 경계(vuski/admdongkor, 2026-07), OpenStreetMap 도로·철도·수계.

## 구성
- `index.html`: 페이지 본문, `data.js`(단지·실거래)와 `mapdata.js`(지도 레이어)를 로드
- `scripts/`: 수집·병합·빌드 스크립트 (`scrape_molit.py` → `geocode_zigbang.py`/`geocode_pass2.py` → `build_data.py` → `process_map.py` → `patch_map.py` → `page_build.py`)
- `data/complexes.json`: 병합된 단지 데이터, `data/schools.json`: 중학교 성취도·등급과 단지별 배정 예측, `data/mapdata.js`: 지도 벡터 레이어

## 주의
의사결정 보조 도구이며 투자 자문이 아닙니다. 시세·규제·세금·학교 배정은 변동되므로 계약 전 원본 자료와 전문가 확인이 필요합니다. 출근시간·교육 등급은 분석가 추정값입니다.
