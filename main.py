import aiohttp
import asyncio
import sys
import pprint
from datetime import datetime, timedelta

pure_url = "https://api.privatbank.ua/p24api/exchange_rates?date="

class HttpError(Exception):
    pass

async def request(url: str):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    raise HttpError(f"Error status {resp.status} for {url}")
        except (aiohttp.ClientConnectionError, aiohttp.InvalidURL) as err:
            raise HttpError(f"Connection error: {url}, {err}")

async def main(day_index):
    if int(day_index) > 10:
        print("to many days")
        day_index = input("enter days >>> ") 
    try:
        current_day = datetime.now()
        tasks = []
        for i in range(int(day_index)):
            date = current_day - timedelta(days=i)
            formatted_date = date.strftime("%d.%m.%Y")
            url = pure_url + formatted_date
            tasks.append(request(url))    
        return await asyncio.gather(*tasks)
    except HttpError as err:
        print(err)
        return None
    
def extract_rates_for_dates(data_list):
    result = []
    for data in data_list:
        date = data['date']
        rates = {}
        for rate in data['exchangeRate']:
            if rate['currency'] in ['EUR', 'USD']:
                rates[rate['currency']] = {
                    'sale': rate['saleRate'],
                    'purchase': rate['purchaseRate']
                }
       
        result.append({date: rates})
    return result


if __name__ == "__main__":
    res = asyncio.run(main(sys.argv[1]))
    result = extract_rates_for_dates(res)
    pprint.pprint(result)
    

    
    
