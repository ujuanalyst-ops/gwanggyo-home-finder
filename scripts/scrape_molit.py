import requests, time, os, sys, warnings
warnings.filterwarnings("ignore")
OUT = os.path.join(os.path.dirname(__file__), "molit")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36"
SGG = [("41","41117","경기도","수원시 영통구"),("41","41111","경기도","수원시 장안구"),("41","41113","경기도","수원시 권선구"),("41","41115","경기도","수원시 팔달구"),
       ("41","41465","경기도","용인시 수지구"),("41","41463","경기도","용인시 기흥구"),("41","41590","경기도","화성시"),("41","41370","경기도","오산시"),
       ("41","41220","경기도","평택시"),("11","11590","서울특별시","동작구")]
RANGES_SALE = [("2024-10-01","2025-09-30"),("2025-10-01","2026-09-25")]
RANGES_RENT = [("2025-10-01","2026-09-25")]
s = requests.Session(); s.headers.update({"User-Agent":UA})
s.get("https://rt.molit.go.kr/pt/xls/xls.do?mobileAt=", timeout=30)
def dl(kind, sido, sgg, sidoNm, sggNm, f, t, path):
    data = {"srhThingNo":"A","srhDelngSecd":kind,"srhAddrGbn":"1","srhLfstsSecd":"1","srhNewRonSecd":"","srhSidoCd":sido,"srhSggCd":sgg,"srhEmdCd":"","srhRoadNm":"","srhLoadCd":"","srhHsmpCd":"","srhArea":"","srhLrArea":"","srhFromDt":f,"srhToDt":t,"srhFromAmount":"","srhToAmount":"","sidoNm":sidoNm,"sggNm":sggNm,"emdNm":"전체","loadNm":"전체","areaNm":"전체","hsmpNm":"전체","mobileAt":""}
    for attempt in range(3):
        try:
            r = s.post("https://rt.molit.go.kr/pt/xls/ptXlsCSVDown.do", data=data, headers={"Referer":"https://rt.molit.go.kr/pt/xls/xls.do?mobileAt="}, timeout=180)
            if r.status_code==200 and len(r.content)>2000:
                open(path,"wb").write(r.content); print("ok",path,len(r.content),flush=True); return
            print("retry",path,r.status_code,len(r.content),flush=True)
        except Exception as e: print("err",path,e,flush=True)
        time.sleep(3)
for sido,sgg,sidoNm,sggNm in SGG:
    for f,t in RANGES_SALE: dl("1",sido,sgg,sidoNm,sggNm,f,t,os.path.join(OUT,f"sale_{sgg}_{f[:4]}.csv")); time.sleep(1.5)
    for f,t in RANGES_RENT: dl("2",sido,sgg,sidoNm,sggNm,f,t,os.path.join(OUT,f"rent_{sgg}_{f[:4]}.csv")); time.sleep(1.5)
print("DONE",flush=True)
