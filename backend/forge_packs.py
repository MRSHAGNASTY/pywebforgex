
from __future__ import annotations
from pathlib import Path


PACKS = {
  "fastapi-app": {
    "main.py": "from fastapi import FastAPI
app=FastAPI()
@app.get('/')
def hi(): return {'ok':True}
",
    "requirements.txt": "fastapi
uvicorn
"
  },
  "streamlit-app": {
    "app.py": "import streamlit as st
st.title('Hello from Streamlit')
st.write('It works!')
",
    "requirements.txt": "streamlit
"
  },
  "cli-tool": {
    "tool.py": "#!/usr/bin/env python3
import argparse
p=argparse.ArgumentParser();p.add_argument('--echo');print(p.parse_args().echo)
"
  },
  "etl-skeleton": {
    "etl.py": "def extract(): return [1,2]

def transform(rows): return [r*2 for r in rows]

def load(rows): return len(rows)

def run():
    data = extract(); data = transform(data); return load(data)
"
  },
  "web-scraper": {
    "scraper.py": "def fetch(url:str):
    import urllib.request
    return urllib.request.urlopen(url, timeout=5).read()[:200].decode('utf-8','ignore')
"
  },
  "langchain-agent": {
    "agent.py": "# Minimal skeleton; requires API keys
from typing import List

def run_agent(prompt: str, tools: List[str]|None=None):
    # TODO: wire LangChain constructs, models, and tools
    # placeholder logic returns echo for offline demo
    return {'answer': f'Agent echo: {prompt}', 'tools': tools or []}
",
    "requirements.txt": "langchain
openai
"
  },
  "db-etl-sqlalchemy": {
    "etl_db.py": "from sqlalchemy import create_engine, text

def init(db='sqlite:///data.db'):
    e = create_engine(db)
    with e.begin() as c:
        c.execute(text('CREATE TABLE IF NOT EXISTS items(id INTEGER PRIMARY KEY, v INTEGER)'))
    return str(e.url)

def load(values, db='sqlite:///data.db'):
    e = create_engine(db)
    with e.begin() as c:
        for v in values:
            c.execute(text('INSERT INTO items(v) VALUES(:v)'), {'v': v})
    return len(values)
",
    "requirements.txt": "SQLAlchemy
"
  },
  "celery-worker": {
    "celery_app.py": "from celery import Celery
app = Celery('omega', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')
@app.task
def add(x, y): return x+y
",
    "requirements.txt": "celery
redis
",
    "README.md": "Run worker: celery -A celery_app.app worker --loglevel=INFO
"
  },
  "airflow-dag": {
    "dags/sample_dag.py": "from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator

def hello(): print('hello')

dag = DAG('sample', start_date=datetime(2023,1,1), schedule='@daily', catchup=False)
PythonOperator(task_id='say_hi', python_callable=hello, dag=dag)
",
    "README.md": "Place this folder inside an Airflow DAGs directory. Installing Airflow is out-of-scope for the runtime demo.
"
  }
}
\n",
    "requirements.txt": "fastapi\nuvicorn\n"
  },
  "streamlit-app": {
    "app.py": "import streamlit as st\nst.title('Hello from Streamlit')\nst.write('It works!')\n",
    "requirements.txt": "streamlit\n"
  },
  "cli-tool": {
    "tool.py": "#!/usr/bin/env python3\nimport argparse\nparser=argparse.ArgumentParser();parser.add_argument('--echo');print(parser.parse_args().echo)\n"
  },
  "etl-skeleton": {
    "etl.py": "def extract(): return [1,2]\n\ndef transform(rows): return [r*2 for r in rows]\n\ndef load(rows): return len(rows)\n\ndef run():\n    data = extract(); data = transform(data); return load(data)\n"
  },
  "web-scraper": {
    "scraper.py": "def fetch(url:str):\n    import urllib.request\n    return urllib.request.urlopen(url, timeout=5).read()[:200].decode('utf-8','ignore')\n"
  }
}

def materialize(dest: Path, pack: str, name: str):
    dest = Path(dest)/name
    dest.mkdir(parents=True, exist_ok=True)
    tpl = PACKS.get(pack) or {}
    for rel, content in tpl.items():
        p = dest/rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding='utf-8')
    return {"ok": True, "path": str(dest), "files": len(tpl)}
