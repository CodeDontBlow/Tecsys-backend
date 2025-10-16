import logging
import os

def setup_logger():
    log_level = logging.INFO
    log_filename = "descriptum.log"
    log_dir = "app/log"
    log_format = "%(asctime)s - %(levelname)s - %(message)s"

    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, log_filename)

    logging.basicConfig(
        filename=log_path,
        level=log_level,
        format=log_format,
        force=True,
        encoding="UTF-8" ,
        filemode="a" 
    )
    return logging.getLogger()