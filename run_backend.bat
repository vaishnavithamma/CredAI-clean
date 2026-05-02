@echo off
call conda activate credai
uvicorn backend.main:app --reload --port 8000 > uvicorn.log 2>&1
