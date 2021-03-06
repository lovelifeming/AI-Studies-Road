# encoding: utf-8
import datetime
import json
import logging
import threading
import time
from logging.handlers import TimedRotatingFileHandler
from queue import Queue

import psycopg2.extras
import requests
from influxdb import InfluxDBClient

# 定义报警规则读取时间间隔（秒）
GZ_READ_TIME = 60 * 60
# 定义报警规则处理时间间隔（秒）
GZ_HANDLE_TIME = 60 * 60
# 定义数据查询向前偏移时间（秒）
SJ_XQPY = 8 * 60 * 60 + 60 * 60
# 定义获取规则数据接口url
HQ_SJGZ = 'http://localhost:8087/digitized/rule/python/param'
# 定义获取规则数据接口参数
PAYLOAD = {'scriptTag': 'MAIN_DRIVE_ALARM_TRUE'}
# 定义消费者线程数
CUS = 5


# 创建数据库连接
def create_con():
    gp_db, cur, client = None, None, None
    while True:
        try:
            if gp_db is None or cur is None or client is None:
                gp_con = psycopg2.connect(dbname="testdb", user="gpadmin", password="gpadmin", host="192.1.1.100",
                                          port="5432")
                cur = gp_db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                # 连接tsdb数据库
                client = InfluxDBClient('192.1.1.100', 8086, 'admin', '123456', 'testdb')
            return gp_db, cur, client
        except Exception as e:
            logger.error(e)


# 获取当前时间前5秒
def now_time():
    now_time = datetime.datetime.now()
    now_old = now_time + datetime.timedelta(seconds=-SJ_XQPY)
    now_old = str(now_old)
    now_old_split = now_old.split(" ")
    now_old = now_old_split[0] + "T" + now_old_split[1] + "Z"
    now_time = str(now_time)
    now_time_split = now_time.split(" ")
    now_time = now_time_split[0] + "T" + now_time_split[1] + "Z"
    return [now_old, now_time]


def str_to_timestamp(utc_str: str, utc_format: str, offset: int):
    """
    UTC时间字符串转换为时间戳
    """
    timeArray = time.strptime(utc_str, utc_format)
    timeStamp = (int(time.mktime(timeArray)) + offset * 60 * 60) * 1000
    return timeStamp


def getLogger(fileName: str, name='mylogger', level=logging.DEBUG):
    logger1 = logging.getLogger(name)
    logger1.setLevel(level)
    formatter_str = '[%(asctime)s][%(thread)d][%(filename)s][line: %(lineno)d][%(levelname)s] ## %(message)s'
    datefmt = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter(formatter_str, datefmt)

    rf = TimedRotatingFileHandler(filename=fileName, when="midnight", interval=1, backupCount=15,
                                  encoding='utf-8')
    rf.suffix = "%Y-%m-%d_%H-%M.log"
    rf.setFormatter(formatter)
    rf.setLevel(level)
    logger1.addHandler(rf)
    return logger1


logger = getLogger("./logs/equipment_alarm_main_drive_alarm_true.log")

# 创建队列
fifo = Queue()
# 创建缓存数据列表
cache = []
# 创建待处理列表
wait = []
# 创建处理失败列表
fail = []


# 生成任务队列
def producers():
    while True:
        # 模拟数据
        try:
            resp = requests.get(HQ_SJGZ, params=PAYLOAD)
            resp.encoding = 'utf-8'
            #   json解析
            html = json.loads(resp.text)
            mll = html["data"]
            # 判断是否是新规则，如果是新规则，加入任务队列
            cache.clear()
            fifo.queue.clear()
            for m in mll:
                for i in m:
                    fifo.put(i)
                    cache.append(i)
            time.sleep(GZ_READ_TIME)
        except Exception as e:
            logger.exception(e)
            if e == "## cursor already closed":
                create_con()


