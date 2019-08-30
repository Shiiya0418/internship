
import time
#import nfc
import mysql.connector
import RPi.GPIO as GPIO
import MFRC522
import signal

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(11,GPIO.OUT,initial=GPIO.LOW)

continue_reading = True

terminal_date = "2018.01.01"
terminal_time = "00:00:00"
terminal_id   = "WA18"
terminal_seq  = "0001"
tag_id = "D"
last_UID = []
last_ctime = time.time()


# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()


#GPIO.setmode(GPIO.BCM)

GPIO.setup(36,GPIO.OUT)
GPIO.setup(32,GPIO.OUT)

p = GPIO.PWM(32,1000)
#p.start(50)   50% duty 
#p.stop()

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    global continue_reading
    print "Ctrl+C captured, ending read."
    continue_reading = False
    global p
    p.stop()
    GPIO.cleanup()

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)


#bootup sign
GPIO.output(36,1)
#GPIO.output(32,1)
p.start(50)
time.sleep(0.4)
p.stop()
#GPIO.output(32,0)
GPIO.output(36,0)
#print "database connecting .."
#conn = mysql.connector.connect(user='root', password='raspberry',\
#       host='192.168.24.230', database='onlyboard_db')
#conn.close
#print "database connect ok"
time.sleep(0.8)
GPIO.output(36,1)
#GPIO.output(32,1)
p.start(50)
time.sleep(0.4)
p.stop()
#GPIO.output(32,0)
GPIO.output(36,0)

check_times = 0

# Scan for cards
#(status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

