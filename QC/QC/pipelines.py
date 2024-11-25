# Define your item pipelines here
from QC.items import QcItem
import QC.db_config as db


class QcPipeline:

    def open_spider(self, spider):

        if '_newUrls' in spider.name:
            db.db_data_table = f"{spider.name}_{db.delivery_date}_newUrlPids"
            print('new urls table name changed...')
        else:
            print('regular table name set.')
            db.db_data_table = f"{spider.name}_{db.delivery_date}"
        try:
            create_database = f"CREATE DATABASE IF NOT EXISTS `{db.db_name}`;"
            spider.cursor.execute(create_database)
            spider.cursor.execute(f"USE `{db.db_name}`;")
        except Exception as e:
            print(e)

        try:
            # Create the data table if not exists
            create_table = f"""CREATE TABLE IF NOT EXISTS `{db.db_data_table}` 
            (`Id` INT NOT NULL AUTO_INCREMENT,
                `comp` VARCHAR (255) DEFAULT 'N/A',
                `fk_id` VARCHAR (255) DEFAULT 'N/A',
                `pincode` VARCHAR (255) DEFAULT 'N/A',
                `url` VARCHAR (10000) DEFAULT 'N/A',
                `name` TEXT,
                `availability` VARCHAR (255) DEFAULT 'N/A',
                `price` VARCHAR (255) DEFAULT 'N/A',
                `discount` VARCHAR (255) DEFAULT 'N/A',
                `mrp` VARCHAR (255) DEFAULT 'N/A',
                PRIMARY KEY (`Id`),
                UNIQUE KEY `fid` (`fk_id`,`pincode`)
                ) ENGINE = InnoDB DEFAULT CHARSET = UTF8MB4;
                """
            spider.cursor.execute(create_table)
        except Exception as e:
            print(e)

    def process_item(self, item, spider):
        input_table = spider.input_table
        if isinstance(item, QcItem):
            # print('instance of QcItem')
            item_copy = item.copy()
            index_id = item_copy['index_id']

            item.pop('index_id')
            field_list = []
            value_list = []

            for field in item:
                field_list.append(str(field))
                value_list.append('%s')
            fields = ','.join(field_list)
            values = ", ".join(value_list)

            insert_db = f"""insert ignore into {db.db_data_table}
            ( """ + fields + """ ) values ( """ + values + """ )"""

            try:
                spider.cursor.execute(insert_db, tuple(item.values()))
                spider.con.commit()
                print('Data Inserted...')
            except Exception as e:
                print('Error while inserting data:', e)

            try:
                update_query = f"""UPDATE {input_table} SET status='DONE'
                 WHERE index_id={index_id}"""
                spider.cursor.execute(update_query)
                spider.con.commit()
                print('Status Updated')
            except Exception as e:
                print('Error while updating:', e)
                
        return item