# 消费者线程--处理数据
def consumers(q_fifo, thread):
    gp_db, cur, client = None, None, None
    con_flag = False
    while True:
        try:
            if cur is None or con_flag:
                gp_db_c, cur_c, client_c = create_con()
                gp_db, cur, client = gp_db_c, cur_c, client_c
            clx = q_fifo.get()
            wait.append(clx["rule_name"] + "--》" + clx["en_name"])
            logger.info(thread + "--正在处理：{}".format(clx["rule_name"] + "--》" + clx["en_name"]))
            call_type = 0
            alert_context = ""

            # 获得库源
            result = None
            table_type = clx["table_type"]
            if table_type == "gp":
                time_split = now_time()
                start_time = time_split[0].replace("T", " ").replace("Z", "")
                end_time = time_split[1].replace("T", " ").replace("Z", "")
                sql = "select " + clx["en_name"] + "," + clx["table_en_time"] + " from " + clx[
                    "table_en_name"] + " where " + clx["table_en_time"] + ">='" + start_time + "' and " + clx[
                          "table_en_time"] + "<='" + end_time + "' order by " + clx["table_en_time"] + " DESC LIMIT 1"
                logger.info("execute sql:" + sql)
                cur.execute(sql)
                result = cur.fetchall()

            if table_type == "tsdb":
                time_split = now_time()
                start_time = time_split[0]
                end_time = time_split[1]
                sql = "select " + clx["en_name"] + " from " + clx["table_en_name"] + " where " + clx[
                    "table_en_time"] + ">='" + start_time + "' and " + clx[
                          "table_en_time"] + "<='" + end_time + "' order by " + clx["table_en_time"] + " DESC"
                logger.info("execute sql:" + sql)
                result = client.query(sql)
            # 获取规则 获得最大，最小值,
            # 写自己的报警逻辑，决定call_type的值，1位报警，0为不报警
            alarm_value = ''
            param_info = clx["param_info"]
            for p in param_info:
                if p["code"] == "alarm_value":
                    alarm_value = p["value"]
            point_value_list = []
            point_value_time = ''
            point_value_value = None
            logger.info("查询结果：" + str(result))

            if table_type == "gp":
                for r in result:
                    point_value_list.append([r[clx["en_name"].lower()], r[clx["table_en_time"]]])
            if table_type == "tsdb":
                for r in result.get_points():
                    point_value_list.append([r[clx["en_name"]], r[clx["table_en_time"]]])
            if alarm_value != '':
                for pv in point_value_list:
                    if pv[0] is not None and alarm_value in pv[0]:
                        point_value_value = pv[0]
                        point_value_time = pv[1]
                        alert_context = "主传动故障报警:"
                        call_type = 1

            # 如果没有达到报警标准，十分钟保持归位，则任务继续，处理逻辑==========================================
            if call_type != 1:
                fifo.put(clx)
            # 如果报警则处理逻辑==============================================================================
            if call_type == 1:
                # 处理成功从待处理列表中移除
                # 查询设备名
                cur.execute("select device_name,device_id from bd.bd_app_device where device_id in(select device_id "
                            "from bd.bd_app_device_point where point_en_name=%s limit 1)" % (
                                    "'" + clx["en_name"] + "'"))
                sb = cur.fetchone()
                device_name = sb["device_name"]
                device_code = sb["device_id"]

                # 获取报警时间
                timestamp = None
                if table_type == "gp":
                    timestamp = str_to_timestamp(str(point_value_time), "%Y-%m-%d %H:%M:%S.%f", 0)
                if table_type == "tsdb":
                    timestamp = str_to_timestamp(point_value_time, "%Y-%m-%dT%H:%M:%S.%fZ", 8)

                count = 1
                point_list = ''
                for ch in reversed(point_value_value):
                    if ch == alarm_value:
                        point_list += str(count) + ","
                    count += 1
                if point_list != '':
                    name = clx["en_name"]
                    sql = u'select * FROM bd.bd_device_signal_dict WHERE type_code=upper(%s) AND index_code in(%s)' \
                          % ("'" + name[name.rindex('_') + 1::] + "'", point_list[0:-1])
                    cur.execute(sql)
                    signalDict = cur.fetchall()
                    for d in signalDict:
                        alert_context += d["type_code"] + "," + str(d["index_code"]) + "," + d["hw_drawing"] + "," \
                                         + str(d["signal"]) + "," + str(d["signal_val"])
                        logger.info(alert_context)
                        ret = cur.execute("INSERT INTO bd.bd_uu_alert_num (device_name, device_code, create_time, "
                                          "alert_context, production_line, call_type,  point_name, point_code, point_value, alert_param)"
                                          " VALUES (%s, %s,%s, %s,%s, %s,%s, %s,%s,%s);"
                                          % ("'" + device_name + "'", "'" + device_code + "'", timestamp,
                                             "'" + alert_context + "'",
                                             "'" + "万能二线轧线" + "'", "'" + str(call_type) + "'",
                                             "'" + clx["ch_name"] + "'",
                                             "'" + clx["en_name"] + "'", "'" + str(point_value_value) + "'",
                                             "'" + json.dumps(clx["param_info"]) + "'"))
                gp_db.commit();
            wait.remove(clx["rule_name"] + "--》" + clx["en_name"])

            # 处理成功从失败列表中移除
            if clx["rule_name"] + "--》" + clx["en_name"] in fail:
                fail.remove(clx["rule_name"] + "--》" + clx["en_name"])
            if point_value_value is None:
                point_value_value = "无报警值"
            logger.info(thread + "--成功处理：{}--设定报警值{}:当前值{}--待处理{}个--处理失败列表:{}".format(
                clx["rule_name"] + "--》" + clx["en_name"], alarm_value, point_value_value, len(wait), fail))
            con_flag = False

        # 程序异常，继续处理
        except Exception as e:
            logger.exception(e)
            if str(e) in "## gp cursor already closed" or str(e) in "## server closed the connection unexpectedly":
                con_flag = True
            threadName = clx["rule_name"] + "--》" + clx["en_name"]
            if threadName in wait:
                wait.remove(threadName)
            if clx["rule_name"] + "--》" + clx["en_name"] not in fail:
                fail.append(clx["rule_name"] + "--》" + clx["en_name"])
            logger.info(thread + "--处理失败：{}--待处理{}个--处理失败列表:{}".format(clx["rule_name"] + "--》" +
                                                                       clx["en_name"], len(wait), fail))
            fifo.put(clx)
        time.sleep(GZ_HANDLE_TIME)


def main():
    # 建立1个生产者线程
    thread_pro = threading.Thread(target=producers)
    pthread_list = [thread_pro]
    # 建立n个消费者线程  CUS
    for i in range(CUS):
        thread_cus = threading.Thread(target=consumers, args=(fifo, "消费线程{}".format(i + 1)))
        pthread_list.append(thread_cus)
    for i in pthread_list:
        i.start()
    for i in pthread_list:
        i.join
    return 0


if __name__ == '__main__':
    main()
