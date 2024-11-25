from datetime import datetime, timedelta
import subprocess
import pymysql
import os
import pytz

db_host = 'localhost'
# db_host = '148.113.1.101'
db_user = 'root'
db_password = 'actowiz'
db_port = 3306
db_name = 'swg'
db_links_table = 'input'
db_data_table = None

delivery_date = str(datetime.today().strftime("%Y%m%d"))

network_drive_path = r"\\172.27.132.84\D"  # Network drive path with ip and Drive name
drive_letter = "W:"  # Drive letter you want to use for network drive
username = "actowiz"  # username of KVM
password = "actowiz123"  # password of KVM


# FOR TODAY's - 1  Date
# delivery_date = (datetime.today() + timedelta(days=1)).strftime("%Y%m%d")


# Function to return page save path
def dynamic_drive(store):
    if 'W:\\' not in os.listdrives():
        # print(os.listdrives())
        # Running command to connect Network drive if not connected
        try:
            subprocess.run(args=["net", "use", drive_letter, network_drive_path, "/user:" + username, password],
                           shell=True)
            print('Network Drive Reconnected...!')
        except Exception as e:
            print('Error while Reconnecting Network Drive...', e)

    page_save_path = fr'W:/QC_page_saves/{delivery_date}/{store}'  # Creating page_save_path name
    os.makedirs(page_save_path, exist_ok=True)  # Creating page_save_path if not exists
    return page_save_path  # Return page_save_path

# For testing Database connection
# if __name__ == '__main__':
#     # To check if connection is ON or OFF
#
#     connection = pymysql.connect(
#         user=db_user,
#         password=db_password,
#         host=db_host,
#         port=db_port,
#         autocommit=True
#     )
#
#     print(connection.open)
