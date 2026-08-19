import mysql.connector

try:
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="14072004",
        database="heart_disease_db"
    )

    if connection.is_connected():
        print("MySQL Connected Successfully!")

except mysql.connector.Error as err:
    print("Error:", err)