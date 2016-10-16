import pymysql

class DuplicatePrimaryKeyError(Exception):
    '''
    Raised when an insertion was performed with primary key that already exist.
    '''
    def __init__(self, keys=["id"]):
        m = "("
        for i in keys:
            m += "%s," % (i)
        m = m[0:-1] + ")"
        self.message = "The keys %s conflicts with the existing keys"
    

class Database:

    MySQL_IP = ''
    MySQL_user = ''
    MySQL_pass = ''
    MySQL_db = ''

    def __init__(self):
        #connect to sql database
        self.database = pymysql.connect(host=Database.MySQL_IP,
                             port=3306,
                             user=Database.MySQL_user,
                             password=Database.MySQL_pass,
                             db=Database.MySQL_db,
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.database.close()

    #string name:   the name of the table to make
    #list fields:   list of fields the table will take.  should be in "field_name type" format
    def create_table(self, name, fields):
        with self.database.cursor() as cursor:
            sql = "CREATE TABLE %s (" % (name)
            for f in fields:
                fs = f.split()
                sql += "%s %s," % (fs[0], fs[1])
            sql = sql[0:-1] + ");"
            cursor.execute(sql)
        self.database.commit()

    def insert(self, table, values, columns=[]):
        with self.database.cursor() as cursor:
            if len(columns) != 0:
                col = "("
                for i in columns:
                    col += "%s," % (i)
                col = col[0:-1] + ")"
            else:
                col = ""
            sql = "INSERT INTO %s %s\nVALUES (" % (table, col)
            for v in values:
                if isinstance(v, set):
                    sql += "'{\"array\":["
                    for i in v:
                        sql += '"%s",' % (i)
                    sql = sql[0:-1] + "]}',"
                else:
                    sql += "'%s'," % v
            sql = sql[0:-1] + ");"
            cursor.execute(sql)
        self.database.commit()

    def select(self, table, columns, operator=""):
        with self.database.cursor() as cursor:
            sql = "SELECT "
            for c in columns:
                sql += "%s," % (c)
            sql = sql[0:-1] + "\nFROM %s\n" % (table)
            if (len(operator) > 0):
                sql += "WHERE %s;" % (operator)
            cursor.execute(sql)
            return cursor.fetchall()

    def select_joined(self, table1, table2, on_columns, columns, operator=""):
        with self.database.cursor() as cursor:
            sql = "SELECT "
            for c in columns:
                sql += "%s," % (c)
            sql = sql[0:-1] + "\nFROM %s INNER JOIN %s\nON " % (table1, table2)
            for o in on_columns:
                sql += "%s AND " % (o)
            sql = sql[0:-5]
            if (len(operator) > 0):
                sql += "\nWHERE %s;" % (operator)
            cursor.execute(sql)
            return cursor.fetchall()

    def delete(self, table, operator):
        with self.database.cursor() as cursor:
            sql = "DELETE FROM %s\nWHERE %s;" % (table, operator)
            cursor.execute(sql)
        self.database.commit()

    def update_id(self, table, server, nid):
        currID = int(self.select("ids", [table], "server='%s'" % (server))[0][table])
        if (nid > currID):
            self.update("ids", ["%s=%s" % (table,nid)], "server='%s'" % (server))

    def update(self, table, values, operator):
        with self.database.cursor() as cursor:
            sql = "UPDATE %s\nSET " % (table)
            for v in values:
                sql += "%s," % (v)
            sql = sql[0:-1] + "\nWHERE %s;" % (operator)
            cursor.execute(sql)
        self.database.commit()
            
    def MySQL_commands(self, command):
        with self.database.cursor() as cursor:
            cursor.execute(command)
            self.database.commit()
            return cursor.fetchall()

    def escape_characters(self, v, n):
        tmp = v.split(n)
        v = ""
        for a in tmp:
            v += a + "\\" + n
        v = v[0:-2]
        return v
