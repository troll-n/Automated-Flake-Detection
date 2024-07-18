"""
Author: Patrick Kaczmarek
General server-related testing things
"""
import argparse
import json
import os

import cv2
import numpy as np

from demo.demo_functions import visualise_flakes
from GMMDetector import MaterialDetector
from GMMDetector.structures import Flake 

import time

from mysql.connector import Error, connect
from getpass import getpass

"""
Connect to the MySQL server.
Create a new database.
Connect to the newly created or an existing database.
Execute a SQL query and fetch results.
Inform the database if any changes are made to a table.
Close the connection to the MySQL server.
"""

#from a array containing falkes, I can strip things
# this is not implemented here shrimply because i leave in 5


"""
tables: chip & flake, as described elsewhere
"""
insert_chip_query = """
INSERT INTO chips (material, size)
VALUES 
    ('Graphene','25'),
    ('Graphene','10'),
    ('Graphene','3'),
    ('Graphene','2')
;
"""
insert_flake_query = """
INSERT INTO flakes (chip_id, flake_id, size)
VALUES 
    (%s,%s,%s)
"""
chip_id = 2
flakeSizeList = [200,300,123,491,2390]
flakes = []
flake_id = 1
for fs in flakeSizeList:
    flakes.append(
        (chip_id, flake_id, fs)
    )
    flake_id = flake_id + 1

try:
    with connect(
        host="localhost",
        user=input("Enter username: "),
        password=getpass("Enter password: "),
        database = "test_db",
    ) as connection:
        with connection.cursor() as cursor:
            cursor.executemany(insert_flake_query, flakes)
            connection.commit()
except Error as e:
    print(e)