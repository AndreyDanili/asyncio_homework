import asyncio
import aiohttp
import asyncpg
from more_itertools import chunked

import config


async def get_people(session, people_id):
    async with session.get(f'https://swapi.dev/api/people/{people_id}') as response:
        json_data = await response.json()
        return json_data


async def insert_users(pool: asyncpg.Pool, user_list):
    query = 'INSERT INTO swapi (' \
            'birth_year, ' \
            'eye_color, ' \
            'films, ' \
            'gender, ' \
            'hair_color, ' \
            'height, ' \
            'homeworld, ' \
            'mass, ' \
            'name, ' \
            'skin_color, ' \
            'species, ' \
            'starships, ' \
            'vehicles' \
            ') VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)'
    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.executemany(query, user_list)


async def main():
    pool = await asyncpg.create_pool(config.PG_DSN, min_size=20, max_size=20)
    async with aiohttp.ClientSession() as session:
        coroutines = (get_people(session, i) for i in range(1, 100))
        for users_chunk in chunked(coroutines, 30):
            result = await asyncio.gather(*users_chunk)
            users_list = list(((
                                i['birth_year'],
                                i['eye_color'],
                                ", ".join(i['films']),
                                i['gender'],
                                i['hair_color'],
                                i['height'],
                                i['homeworld'],
                                i['mass'],
                                i['name'],
                                i['skin_color'],
                                ", ".join(i['species']),
                                ", ".join(i['starships']),
                                ", ".join(i['vehicles'])
                                ) for i in result if 'name' in i))
            asyncio.create_task(insert_users(pool, users_list))
            
    print()
    print("#############<Import people success!>#############")
    print()

    await pool.close()


if __name__ == '__main__':
    asyncio.run(main())
    input()
