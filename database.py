import pymysql


def conectar():
    conexion = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="flashop",
        port=3306,
        cursorclass=pymysql.cursors.DictCursor
    )

    return conexion