from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.environ.get("API_KEY")
debug_mode_str = os.environ.get("DEBUG_MODE", "False")

debug_mode = debug_mode_str.lower() == "true"

print(f"API_KEY: {api_key}")
print(f"DEBUG_MODE: {debug_mode}")

if debug_mode:
    print("Приложение запущено в режиме отладки")
else:
    print("Приложение запущено в обычном режиме")
