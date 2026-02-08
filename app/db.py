import os
from supabase import create_client

supabase = None

def get_supabase():
    global supabase
    if supabase is not None:
        return supabase

    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError("Supabase credentials not found in environment")

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    return supabase
