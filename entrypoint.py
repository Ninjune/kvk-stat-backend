import os

use_flask = os.getenv("USE_FLASK", "").lower() in ("true", "1", "yes")

if use_flask:
    print("Starting Flask development server...")
    os.chdir("src")
    os.execvp("python", ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=80"])
else:
    print("Starting Gunicorn production server...")
    os.execvp("gunicorn", ["gunicorn", "-b", "0.0.0.0:80", "--chdir", "src", "app:app"])
