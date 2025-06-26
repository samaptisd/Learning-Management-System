import pandas as pd
import pymysql
import os
import django
from django.conf import settings
from django.contrib.auth.hashers import make_password

def setup_django():
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SMS.settings')  #
        django.setup()  
        print("Django settings configured successfully.")
    except Exception as e:
        print(f"Error during Django setup: {e}")
        raise

def import_csv_to_mysql(csv_file_path):
    try:
        setup_django()

        connection = pymysql.connect(
            host='localhost',        
            user='root',  
            password='',
            database='elearn'        
        )

        if connection:
            print("Connected to MySQL database")

            data = pd.read_csv(csv_file_path)

            cursor = connection.cursor()

            sql = """INSERT INTO accounts_user (
                        id, password, last_login, is_superuser, username, first_name, last_name, is_staff,
                        is_active, date_joined, is_student, is_lecturer, phone, picture, email, 
                        is_dep_head, zone, branch, date_of_join_in_aludecor, department, reporting_to
                     ) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            
            for index, row in data.iterrows():
                row = row.where(pd.notnull(row), None)  

                hashed_password = make_password(row['password']) if row['password'] is not None else None
                
                values = (
                    row['id'], hashed_password, row['last_login'], row['is_superuser'], row['username'], 
                    row['first_name'], row['last_name'], row['is_staff'], row['is_active'], row['date_joined'], 
                    row['is_student'], row['is_lecturer'], row['phone'], row['picture'], row['email'], 
                    row['is_dep_head'], row['zone'], row['branch'], row['date_of_join_in_aludecor'], 
                    row['department'], row['reporting_to']
                )



                cursor.execute(sql, values)
            
            connection.commit()

            print("CSV data imported successfully into the accounts_user table")

    except Exception as e:
        print(f"Error: {e}")
        connection.rollback()  

    finally:
        if connection:
            cursor.close()
            connection.close()
            print("MySQL connection is closed")


csv_file_path = 'accounts_user.csv' 
import_csv_to_mysql(csv_file_path)




################################################################## Quiz_Quiz #################################################




