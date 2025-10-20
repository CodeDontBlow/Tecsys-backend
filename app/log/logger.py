import logging
import os

class Logger:
    def __init__(self):    
        self.level = logging.INFO
        self.filename = "descriptum.log"
        self.dir = "app/log"
        self.format =  "%(asctime)s - %(levelname)s - %(message)s"

    def config_logger(self):
        os.makedirs(self.dir, exist_ok=True)
        path = os.path.join(self.dir, self.filename)

        logging.basicConfig(
            filename=path,
            level=self.level,
            format=self.format,
            force=True,
            encoding="UTF-8",
            filemode="a" 
        )
        return logging.getLogger()
    
logger = Logger().config_logger()