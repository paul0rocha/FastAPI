from typing import Union
import httpx
from fastapi import FastAPI,HTTPException
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None


async def get_exchange_rate():
    url = "https://v6.exchangerate-api.com/v6/f57e2c889fb78a82507ac13d/latest/USD"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()


@app.get("/")
async def read_api():
    exchange_rate_data = await get_exchange_rate()
    return exchange_rate_data


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}

@app.post("/thingspeak/write/{field_value}")
async def data(field_value: int):
    data = await post_write_data(field_value)
    return data

async def post_write_data(field_value: int):
    url = f"https://api.thingspeak.com/update?api_key=WJPE65B0OQBNRXXV"
    json_payload = {"field1": field_value}

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=json_payload)

    if response.status_code == 200:
        return {"status code":response.status_code, "response": response.json()}
    else:
        raise HTTPException(status_code=response.status_code, detail="Failed to write data to ThingSpeak")



class ThingSpeakData(BaseModel):
    field1: int
    field2: int
    field3: int

@app.post("/thingspeak/writes")
async def write_to_thingspeak(data: ThingSpeakData):
    field1_value = data.field1
    field2_value = data.field2
    field3_value = data.field3

    result = await post_write_data(field1_value, field2_value, field3_value)
    return result


async def post_write_data(field1_value: int, field2_value: int, field3_value: int):
    url = f"https://api.thingspeak.com/update?api_key=WJPE65B0OQBNRXXV"
    json_payload = {
        "field1": field1_value,
        "field2": field2_value,
        "field3": field3_value
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=json_payload)

    if response.status_code == 200:
        return {
            "status_code": response.status_code,
            "Input Values": {
                "field1": field1_value,
                "field2": field2_value,
                "field3": field3_value
            },
            "response": response.json()
        }
    else:
        raise HTTPException(status_code=response.status_code, detail="Failed to write data to ThingSpeak")



class ThingSpeakDatas(BaseModel):
    field1: int

@app.post("/thingspeak/write")
async def write_to_thingspeaks(data: ThingSpeakDatas):
    field1_value = data.field1

    result = await post_write_datas(field1_value)
    return result

async def post_write_datas(field1_value: int):
    url = f"https://api.thingspeak.com/update?api_key=WJPE65B0OQBNRXXV"
    json_payload = {
        "field1": field1_value
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=json_payload)

    if response.status_code == 200:
        return {
            "status_code": response.status_code,
            "Input Values": {
                "field1": field1_value
            },
            "response": response.json()
        }
    else:
        raise HTTPException(status_code=response.status_code, detail="Failed to write data to ThingSpeak")
