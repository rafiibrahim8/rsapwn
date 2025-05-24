import logging


class ColoredFormatter(logging.Formatter):
    """A colorful formatter for logging module."""

    def __init__(self, *args, **kwargs):
        """Initialize a new ColoredFormatter instance."""
        super(ColoredFormatter, self).__init__(*args, **kwargs)
        self._colors = {
            "WARNING": "\033[93m",
            "INFO": "\033[94m",
            "DEBUG": "\033[92m",
            "CRITICAL": "\033[91m",
            "ERROR": "\033[91m",
        }
        self._reset = "\033[0m"

    def format(self, record):
        """Format the specified record as text."""
        levelname = record.levelname
        if levelname in self._colors:
            levelname_color = self._colors[levelname] + levelname + self._reset
            record.levelname = levelname_color
        return super(ColoredFormatter, self).format(record)


def init_logger(name, level):
    logger = logging.getLogger(name)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(ColoredFormatter("%(levelname)s: %(message)s"))
    logger.addHandler(console_handler)
    logger.setLevel(level)
    return logger
