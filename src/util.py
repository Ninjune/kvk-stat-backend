import enum
from time import localtime
from datetime import datetime
from api.models.extra_models import SaveData

class Status(enum.Enum):
    OK = "OK",
    ERROR = "Error",
    WARNING = "Warning"

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_path = f"logs/log_{timestamp}.txt"
log_data = SaveData[str](log_path, "", False)
def log(message: str, status: Status = Status.OK):
    t = localtime()
    time = "[" + ("0" if t.tm_hour < 10 else "") + str(t.tm_hour) + ":" \
            + ("0" if t.tm_min < 10 else "") + str(t.tm_min) + ":" \
            + ("0" if t.tm_sec < 10 else "") + str(t.tm_sec) + "] " 

    fullMessage = time + str(status.value[0]) + ": " + message
    print(fullMessage, flush=True)
    log_data.data += fullMessage + "\n"
    log_data.save()
