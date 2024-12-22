from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from fastapi import Request
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

font_path = "/System/Library/Fonts/Supplemental/AppleGothic.ttf"
fontprop = fm.FontProperties(fname=font_path)

plt.rc('font', family=fontprop.get_name())



app = FastAPI()
templates = Jinja2Templates(directory="templates")
data = [
    {"date": "2023-01-01", "weight": 70.0, "exercise_time": 30.0, "calories": 2000.0},
    {"date": "2023-01-02", "weight": 69.5, "exercise_time": 45.0, "calories": 2100.0},
    {"date": "2023-01-03", "weight": 69.0, "exercise_time": 60.0, "calories": 2200.0},
]

class HealthData(BaseModel):
    date: str  
    weight: float
    exercise_time: float  
    calories: float  

@app.post("/add_data/")
async def add_health_data(item: HealthData):
    data.append(item.dict())
    return {"message": "데이터가 성공적으로 추가되었습니다!"}

@app.get("/summary/")
async def get_summary():
    if not data:
        raise HTTPException(status_code=404, detail="데이터가 없습니다")
    
    df = pd.DataFrame(data)
    return {
        "total_days": len(df),
        "average_weight": df["weight"].mean(),
        "average_exercise_time": df["exercise_time"].mean(),
        "average_calories": df["calories"].mean(),
    }

@app.get("/visualize/")
async def visualize_data():
    if not data:
        raise HTTPException(status_code=404, detail="데이터가 없습니다")
    
    df = pd.DataFrame(data)
    fig, ax = plt.subplots(3, 1, figsize=(8, 12))
    
    for i, (col, title, ylabel, color) in enumerate(zip(
        ["weight", "exercise_time", "calories"],
        ["체중 변화", "운동 시간 변화", "칼로리 변화"],
        ["체중 (kg)", "운동 시간 (분)", "칼로리 (kcal)"],
        ["blue", "green", "red"]
    )):
        ax[i].plot(df["date"], df[col], marker='o', label=title, color=color)
        ax[i].set_title(title)
        ax[i].set_xlabel("날짜")
        ax[i].set_ylabel(ylabel)
        ax[i].legend()
    
    plt.tight_layout()
    
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    buffer.close()
    
    return {"image": img_base64}
@app.get("/visualize_html/", response_class=HTMLResponse)
async def visualize_data_html(request: Request):
    if not data:
        raise HTTPException(status_code=404, detail="데이터가 없습니다")
    
    df = pd.DataFrame(data)
    fig, ax = plt.subplots(3, 1, figsize=(8, 12))
    
    for i, (col, title, ylabel, color) in enumerate(zip(
        ["weight", "exercise_time", "calories"],
        ["체중 변화", "운동 시간 변화", "칼로리 변화"],
        ["체중 (kg)", "운동 시간 (분)", "칼로리 (kcal)"],
        ["blue", "green", "red"]
    )):
        ax[i].plot(df["date"], df[col], marker='o', label=title, color=color)
        ax[i].set_title(title)
        ax[i].set_xlabel("날짜")
        ax[i].set_ylabel(ylabel)
        ax[i].legend()
    
    plt.tight_layout()
    
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    buffer.close()
    
    return templates.TemplateResponse("visualization.html", {"request": request, "image": img_base64})