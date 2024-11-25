import db_config  # Import Database connection details
import pymysql
import os


# List of update queries
update_queries = [
    "UPDATE `mapped_amazon_inputs` SET STATUS = 'Pending'",
    "UPDATE `mapped_amazon_inputs_final` SET STATUS = 'Pending'",
    "UPDATE `mapped_bb_inputs` SET STATUS = 'Pending'",
    "UPDATE `mapped_blk_inputs` SET STATUS = 'Pending'",
    "UPDATE `mapped_dmt_inputs` SET STATUS = 'Pending'",
    # "UPDATE `mapped_fkg_inputs` SET STATUS = 'Pending'",
    "UPDATE `mapped_jmt_inputs` SET STATUS = 'Pending'",
    "UPDATE `mapped_swiggy_inputs` SET STATUS = 'Pending'",
    "UPDATE `mapped_zpt_inputs` SET STATUS = 'Pending'"
]


def execute_update_queries(queries):
    try:
        # Establishing connection
        connection = pymysql.connect(
            host=db_config.db_host,
            user=db_config.db_user,
            password=db_config.db_password,
            database=db_config.db_name,
            port=db_config.db_port,
            autocommit=True
        )
        print("Sql is connected..." if connection.open else "Sql is not connected...")
        with connection.cursor() as cursor:
            # Execute each query
            for query in queries:
                try:
                    cursor.execute(query)
                    print(f"Executed: {query}")
                except Exception as e:
                    print('Execution error', e)
        print("All queries executed and committed successfully.")
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
    finally:
        # Close the connection
        if connection:
            connection.close()


if __name__ == '__main__':
    os.chdir(os.getcwd())
    # Execute the update queries
    execute_update_queries(update_queries)
