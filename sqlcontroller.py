import string
import discord
from pymysql import NULL
from datetime import datetime
import pymysql.cursors
import hashlib

dbhost = 'localhost'
dbuser = 'usuariomaster'
dbpassword = 'pass123'
dbdatabase = dbdatabase


def gerarSQL(member, script, ip):
    try:
        connection = pymysql.connect(host=dbhost,user=dbuser,password=dbpassword,database=dbdatabase,cursorclass=pymysql.cursors.DictCursor)
        with connection.cursor() as cursor:
            licencabase = f"{member.id};{script}"
            licenca = hashlib.sha1(licencabase.encode()).hexdigest().upper()
            sql = f"INSERT INTO `licenses` (`user_id`, `script`, `licenca`, `ip`) VALUES ('{member.id}', '{script}', '{licenca}', '{ip}');"
            cursor.execute(sql)
            connection.commit()
            cursor.close()
        connection.close()
        return licenca
    except:
        return "Erro"

def gerarSQLLoja(script, quantidade):
    memberid = "loja"
    matrizScript = {'jw_vip': 25, 'five_set_system_lite': 42, 'five_set_system_pro': 43}
    actualScript = script.replace("_lite", "").replace("_pro", "")
    pro = '{"default","pro"}'
    quantidade = int(quantidade)
    try:
        connection = pymysql.connect(host=dbhost,user=dbuser,password=dbpassword,database=dbdatabase,cursorclass=pymysql.cursors.DictCursor)
        connection2 = pymysql.connect(host=dbhost,user=dbuser,password=dbpassword,database='fiveloja',cursorclass=pymysql.cursors.DictCursor)
        with connection2.cursor() as cursor2:
            with connection.cursor() as cursor:
                for contador in range(quantidade):
                    stamp = datetime.timestamp(datetime.now())
                    licencabase = f"{memberid};{stamp};{contador};{actualScript}"
                    licenca = hashlib.sha1(licencabase.encode()).hexdigest().upper()
                    if("_pro" in script):
                        sql = f"INSERT INTO `licenses` (`user_id`, `script`, `plugin`, `licenca`, `ip`) VALUES ('{memberid}', '{actualScript}', '{pro}', '{licenca}', '127.0.0.1');"
                    else:
                        sql = f"INSERT INTO `licenses` (`user_id`, `script`, `licenca`, `ip`) VALUES ('{memberid}', '{actualScript}', '{licenca}', '127.0.0.1');"
                    sql2 = f"INSERT INTO `wp_serial_numbers` (`serial_key`, `product_id`, `order_id`, `vendor_id`, `expire_date`, `created_date`) VALUES ('Sua Licença: {licenca}\r\nDownload: https://download.fivebrazil.com.br/download?licenca={licenca}', '{matrizScript[script]}', '0', '1', '0000-00-00 00:00:00', '0000-00-00 00:00:00');"
                    cursor.execute(sql)
                    cursor2.execute(sql2)
                    connection.commit()
                    connection2.commit()
                cursor.close() 
            connection.close()
            cursor2.close()
        connection2.close()
    except Exception as e:
        print(e)
        return "Erro"
        
def trocarIP(member, licenca, ip, validar=False):
    try:
        connection = pymysql.connect(host=dbhost,user=dbuser,password=dbpassword,database=dbdatabase,cursorclass=pymysql.cursors.DictCursor)
        with connection.cursor() as cursor:
            checkLojaData = checkLoja(licenca)
            if(validar == True and checkLojaData == False):
                return "Erro: essa licenca não é da loja ou o SQL está fora do ar."
            if(checkLojaData == False):
                sql = f"UPDATE `licenses` SET `ip` = '{ip}' WHERE `licenca` = '{licenca}' AND `user_id` = {member.id};"
            else:
                sql = f"UPDATE `licenses` SET `ip` = '{ip}', `user_id` = {member.id} WHERE `licenca` = '{licenca}';"
            affected_rows = cursor.execute(sql)
            connection.commit()
            cursor.close()
        connection.close()
        if(affected_rows > 0):
            if(validar == False):
                return f"Show de bola {member.mention}. O IP do script foi alterado com sucesso!"
            else:
                return f"Show de bola {member.mention}. Sua Licença foi verificada!"
        else:
            return "Erro: essa licenca não está em seu usuario ou o SQL está fora do ar."
    except:
        return "Erro: essa licenca não está em seu usuario ou o SQL está fora do ar."

def checkLoja(licenca):
    try:
        connection = pymysql.connect(host=dbhost,user=dbuser,password=dbpassword,database=dbdatabase,cursorclass=pymysql.cursors.DictCursor)
        with connection.cursor() as cursor:
            sql = f"SELECT * FROM `licenses` WHERE `user_id`='loja' AND `licenca` = '{licenca}'"
            cursor.execute(sql)
            result = cursor.fetchall()
            cursor.close()
        connection.close()
        if(len(result) > 0):
            return True
        else:
            return False
    except Exception as e:
        return False

