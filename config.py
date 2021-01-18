import os
import sys
import logging
import datetime

# Basic constants.
TOKEN = open("src/txt/TOKEN.txt", "r").read()
PREFIX = open("src/txt/PREFIX.txt", "r").read().rstrip()
DEBUG = True

# Users to ping on unexpected error:
USER_IDS = ("370964201478553600", "581141017823019038", "442713612822380554", "253227815338508289")
            # URL                 # Diatom              # Cirro               # Galoomba

# General config.
fileCount = 0

# Create log folder.
try:
    os.mkdir("logs")
except FileExistsError:
    pass

# Configures logger.
a_logger = logging.getLogger()
a_logger.setLevel(logging.INFO)
output_file_handler = logging.FileHandler("logs/log " +
    datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S") + ".txt", 'w', 'utf-8')
stdout_handler = logging.StreamHandler(sys.stdout)
a_logger.addHandler(output_file_handler)
a_logger.addHandler(stdout_handler)