import asyncio
import sys

sys.path.append(".")

from tests.test_methods import clear_db


async def main():
    await clear_db()


if __name__ == "__main__":
    asyncio.run(main())
