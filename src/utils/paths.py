import sys
import os
from pathlib import Path

if getattr(sys, "frozen", False):
    # .exe 앱실행 임시 폴더
    PROJECT_ROOT = Path(sys._MEIPASS)
else:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

BASE_DIR = PROJECT_ROOT / "src"
