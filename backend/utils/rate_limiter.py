import time
from collections import deque

REQUEST_LIMIT = 15
TIME_WINDOW = 60  # seconds
request_times = deque()

def enforce_rate_limit():
    current_time = time.time()
    while request_times and current_time - request_times[0] > TIME_WINDOW:
        request_times.popleft()
    if len(request_times) >= REQUEST_LIMIT:
        wait_time = TIME_WINDOW - (current_time - request_times[0])
        print(f"⏳ Waiting {wait_time:.2f}s to respect Gemini rate limit...")
        time.sleep(wait_time)
        enforce_rate_limit()
    request_times.append(time.time())