def downloadScript(member,licenca):
    try:
        connection = pymysql.connect(host=dbhost,user=dbuser,password=dbpassword,database=dbdatabase,cursorclass=pymysql.cursors.DictCursor)
        with connection.cursor() as cursor:
            sql = f"SELECT * FROM `licenses` WHERE `user_id`='{member.id}' AND `licenca` = '{licenca}'"
            cursor.execute(sql)
            result = cursor.fetchall()
            cursor.close()
        connection.close()
        for row in result:
            script = row["script"]
            connection = pymysql.connect(host=dbhost,user=dbuser,password=dbpassword,database=dbdatabase,cursorclass=pymysql.cursors.DictCursor)
            with connection.cursor() as cursor:
                sql = f"SELECT * FROM `download` WHERE `script`='{script}'"
                cursor.execute(sql)
                result = cursor.fetchall()
                cursor.close()
            connection.close()
            for row in result:
                script = row["script"]
                version = row["version"]
                download = row["download"]

                return True, f"> Aqui está o **download** solicitado:\n**Script:** {script}\n**Version:** {version}\n**Download:** {download}",script,version
        return False, f"Error: essa licenca não está em seu usuario ou o SQL está fora do ar.",NULL,NULL
    except Exception as e:
       return False, f"Error: essa licenca não está em seu usuario ou o SQL está fora do ar.",NULL,NULL

def getLicensesSQL(member):
    try:
        connection = pymysql.connect(host=dbhost,user=dbuser,password=dbpassword,database=dbdatabase,cursorclass=pymysql.cursors.DictCursor)
        with connection.cursor() as cursor:
            sql = "SELECT * FROM `licenses` WHERE `user_id`='" + str(member.id) + "'"
            cursor.execute(sql)
            result = cursor.fetchall()
            cursor.close()
        connection.close()
        return result
    except Exception as e:
        print(e)
        print("Erro ao pegar licencas do SQL!")

def getTicketTypeSql(member):
    try:
        connection = pymysql.connect(host=dbhost,user=dbuser,password=dbpassword,database=dbdatabase,cursorclass=pymysql.cursors.DictCursor)
        with connection.cursor() as cursor:
            sql = "SELECT type FROM `tickets` WHERE `user_id`='" + str(member.id) + "'"
            cursor.execute(sql)
            result = cursor.fetchall()
            cursor.close()
        connection.close()
        return result
    except Exception as e:
        print(e)
        print("Erro ao pegar tickets do SQL!")

def getTicketChannelSql(channel):
    try:
        connection = pymysql.connect(host=dbhost,user=dbuser,password=dbpassword,database=dbdatabase,cursorclass=pymysql.cursors.DictCursor)
        with connection.cursor() as cursor:
            sql = "SELECT * FROM `tickets` WHERE `channel_id`='" + str(channel.id) + "'"
            cursor.execute(sql)
            result = cursor.fetchall()
            cursor.close()
        connection.close()
        return result
    except Exception as e:
        print(e)
        print("Erro ao pegar tickets do SQL!")

def getAllTicketsSql(member):
    try:
        connection = pymysql.connect(host=dbhost,user=dbuser,password=dbpassword,database=dbdatabase,cursorclass=pymysql.cursors.DictCursor)
        with connection.cursor() as cursor:
            sql = "SELECT * FROM `tickets` WHERE `user_id`='" + str(member.id) + "'"
            cursor.execute(sql)
            result = cursor.fetchall()
            cursor.close()
        connection.close()
        if result:
            return True
        else:
            return False
    except Exception as e:
        print(e)
        print("Erro ao pegar tickets do SQL!")

def gerarTicketSql(channel, member, type):
    try:
        connection = pymysql.connect(host=dbhost,user=dbuser,password=dbpassword,database=dbdatabase,cursorclass=pymysql.cursors.DictCursor)
        with connection.cursor() as cursor:
            sql = f"INSERT INTO `tickets` (`channel_id`, `user_id`, `type`) VALUES ('{channel.id}', '{member.id}', '{type}');"
            cursor.execute(sql)
            connection.commit()
            cursor.close()
        connection.close()
    except:
        return "Erro"

def deleteTicketSql(channel):
    try:
        connection = pymysql.connect(host=dbhost,user=dbuser,password=dbpassword,database=dbdatabase,cursorclass=pymysql.cursors.DictCursor)
        with connection.cursor() as cursor:
            sql = f"DELETE FROM `tickets` WHERE `channel_id` = '{channel.id}';"
            affected_rows = cursor.execute(sql)
            connection.commit()
            cursor.close()
        connection.close()
    except:
        print("Canal não existe")


def getAllStaffSql(perm):
    try:
        connection = pymysql.connect(host=dbhost,user=dbuser,password=dbpassword,database=dbdatabase,cursorclass=pymysql.cursors.DictCursor)
        with connection.cursor() as cursor:
            sql = "SELECT user_id FROM `staff` WHERE `perm`='" + str(perm) + "'"
            cursor.execute(sql)
            result = cursor.fetchall()
            cursor.close()
        connection.close()
        return result
    except Exception as e:
        print(e)
        print("Erro ao pegar staffs do SQL!")

def addStaffSql(member, perm):
    try:
        connection = pymysql.connect(host=dbhost,user=dbuser,password=dbpassword,database=dbdatabase,cursorclass=pymysql.cursors.DictCursor)
        with connection.cursor() as cursor:
            sql = f"INSERT INTO `staff` (`user_id`, `perm`, `name`, `tag`) VALUES ('{member.id}', '{perm.id}', '{member.display_name}', '{perm.name}');"
            cursor.execute(sql)
            connection.commit()
            cursor.close()
        connection.close()
    except:
        return "Erro"
