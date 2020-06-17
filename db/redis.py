import asyncio
import aioredis

class RedisDB():
    
    @classmethod
    async def create(cls, redis_host: str = "localhost", port: str = "6379", db: str = "0", username: str = None, password: str = None):
        # Initialize a connection pool upon creation of the instance
        self = RedisDB()
        self.host = redis_host
        self.port = port
        self.db = db
        self.username = username
        self.password = password
        self.pool = await self.create_pool()
        return self

    async def create_pool(self):
        # Create a redis pool connection
        auth_string = f'redis://{self.username}:' if self.username else 'redis://:'
        auth_string = auth_string + (f'{self.password}' if self.password else '')
        auth_string = auth_string + f'@{self.host}:{self.port}/{self.db}'
        return await aioredis.create_redis_pool(auth_string)


    async def close(self):
        # Close the connection pool and set to None.
        if self.pool is not None:
            self.pool.close()
            await self.pool.wait_closed()
            self.pool = None
        return

    
    async def get_connection(self):
        # Return an individual redis connection
        if self.pool is None:
            self.pool = await self.create_pool()
        return self.pool
    

    async def get(self, key: str):
        # Get a value associated with a key in Redis
        conn = await self.get_connection()
        response = await conn.get(key)
        if response is not None:
            return response.decode('utf-8')
        else:
            return response

    
    async def set(self, key: str, val: str, expire: int = 0):
        # Set a key / value pair in Redis
        conn = await self.get_connection()
        await conn.set(key, val, expire=expire)
        

    async def delete(self, key: str):
        # Delete a key from Redis
        conn = await self.get_connection()
        await conn.delete(key)

