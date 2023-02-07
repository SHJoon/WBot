from dotenv import load_dotenv
load_dotenv()

import os
import asyncio

from supabase import create_client

def load_db():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    supabase = create_client(url, key)

    return supabase


if __name__ == "__main__":
    load_db()