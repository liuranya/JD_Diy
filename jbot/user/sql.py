import sqlite3


# 打开数据库
def open_sqlite(db):
    global con
    con = sqlite3.connect(db)    
    
 
# 关闭数据库
def close_sqlite():
    global con
    try:
        con.close()
    except:
        pass
    

# 提交数据库
def commit_sqlite():
    global con
    con.commit()


# 查询数据
def select_where_sqlite(name,key,value):
    global con
    try:
        cursor = con.cursor()
        cursor.execute(f'select * from {name} where {key}=?', (value,))
        values = cursor.fetchone()
        if values:
            return values
        else:
            return 
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        
        
# 查询所有数据
def select_sqlite(name):
    global con
    try:
        cursor = con.cursor()
        cursor.execute(f'select * from {name}')
        values = cursor.fetchall() 
        if values:
            return values
        else:
            return 
    except Exception as e:
        print(e)
    finally:
        cursor.close()
    
   
# 创建 表 
def create_table_sqlite(name,keys):
    global con
    try:
        cursor = con.cursor()
        cursor.execute(f'create table {name} ({keys})')
        return True
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        con.commit()
        

# 插入数据
def insert_into_sqlite(name,keys,values):
    global con
    if not isinstance(values,(tuple,list)):
        print('values必须是tuple或list')
        return
    if len(values)<0:
        print('values不能为空')
        return
    try:
        cursor = con.cursor()
        if isinstance(values,tuple):
            cursor.execute(f'insert into {name} ({keys}) values ({("?,"*len(values))[:-1]})',values)
        else:
            cursor.executemany(f'insert into {name} ({keys}) values ({("?,"*len(values[0]))[:-1]})',values)
        return True
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        con.commit()
        
        
# 更新数据
def update_sqlite(name,a_key,a_value,search_key,search_value):
    global con
    try:
        cursor = con.cursor()
        cursor.execute(f"update {name} set '{a_key}'='{a_value}' where {search_key}='{search_value}'")
        return True
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        con.commit()
        
        
# 删除数据
def delete_where_sqlite(name,key,value):
    global con
    try:
        cursor = con.cursor()
        cursor.execute(f"delete from {name} where {key}=?",(value,))
        return True
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        con.commit()
        
        
# 删除所有数据
def delete_sqlite(name):
    global con
    try:
        cursor = con.cursor()
        cursor.execute(f"delete from {name}")
        return True
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        con.commit()

      