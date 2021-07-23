"""
Common definitions for logging
"""

import contextlib
import datetime
import logging
import logging.handlers
import pathlib
import sys

_LOG_DIRECTORY = pathlib.Path("/var") / "log" / "128T-provisioner"
_MAX_LOGFILE_BYTES = 2 ** 20
_MAX_LOGFILE_BACKUPS = 20

# Longest builtin level is "CRITICAL" of length 8
_DEFAULT_FORMATTER = logging.Formatter(
    "{asctime} - {levelname:<8} [{name}] {message}", style="{"
)
_CONSOLE_FORMATTER = logging.Formatter("{levelname:<8} - {message}", style="{")

_EXTERNAL_LOG_LEVEL = logging.WARNING

_AUDIT_LOG_NAME = "audit"
_AUDIT_FILE_TEMPLATE = r"provisioner_%Y-%m-%dT%H%M%S%z.log"
_AUDIT_LOG_LEVEL = logging.INFO


def initialize(name, level, console_level=logging.INFO):
    """
    Initialize logging for a script or application.

    This function should be called once per application, after which individual
    modules can use logging.getLogger(__name__) to get a logger with which they
    can log to default handlers.

    Args:
        name (str): The logger name to initialize

        level (int): The log file level, one of:
            - logging.CRITICAL
            - logging.ERROR
            - logging.WARNING
            - logging.INFO
            - logging.DEBUG

        console_level (int | None): The log level to print to console.
            Can be None to disable console logging, or one of the allowed log
            levels as for the `level` parameter.

    Raises:
        OSError: For any file system failures
    """

    logger = logging.getLogger()
    logger.setLevel(level)

    if not logger.hasHandlers():
        _LOG_DIRECTORY.mkdir(parents=True, exist_ok=True)

        log_file_path = _LOG_DIRECTORY / f"{name}.log"
        file_handler = _create_file_handler(level, log_file_path)
        logger.addHandler(file_handler)

        if console_level:
            console_handler = _create_console_handler(console_level)
            logger.addHandler(console_handler)

    _initialize_audit_logger()


def audit(logger, msg, *args, level=logging.INFO, log_to_root=True):
    """
    Log something at INFO level to the audit log.

    Args:
        logger (logging.Logger): The logger from which the audit log originates

        msg (str): The message to log in the audit log.

        *args: Remaining args forwarded to `logging.info()`

        level (int): The level to log at, one of:
            - logging.CRITICAL
            - logging.ERROR
            - logging.WARNING
            - logging.INFO
            - logging.DEBUG

        log_to_root (bool): If True (the default), the message will be logged
            to audit and the main logger. Otherwise only the audit log will
            receive the message.
    """
    audit_logger = logging.getLogger(_AUDIT_LOG_NAME)

    with _logging_propagation(audit_logger, propagate=log_to_root):
        audit_logger.getChild(logger.name).log(level, msg, *args)


@contextlib.contextmanager
def _logging_propagation(logger, *, propagate):
    previous_propagation = logger.propagate
    try:
        logger.propagate = propagate
        yield
    finally:
        logger.propagate = previous_propagation


def _initialize_audit_logger():
    audit_logger = logging.getLogger(_AUDIT_LOG_NAME)
    audit_logger.setLevel(_AUDIT_LOG_LEVEL)
    # Avoid logging to the root application logger by default
    audit_logger.propagate = False

    if not audit_logger.hasHandlers():
        audit_path = (
            _LOG_DIRECTORY
            / _AUDIT_LOG_NAME
            / datetime.datetime.now().strftime(_AUDIT_FILE_TEMPLATE)
        )
        audit_path.parent.mkdir(parents=True, exist_ok=True)

        # Use a non-rotating FileHandler since we timestamp the filename
        audit_file_handler = logging.FileHandler(audit_path)
        audit_file_handler.setLevel(_AUDIT_LOG_LEVEL)
        audit_file_handler.setFormatter(_DEFAULT_FORMATTER)
        audit_logger.addHandler(audit_file_handler)


def _create_file_handler(level, file_path):
    existed = file_path.exists()

    file_handler = logging.handlers.RotatingFileHandler(
        file_path, maxBytes=_MAX_LOGFILE_BYTES, backupCount=_MAX_LOGFILE_BACKUPS
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(_DEFAULT_FORMATTER)
    file_handler.namer = lambda name: str(_swap_suffixes(name))

    if existed:
        file_handler.doRollover()

    return file_handler


def _swap_suffixes(old_name):
    old_path = pathlib.Path(old_name)
    new_suffix = "".join(reversed(old_path.suffixes))
    # Call .with_suffix("") twice to remove both suffixes
    return old_path.with_suffix("").with_suffix("").with_suffix(new_suffix)


def _create_console_handler(level):
    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(_CONSOLE_FORMATTER)
    return console_handler


def create_log_context(entry_id, message):
    """
    Appends log context with entry ID to message

    Args:
        entry_id (str): The entry ID

        message (str): The log message

    Returns:
        str: The log message with log context
    """
    return " ".join([message, "{", entry_id, "}"])
