import logging
from typing import Optional


class LogManager:
    """
    A class to handle logging to a file and logging messages.

    Args:
        filename (str): The name of the filename where logs are written.
    """

    def __init__(self, filename: Optional[str] = 'logs.log') -> None:
        self.filename = filename if filename else 'logs.log'
        logging.basicConfig(filename=self.filename,
                            format='%(levelname)s:%(message)s')
        self.logger = logging.getLogger(__name__)

    def log(self, message: str) -> None:
        """
        Logs a message to the file `self.filename`.

        Args:
            message (str): The message to log.
        Returns:
            None
        """
        self.logger.warning(message)
