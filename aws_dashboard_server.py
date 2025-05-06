from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
import uvicorn
import shutil
import os
from typing import List, Dict, Any
import re
from pathlib import Path
import time
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
from pydantic import BaseModel
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

app = FastAPI()

# CORS 설정
ALLOWED_ORIGINS = [
    "http://localhost:3000",  # 개발 환경
    "https://dashboard-html-chi.vercel.app",  # Vercel 배포 프론트엔드
    "https://dashboard-server-8neo.onrender.com"  # Render 배포 백엔드
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# MySQL 데이터베이스 연결 설정 - 환경 변수에서 로드
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# SQLAlchemy 엔진 생성
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)

# DB 연결 테스트 함수
def test_db_connection():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            return True
    except SQLAlchemyError as e:
        print(f"데이터베이스 연결 오류: {e}")
        return False

# --- MySQL 데이터 조회 API 엔드포인트 ---
@app.get("/db/ques")
def get_ques_data():
    try:
        if not test_db_connection():
            return {"error": "데이터베이스 연결에 실패했습니다."}
        
        query = "SELECT * FROM ques ORDER BY id DESC LIMIT 100"
        df = pd.read_sql(query, engine)
        
        # 날짜/시간 포맷 변환
        if 'created_at' in df.columns:
            df['created_at'] = df['created_at'].astype(str)
            
        return df.to_dict(orient="records")
    except Exception as e:
        return {"error": f"데이터 조회 중 오류 발생: {str(e)}"}

@app.get("/db/uastatus")
def get_uastatus_data():
    try:
        if not test_db_connection():
            return {"error": "데이터베이스 연결에 실패했습니다."}
        
        query = "SELECT * FROM uastatus LIMIT 1000"
        df = pd.read_sql(query, engine)
        
        return df.to_dict(orient="records")
    except Exception as e:
        return {"error": f"데이터 조회 중 오류 발생: {str(e)}"}

@app.get("/db/agent_conid")
def get_agent_conid_data():
    try:
        if not test_db_connection():
            return {"error": "데이터베이스 연결에 실패했습니다."}
        
        query = "SELECT * FROM agent_conID LIMIT 100"
        df = pd.read_sql(query, engine)
        
        return df.to_dict(orient="records")
    except Exception as e:
        return {"error": f"데이터 조회 중 오류 발생: {str(e)}"}

# 모든 테이블 데이터를 한 번에 조회하는 API
@app.get("/db/all_data")
def get_all_data():
    try:
        if not test_db_connection():
            return {"error": "데이터베이스 연결에 실패했습니다."}
        
        result = {}
        
        # ques 테이블 조회
        ques_query = "SELECT * FROM ques ORDER BY id DESC LIMIT 100"
        ques_df = pd.read_sql(ques_query, engine)
        if 'created_at' in ques_df.columns:
            ques_df['created_at'] = ques_df['created_at'].astype(str)
        result["ques"] = ques_df.to_dict(orient="records")
        
        # uastatus 테이블 조회
        ua_query = "SELECT * FROM uastatus LIMIT 1000"
        ua_df = pd.read_sql(ua_query, engine)
        
        result["uastatus"] = ua_df.to_dict(orient="records")
        
        # agent_conid 테이블 조회
        try:
            agent_query = "SELECT * FROM agent_conID LIMIT 100"
            agent_df = pd.read_sql(agent_query, engine)
            result["agent_conID"] = agent_df.to_dict(orient="records")
        except Exception as e:
            result["agent_conID"] = {"error": f"데이터 조회 중 오류 발생: {str(e)}"}
        
        return result
    except Exception as e:
        return {"error": f"데이터 조회 중 오류 발생: {str(e)}"}

# --- FastAPI 서버 실행 부분 ---
if __name__ == "__main__":
    uvicorn.run("aws_dashboard_server:app", host="0.0.0.0", port=8000, reload=True)