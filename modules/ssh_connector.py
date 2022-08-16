import sys
import pandas as pd
import pymysql
from sqlalchemy import create_engine
import mysql
import paramiko
from paramiko import SSHClient
from sshtunnel import SSHTunnelForwarder
from os.path import expanduser
import pymysql.cursors
import traceback
import mysql.connector
from dotenv import load_dotenv
from os import getenv

"""Author: tuomas karjalainen"""

def Connect(query1,df,table_name):
    """Function for SSH-connection."""
    try:
        ssh = paramiko.SSHClient()
        mypkey = ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # MariaDB-container
        sql_hostname = getenv("MARIADB_IP")
        sql_username = getenv("MARIADB_USER")
        sql_password = getenv("MARIADB_PASSWORD")
        sql_main_database = getenv("MARIADB_DATABASE")
        sql_port = int(getenv("MARIADB_PORT"))

        # Blade
        ssh_host = getenv("SSH_HOST")
        ssh_user = getenv("SSH_USER")
        ssh_port = int(getenv("SSH_PORT"))
        ssh_password = getenv("SSH_PASSWORD")

        print('\nConnection!')
    except Exception:
        print(traceback.format_exc())


    with SSHTunnelForwarder(
        (ssh_host, ssh_port),
        ssh_username=ssh_user,
        ssh_pkey=mypkey,
        ssh_password=ssh_password,
        remote_bind_address=(sql_hostname, sql_port)) as tunnel:
        conn = pymysql.connect(host='localhost', user=sql_username,
                passwd=sql_password, db=sql_main_database,
                port=tunnel.local_bind_port)
        
        mycursor = conn.cursor()
        
        engine = create_engine("mysql+pymysql://{user}:{password}@{host}:{port}/{db}".format(
         host='localhost',
         port=tunnel.local_bind_port,
         user=sql_username,
         password=sql_password,
         db=sql_main_database
        ))
        
        print(f"\nCreating table..")   
        mycursor.execute(query1)
        
        print(f"\nPushing data to database...\n\nDatabase: {sql_main_database}\nTable: {table_name}")
        df.to_sql(name=table_name, con=engine, if_exists='replace', index=False)
        
        print("\nDone!")
        
        conn.close()
if __name__ == '__main__':
    Connect()