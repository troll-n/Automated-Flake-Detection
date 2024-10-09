import argparse
import json
import os

FILE_DIR = os.path.dirname(os.path.abspath(__file__))

for file in os.listdir(FILE_DIR):
    filename = os.fsdecode(file)