visit = 0
# loop
print "in loop"
while continue_reading:
    
    # Scan for cards
    # MIFAREReader.M+FRC522_init()
    (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
    print(status)
    print(MIFAREReader.MI_OK)

    # If a card is not found
    if status != MIFAREReader.MI_OK:
        print "visit flag is ",
        print visit
        print("status is not ok")
        if last_UID != []:
            print("tag has been read.")
            if check_times<2:
                check_times+=1
                time.sleep(0.3)
            else:
                if check_times == 2 :
                    print "check times full"
                check_times = 0
                GPIO.output(36,1)
                #GPIO.output(32,1)
                p.start(50)
                time.sleep(0.2)
                p.stop()
                end_time = time.strftime('%H:%M:%S')
                update_datetime = time.strftime('%Y-%m-%d %H:%M:%S')
                
                # update
                conn = mysql.connector.connect(user='internship', password='wakayama',\
                                               host='192.168.24.15', database='wakatestdb')
                cur = conn.cursor()
                print "db connect"
                # update
                sql = "update terminals_tb set end_time =cast(%s as time),"\
                      "update_datetime = cast(%s as datetime) where "\
                      " terminal_date = %s and terminal_time = %s "\
                      " and terminal_id= %s and terminal_seq = %s "\
                      " and tag_id = %s ;"
                cur.execute(sql,(end_time,update_datetime,terminal_date,\
                                 terminal_time,terminal_id,terminal_seq,tag_id))
                print "db connect ok"
                conn.commit()
                cur = conn.cursor()
                # new data
                print("select all data of terminals_tb")
                print(textdataarray[1])
                print("this data came from the tag")
                
                cur.execute("select * from terminals_tb where tag_code = %s",(textdataarray[1],))
                temp = 9999
                
                for row in cur.fetchall():
                    #print(row[5])
                    #List[j] = row[5]
                    for i in range(14):
                        #print i,
                        #print(row[i])
                        if textdataarray[1] == row[5]:
                            temp = row[5]
                    #print("")
                    #j += 1
                conn.commit()
                
                
                cur = conn.cursor()
                print(terminal_id)
                """
                cur.execute("select tag_code"\
                            "from terminals_tb"\
                            "where terminal_id = %s"\
                            "and tag_id = 'A'"\
                            "order by terminal_date "\
                            "limit 1",(terminal_id,))
                """
                cur.execute("select tag_code from terminals_tb where terminal_id = %s and tag_id = 'A' order by terminal_date limit 1",(terminal_id,))
                #print(cur)
                for rec in cur.fetchall():
                    #print rec[0]
                    action_code = rec[0]
                print(action_code)
                conn.commit()
                
                cur = conn.cursor()
                cur.execute("select * from terminals_tb where tag_code = %s order by terminal_date asc limit 1",(tag_code,))
                for rec in cur.fetchall():
                    print rec[0]
                    arr = rec[0]
                conn.commit()
                
                cur = conn.cursor()
                cur.execute("select * from terminals_tb where tag_code = %s and terminal_date > %s and terminal_id = %s",(action_code,arr,terminal_id))
                action_count = 0
                #print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
                for rec in cur.fetchall():
                    action_count += 1
                    print(rec[0])
                print(action_count)
                conn.commit()
                
                cur = conn.cursor()
                cur.execute("select * from kouteihyo where accode = %s",(action_code,))
                ac = 0
                for rec in cur.fetchall():
                    print(rec[0])
                    ac += 1
                print(ac)
                conn.commit()
                cur = conn.cursor()
                cur.execute("select * from kouteihyo order by number desc")
                endflag = 0
                fin_action = 0
                for rec in cur.fetchall():
                    if fin_action == 0:
                        fin_action = rec[8]
                    for i in range(11):
                        print(rec[i]),
                    print("")
                print(fin_action)
                
                
                if (fin_action == action_code) & (ac <= action_count):
                    endflag = 1
                
                if (ac > action_count) & (endflag != 1):
                    #cur = conn.cursor()
                    #cur.execute("select * from kouteihyo where num != non order by number")
                    for k in range(10):
                        print(k)
                        GPIO.output(11,GPIO.HIGH)
                        time.sleep(0.5)
                        print('*')
                        GPIO.output(11,GPIO.LOW)
                        time.sleep(0.5)
                    
                print("end of terminals")
                cur = conn.cursor()
                print("choose SASIDATA table")
                #cur.execute("select * from SASIDATA where DENPYO_NO = %s",(temp,))
                cur.execute("select COLOR from SASIDATA where DENPYO_NO = %s",(temp,))
                #cur.execute("select * from SASIDATA")
                print("select DENPYO_NO data")
                #denpyo = cur.fetchall()
                denpyo = cur.fetchone()
                print(denpyo)
                conn.commit()
                
                cur = conn.cursor()
                print("cur = conn.cousor() of 2ed")
                cur.execute("select * from kouteihyo where work = %s",(denpyo))
                print("kouteihyou ok")
                counter_times = 0
                for row in cur.fetchall():
                    counter_times = row[9]
                """
                    for i in range(10):
                        print i,
                        print(row[i])
                """
                print("")
                print(temp)
                conn.commit()
                print(counter_times)
                
                # hazusareta
                print "Card Removed"
                # LED & BEEP
                GPIO.output(36,1)
                #GPIO.output(32,1)
                p.start(50)
                time.sleep(0.2)
                p.stop()
                end_time = time.strftime('%H:%M:%S')
                update_datetime = time.strftime('%Y-%m-%d %H:%M:%S')
                print("after commit()")
                cur.close
                print("after cur.close")
                conn.close
                print "put write ok"
                p.start(50)
                time.sleep(0.2)
                p.stop()
                #counter_times = 100
                #GPIO.output(32,0) 
                # update
                last_UID = []
                print "remove tag ok"
                p.start(50)
                time.sleep(0.2)
                p.stop()
                #GPIO.output(32,0)
                GPIO.output(36,0)
                
    else:
        try:
          print("status is ok")
          check_times = 0
          # Get the UID of the card
          (status,uid) = MIFAREReader.MFRC522_Anticoll()
          
          # If we have the UID, continue
          if status == MIFAREReader.MI_OK:
            if last_UID != uid:
                if last_UID != []:
                    # remove write
                    GPIO.output(36,1)
                    #GPIO.output(32,1)
                    p.start(50)
                    time.sleep(0.2)
                    p.stop()
                    end_time = time.strftime('%H:%M:%S')
                    update_datetime = time.strftime('%Y-%m-%d %H:%M:%S')
                    
                    
                    last_UID = []
                    p.start(50)
                    time.sleep(0.2)
                    p.stop()
                    #GPIO.output(32,0)
                    GPIO.output(36,0)
                    
                last_UID = uid
                # Select the scanned tag
                print("MIFAREReader.MFRC522_selectTag(uid)")
                MIFAREReader.MFRC522_SelectTag(uid)
                print(MIFAREReader)
                if status == MIFAREReader.MI_OK:
                    # 2ndByte-
                    block_no = 6
                    data = []
                    scouter = 0
                    print(scouter)
                    while 254 not in data:
                        print(scouter)
                        scouter+=1
                        data.extend(MIFAREReader.MFRC522_Read(block_no))
                        block_no += 4
                    MIFAREReader.MFRC522_StopCrypto1()
                    # delete top
                    del data[0]
                    del data[data.index(254):]
                    text = "".join(chr(x) for x in data)
                    print text
                    
                    GPIO.output(36,1)
                    #GPIO.output(32,1)
                    p.start(50)
                    time.sleep(0.2)
                    p.stop()
                    textdataarray = text.split(":")
                    tag_mode = textdataarray[0]
                    """
                    ptint information of the tag
                    for i in range(5):
                        print i
                        print(textdataarray[i])
                    """
                    if tag_mode == "P" or tag_mode == "A" :
                        tag_code = textdataarray[1]
                        tag_name = textdataarray[2]
                        tag_denpyo_number = ""
                        tag_delivery_date = ""
                        tag_order_code    = ""
                        tag_order_name    = ""
                    elif tag_mode == "D" :
                        tag_code          = textdataarray[1]
                        tag_name          = ""
                        tag_denpyo_number = ""
                        tag_delivery_date = textdataarray[2]
                        tag_order_code    = textdataarray[3]
                        tag_order_name    = textdataarray[4]
                    elif tag_mode == "R" :
                        tag_code          = textdataarray[1]
                        tag_name          = ""
                        tag_denpyo_number = textdataarray[2]
                        tag_delivery_date = textdataarray[3]
                        tag_order_code    = textdataarray[4]
                        tag_order_name    = textdataarray[5]
                    print tag_name
                    terminal_date = time.strftime('%Y.%m.%d')
                    terminal_time = time.strftime('%H:%M:%S')
                    terminal_seq  = "0001"
                    tag_id        = tag_mode
                    start_time  = time.strftime('%H:%M:%S')
                    end_time    = time.strftime('%H:%M:%S')
                    delete_flag = "0"
                    regist_datetime = time.strftime('%Y-%m-%d %H:%M:%S')
                    update_datetime = time.strftime('%Y-%m-%d %H:%M:%S')
                    # data insert
                    conn = mysql.connector.connect(user='internship', password='wakayama',\
                                               host='192.168.24.15', database='wakatestdb')
                    cur = conn.cursor()
                    # new data
                    sql = "insert into terminals_tb values (%s,%s,%s,%s,%s,%s,"\
                                    "%s,%s,%s,%s,%s,"\
                                    "cast(%s as time),cast(%s as time),%s,"\
                                    "cast(%s as datetime),cast(%s as datetime));"
                    cur.execute(sql,(terminal_date,terminal_time,terminal_id,\
                                      terminal_seq,tag_id,tag_code,tag_name,\
                                      tag_denpyo_number,tag_delivery_date,\
                                      tag_order_code,tag_order_name,start_time,\
                                      "00:00:00",delete_flag,regist_datetime,\
                                      update_datetime))
                    conn.commit()
                    cur.close
                    conn.close
                    print "put write ok"
                    p.start(50)
                    time.sleep(0.2)
                    p.stop()
                    #GPIO.output(32,0)
                    GPIO.output(36,0)
                    visit = 1
                    print visit
        except:
          pass





