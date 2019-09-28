import os
import time

print(__name__)
print(__file__)
print(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(__file__)
print(BASE_DIR)
UPLOAD_DIR = os.path.join(BASE_DIR,'static/upload')

print(UPLOAD_DIR)
print(time.time())