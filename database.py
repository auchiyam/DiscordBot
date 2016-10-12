import pymysql

class Database:
    
    def __init__(self):
        #connect to sql database
        self.database = pymysql.connect(host='localhost',
                             port=3306,
                             user='koinuri',
                             password='592358803zDf',
                             db='discordbot',
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
            print(sql)
            cursor.execute(sql)
        self.database.commit()

    def insert(self, table, values):
        with self.database.cursor() as cursor:
            sql = "INSERT INTO %s\n VALUES (" % (table)
            for v in values:
                if isinstance(v, set):
                    sql += "'{\"array\":["
                    for i in v:
                        sql += '"%s",' % (i)
                    sql = sql[0:-1] + "]}',"
                else:
                    sql += "'%s'," % v
            sql = sql[0:-1] + ");"
            print(sql)
            try:
                cursor.execute(sql)
            except pymysql.err.IntegrityError:
                nvalue = list()
                nvalue.append(int(values[0])+1)
                for i in values[1:]:
                    nvalue.append(i)
                self.insert(table, nvalue)
                self.update_id(table, nvalue[-1], nvalue[0])
                
        self.database.commit()

    def select(self, table, columns, operator=""):
        with self.database.cursor() as cursor:
            sql = "SELECT "
            for c in columns:
                sql += "%s," % (c)
            sql = sql[0:-1] + "\nFROM %s\n" % (table)
            if (len(operator) > 0):
                sql += "WHERE %s;" % (operator)
            print(sql)
            cursor.execute(sql)
            return cursor.fetchall()

    def delete(self, table, operator):
        with self.database.cursor() as cursor:
            sql = "DELETE FROM %s\nWHERE %s;" % (table, operator)
            print(sql)
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
            print(sql)
            cursor.execute(sql)
        self.database.commit()
            
    def MySQL_commands(self, command):
        with self.database.cursor() as cursor:
            print(command)
            cursor.execute(command)
            return cursor.fetchall()

    def escape_characters(self, v, n):
        tmp = v.split(n)
        v = ""
        for a in tmp:
            v += a + "\\" + n
        v = v[0:-2]
        return v
