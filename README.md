# 개요
JSESSION 로그인 후 메일 데이터 tailing


### 개발환경
Python 3.12, PyQt6, pyqttoast

```commandline
pyinstaller --onefile --windowed --add-data "src/ui;src/ui" --add-data "data;data" --add-data "assets;assets" src/app.py
```

### 필요기능
- JSESSION 로그인
- 메일 tailing + 팝업 알림
- 웹 띄우기

---
출처  
- 이미지 AI 생성
- CODEX 활용 (2026.10)