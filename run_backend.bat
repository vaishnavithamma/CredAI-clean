@echo off
call conda activate credai
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload > uvicorn.log 2>&1
