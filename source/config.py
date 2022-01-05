import sqlite3
import json


def config(value):
    with open("config.json", 'r', encoding='utf-8 sig') as file:
        data = json.load(file)
        token = data['bot']['token']
        category = data['setting']['category']
        guild = data['setting']['guild']
        log_channel = data['setting']['log_channel']
        guild2 = data['setting']['guild2']
        if value == "token":
            return token
        elif value == "category":
            return category
        elif value == "guild":
            return guild
        elif value == "log_channel":
            return log_channel
        elif value == "guild2":
            return guild2
def join_sql():
    try:
        sql = sqlite3.connect("m.db")
        wg = sql.cursor()
        return sql, wg
    except:
        return False, False

def insert_user(id, channel): #새로운 문의자 데이터베이스 삽입
    sql, wg = join_sql()
    if wg:
        insert_user = "insert into m(id, channel) values (?, ?)"
        wg.execute(insert_user, (id, channel))
        sql.commit()
        sql.close()

def check_user_m(id):
    sql, wg = join_sql()
    if wg:
        b = f"select * from m WHERE id = '{id}'"
        wg.execute(b)
        sql.commit()
        result = wg.fetchone()
        if result is None:
            return True
        else:
            return False

def check_user_m2(id, value): #check2
    sql, wg = join_sql()
    if wg:
        if value == "channel":
            b = f"select * from m WHERE id = '{id}'"
            wg.execute(b)
            sql.commit()
            result = wg.fetchone()
            if result is None:
                return False
            else:
                channel = result[1]
                return channel
        else:
            b = f"select * from m WHERE channel = '{id}'"
            wg.execute(b)
            sql.commit()
            result = wg.fetchone()
            if result is None:
                return False
            else:
                user_id = result[0]
                return user_id

def delete_user(channel): #문의종료 후 해당 유저의 데이터 삭제
    sql, wg = join_sql()
    if wg:
        b = f"delete from m WHERE channel = '{channel}'"
        wg.execute(b)
        sql.commit()
        sql.close()



def check_black(id): # 문의자 블랙리스트 확인
    sql, wg = join_sql()
    if wg:
        try:
            b = f"select * from black WHERE id = '{id}'"       
            wg.execute(b)
            sql.commit()
            result = wg.fetchone()
            if result is None:
                sql.close()
                return False, False
            else:
                reason = result[4]
                sql.close()
                return True, reason
        except Exception as e:
            print(f"ERROR MESSAGE : {e} | ERROR CODE : black_01")
            return False, False
    else:
        return False, False

def check_count(id): #문의 내역 건수 확인
    sql, wg = join_sql()
    if wg:
        try:
            b = f"select * from user_m_count WHERE id = '{id}'"
            wg.execute(b)
            sql.commit()
            result = wg.fetchone()
            if result:
                count = result[1] + 1
                update_count = f"update user_m_count SET count = '{count}' WHERE id = '{id}'"
                wg.execute(update_count)
                sql.commit()
                sql.close()
                return
            else:
                insert_count = f"insert into user_m_count(id, count) values (?, ?)"
                wg.execute(insert_count, (id, 1))
                sql.commit()
                sql.close()
                return
        except Exception as e:
            print(f"ERROR MESSAGE : {e} | ERROR CODE : count_01")
            return

def check_url2(id):
    sql, wg = join_sql()
    if wg:
        try:
            ################################카운트 값 구하기########################################
            check_count = f"select * from user_m_count WHERE id = '{id}'"
            count = 0
            wg.execute(check_count)
            sql.commit()
            result = wg.fetchone()
            if result:
                count = result[1]
                if count == 0:
                    return count, False
                else:
                    return count, True
            else:
                return count, False
            #################################URL 값 구하기########################################
        except Exception as e:
            return print(f"ERROR MESSAGE : {e} | ERROR CODE : check_url_02"), False, False, False, False

