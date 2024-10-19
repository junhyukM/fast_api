from fastapi import FastAPI
from pydantic import BaseModel
import requests
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI() 

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 출처 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

db = []

class City(BaseModel):
    name: str
    timezone: str

@app.get("/")
def root():
    return("hell ya")


@app.get('/cities') 
async def get_cities():
    results = []
    async with httpx.AsyncClient() as client:
        for city in db:
            strs = f"http://worldtimeapi.org/api/timezone/{city['timezone']}"
            try:
                r = await client.get(strs)
                r.raise_for_status()  # HTTP 오류가 발생하면 예외 발생
                cur_time = r.json().get('datetime', 'N/A')
            except httpx.HTTPStatusError as e:
                cur_time = f"Error: {str(e)}"  # 에러 메시지

            results.append({'name': city['name'], 'timezone': city['timezone'], 'current_time': cur_time})

    return results

@app.get('/cities/{city_id}') 
async def get_city(city_id: int):
    city = db[city_id-1]
    strs = f"http://worldtimeapi.org/api/timezone/{city['timezone']}"
    
    async with httpx.AsyncClient() as client:
        r = await client.get(strs)
        cur_time = r.json().get('datetime', 'N/A')

    return {'name': city['name'], 'timezone': city['timezone'], 'current_time': cur_time}

@app.post('/cities') 
def create_city(city: City):
    db.append(city.dict())

    return db[-1]

@app.delete('/cities/{city_id}') 
def delete_city(city_id: int):
    db.pop(city_id -1)

    return {}