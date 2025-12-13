import enum
from time import localtime
from datetime import datetime
from api.models.extra_models import SaveData
from constants import IN_DEV, LOG_PATH

class Status(enum.Enum):
    DEBUG = 0,
    OK = 1,
    WARNING = 2,
    ERROR = 3,

def statusToString(s: Status):
    if(s == Status.DEBUG):
        return "Debug"
    if(s == Status.OK):
        return "OK"
    if(s == Status.WARNING):
        return "Warning"
    if(s == Status.ERROR):
        return "Error"

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_path: str = LOG_PATH + f"{timestamp}.txt"
log_data = SaveData[str](log_path, "", False)
logging_level = Status.DEBUG if IN_DEV else Status.OK

def log(message: str, status: Status = Status.OK):
    if(int(status.value[0]) < int(logging_level.value[0])):
        return
    t = localtime()
    time = "[" + ("0" if t.tm_hour < 10 else "") + str(t.tm_hour) + ":" \
            + ("0" if t.tm_min < 10 else "") + str(t.tm_min) + ":" \
            + ("0" if t.tm_sec < 10 else "") + str(t.tm_sec) + "] " 


    fullMessage = time + statusToString(status) + ": " + message
    print(fullMessage, flush=True)
    log_data.data += fullMessage + "\n"
    log_data.save()
