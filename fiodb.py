import sqlite3
import sys

def sql_connect(sqldb):
    try:
        con = sqlite3.connect(sqldb)
        return con
    except Error:
        print(Error)

def sql_close(con):
    print("Sql: Closing connection")
    con.close()

def sql_query_table(con, tablename):
    cur = con.cursor()
    cur.execute("SELECT count(name) FROM sqlite_master WHERE type=\'table\' AND name='{}'".format(tablename))
    if (cur.fetchone()[0] >= 1):
        print("Table {} already exists".format(tablename))
        return 1
    #print("Table {} not present".format(tablename))
    return 0

def sql_create_table(con, tablename):
    if (sql_query_table(con, tablename)):
        return 1
    print(tablename)
    cur = con.cursor()
    cmd = "CREATE TABLE IF NOT EXISTS {} (".format(tablename)
    cmd += " threads int NOT NULL)"
    cur.execute(cmd)

    cmd = "insert INTO {} (threads) Values (1),(2),(4),(8),(12),(16),(24)".format(tablename)
    cur.execute(cmd)
    con.commit()
    print("Sql: Table {} created".format(tablename))
    return 0

    #cmd = "SELECT * FROM {}".format(tablename)
    #cur.execute(cmd)
    #rows = cur.fetchall()
    #for row in rows:
    #    print(row)

def sql_print_table(con, tablename):
    cur = con.cursor()
    cmd = "SELECT * from {}".format(tablename)
    cur.execute(cmd)
    rows = cur.fetchall()
    for row in rows:
        print(row)

def sql_update_table(con, tablename, column, threadID, value):
    cur = con.cursor()
    cmd = "UPDATE {} SET {} = {} WHERE threads = {}".format(tablename, column, value, threadID)
    print(cmd)
    cur.execute(cmd)
    con.commit()

def sql_add_column(con, tablename, columnname):
    cur = con.cursor()
    cmd = "ALTER TABLE {} ADD {} float".format(tablename, columnname)
    print(cmd)
    cur.execute(cmd)
    con.commit()




#con = sql_connect("fioperf.db")
#sql_query_table(con, "dioread_lock_4K")
#sql_create_table(con, "dioread_lock_4K")
#sql_update_table(con, "dioread_lock_4K", "Vanilla", 4, 8)
#sql_update_table(con, "dioread_lock_4K", "ilock", 8, 18)
#sql_print_table(con, "dioread_lock_4K")
