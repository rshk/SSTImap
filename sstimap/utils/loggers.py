import logging
import sys
import logging.handlers

SUCCESS = 21
FAIL = 22
MAJOR = 23
POSITIVE = 24
NEGATIVE = 25
MINOR = 26


log = None
logfile = None
logging.addLevelName(SUCCESS, "SUCCESS")
logging.addLevelName(FAIL, "FAIL")
logging.addLevelName(MAJOR, "MAJOR")
logging.addLevelName(POSITIVE, "POSITIVE")
logging.addLevelName(NEGATIVE, "NEGATIVE")
logging.addLevelName(MINOR, "MINOR")


def no_colour(s):
    import re

    esc = re.compile(r"""\033\[\d+m""", re.VERBOSE)
    esc_url = re.compile(r"""\033]8;;(.+?)\007(.+?)\033]8;;\007""", re.VERBOSE)
    s = esc.sub("", s)
    s = esc_url.sub(r"\2 (\1)", s)
    return s


class SSTImapFormatter(logging.Formatter):
    style = "{"
    colour = True
    FORMATS = {
        logging.DEBUG: "\033[94m[D]\033[0m [\033[4m{module}\033[0m] {message}",
        logging.INFO: "\033[94m[!]\033[0m {message}",
        logging.WARNING: "\033[93m[*]\033[0m [\033[4m{module}\033[0m] {message}",
        SUCCESS: "\033[92m[+]\033[0m {message}",
        FAIL: "\033[91m[-]\033[0m {message}",
        MAJOR: "\033[94m[*]\033[0m {message}",
        POSITIVE: "\033[32m[+]\033[0m {message}",
        NEGATIVE: "\033[31m[-]\033[0m {message}",
        MINOR: "\033[34m[*]\033[0m {message}",
        27: "\033[93m[*]\033[0m {message}",
        28: "\033[33m[*]\033[0m {message}",
        29: "\033[33m[!]\033[0m {message}",
        logging.ERROR: "\033[91m[-]\033 [0m[\033[4m{module}\033[0m] {message}",
        logging.CRITICAL: "\033[91m[!]\033[0m [\033[4m{module}\033[0m] {message}",
        "DEFAULT": "\033[91m[{levelname}]\033[0m {message}",
    }

    def __init__(self):
        super().__init__(style="{")

    def format(self, record):
        super().__init__(
            self.FORMATS.get(record.levelno, self.FORMATS["DEFAULT"]), style="{"
        )
        res = logging.Formatter.format(self, record)
        if not self.colour:
            res = no_colour(res)
        return res


def setup_logging(logfile: str | None = None):
    formatter = SSTImapFormatter()

    stream_handler = logging.StreamHandler(stream=sys.stdout)
    stream_handler.setFormatter(formatter)

    log = logging.getLogger("log")
    log.propagate = False
    log.addHandler(stream_handler)
    log.setLevel(logging.DEBUG)
    stream_handler.setLevel(logging.INFO)

    dlog = logging.getLogger("dlog")
    dlog.propagate = False
    dlog.setLevel(logging.INFO)

    if logfile is not None:
        file_handler = logging.handlers.RotatingFileHandler(
            logfile,
            mode="a",
            maxBytes=5 * 1024 * 1024,
            backupCount=2,
            encoding=None,
            delay=False,
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        log.addHandler(file_handler)
        dlog.addHandler(file_handler)


setup_logging()
