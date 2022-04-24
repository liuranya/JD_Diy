#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import asyncio
import datetime
import os
import re
import sys
import time
import sqlite3
from .sql import *
import json
import requests

from .login import user
from telethon import events, TelegramClient
from .. import chat_id, jdbot, logger, API_ID, API_HASH, PROXY_START, proxy, CONFIG_DIR, JD_DIR, TOKEN, BOT_DIR
from ..bot.utils import cmd, V4, QL, CONFIG_SH_FILE, get_cks,TASK_CMD
from ..diy.utils import getbean, my_chat_id, myzdjr_chatIds,read,shoptokenIds,rwcon,read, write

client = user


@client.on(events.NewMessage(from_users=chat_id, pattern=r"^user(\?|？)$"))
async def user(event):
    try:
        await event.edit(r'`监控已正常启动！`')
    except Exception as e:
        title = ""
        name = "文件名：" + os.path.split(__file__)[-1].split(".")[0]
        function = "函数名：" + sys._getframe().f_code.co_name
        tip = '建议百度/谷歌进行查询'
        await jdbot.send_message(chat_id, f"{title}\n\n{name}\n{function}\n错误原因：{str(e)}\n\n{tip}")
        logger.error(f"错误--->{str(e)}")
@client.on(events.NewMessage(chats=myzdjr_chatIds, pattern=r'([\s\S]*)export\s(jd_wdz_activityId|VENDER_ID|jd_zdjr_activityId|jd_cjhy_activityId|M_WX_ADD_CART_|DAPAINEW|computer_activityIdList).*=(".*"|\'.*\')'))
async def activityID(event):
    
    def time_md():
        return time.strftime('%m%d', time.localtime(time.time()))
    try:
        text = event.message.text
        if "jd_wdz_activityId" in text:
            name = "微定制"
        elif "VENDER_ID" in text:
            name = "入会捡漏"
        elif "jd_zdjr_activityId" in text:
            name = "组队分豆"
        elif "jd_cjhy_activityId" in text:
            name = "CJ组队"
        elif r"M_WX_ADD_CART_" in text:
            name = "加购有礼"
        elif r"DAPAINEW" in text:
            name = "大牌联合"
        elif r"computer_activityIdList" in text:
            name = "电脑配件"
        else:
            return
        group = f'[{event.chat.title}](https://t.me/c/{event.chat.id}/{event.message.id})'
        msg = await jdbot.send_message(chat_id, f'【监控】{group} 发出的 `[{name}]` 环境变量！')

        
        open_sqlite('/ql/jbot/user/user.db')

        sqlite_master=select_sqlite('sqlite_master')
        try:
            table_name_list=[table[1] for table in sqlite_master]
        except:
            table_name_list=list()
        
        # 初始化 time_md 表
        if 'time_md' not in table_name_list:
            create_table_sqlite("time_md", "md varchar(4)")
            
        # 初始化 running_task 表
        if 'running_task' not in table_name_list:
            create_table_sqlite("running_task", "task_name varchar(20)")
            
        # 初始化 all_task 表
        if 'all_task' not in table_name_list:
            create_table_sqlite("all_task", "task_data varchar(500)")

        # 查询时间 月日 ,时间变化则清空 all_task 表
        if not select_where_sqlite("time_md","md",time_md()):
            # 更新 time_md 表
            delete_sqlite("time_md")
            insert_into_sqlite("time_md", "md", (time_md(),))
            # 清空 all_task 表
            delete_sqlite("all_task")
            # 清理 running_task 表
            delete_sqlite("running_task")
            
        
        # 查询是否有正在运行的任务
        task_names=select_sqlite("running_task")
        if task_names:
            for task_name in task_names:
                if task_name[0] == name:
                    await jdbot.send_message(chat_id, f'【监控】 正在运行的任务 {task_name[0]} ,此任务将进入排队')
        
        
        waiting_number = 0       
        # 等待其他任务完成
        while select_sqlite("running_task"):
            close_sqlite()
            await asyncio.sleep(10)
            open_sqlite('/ql/jbot/user/user.db')
            
            waiting_number += 1
            if waiting_number > 150 :
                delete_sqlite("running_task")
                
                
        # 开始任务,更新 running_task 表
        insert_into_sqlite("running_task","task_name",(name,))
        
        messages = event.message.text.split("\n")
              
        change = ""
        for message in messages:
            if "export " not in message:
                continue
            kvs = re.sub(r'.*export ', 'export ', message)
            kv = kvs.replace("export ", "")
            key = kv.split("=")[0]
            value = re.findall(r'[\'|"]([^"]*)[\'|"]', kv)[0]
            configs = rwcon("str")
            # 去掉一些奇怪的符号。
            kv = kv.replace('`', '').replace('*', '')
            key = key.replace('`', '').replace('*', '')
            value = value.replace('`', '').replace('*', '')
            
            # 查询该环境变量是否存在于 all_task 表中
            if select_where_sqlite("all_task","task_data",kv):
                await jdbot.send_message(chat_id, f'【监控】 查询到今日已使用过 {kv} ,忽略')
                continue
            
            # 此任务写入 all_task
            insert_into_sqlite("all_task","task_data",(kv,))
            
            if kv in configs:
                continue
            if key in configs:
                configs = re.sub(f'{key}=("|\').*("|\').*', kv, configs)
                change += f"【替换】{group} 发出的 `[{name}]` 环境变量成功\n`{kv}`\n\n"
                await asyncio.sleep(1) 
                msg = await jdbot.edit_message(msg, change)
            else:
                configs = rwcon("str")
                configs += f'export {key}="{value}"\n'
                change += f"【新增】{group} 发出的 `[{name}]` 环境变量成功\n`{kv}`\n\n"
                msg = await jdbot.edit_message(msg, change)
                await asyncio.sleep(0.5)
            rwcon(configs)
        
        close_sqlite()     
        
        if len(change) == 0:
            await jdbot.send_message(chat_id,f"【取消】{group} 发出的 `{name}` 环境变量无需改动！")
            return
        await asyncio.sleep(1.5)     
        try:
            if "jd_wdz_activityId" in event.message.text:
                RunCommound="jd_task_comment.js"
                msg = await jdbot.send_message(chat_id, r"开始执行微定制脚本，请稍候")
                await cmd('{} {}'.format(TASK_CMD, RunCommound))    
                await jdbot.delete_messages(chat_id, msg)    
            elif "VENDER_ID" in event.message.text:
                RunCommound="KingRan_KR/jd_OpenCard_Force.js"
                msg = await jdbot.send_message(chat_id, r"开始执行入会捡漏脚本，请稍候")
                await cmd('{} {}'.format(TASK_CMD, RunCommound))    
                await jdbot.delete_messages(chat_id, msg)
            elif "jd_zdjr_activityId" in event.message.text:
                RunCommound="jd_zdjr.js"
                msg = await jdbot.send_message(chat_id, r"开始执行组队分豆脚本，请稍候")
                await cmd('{} {}'.format(TASK_CMD, RunCommound))
                await jdbot.delete_messages(chat_id, msg)
            elif "jd_cjhy_activityId" in event.message.text:
                RunCommound="jd_cjzdgf.js"
                msg = await jdbot.send_message(chat_id, r"开始执行CJ组队脚本，请稍候")
                await cmd('{} {}'.format(TASK_CMD, RunCommound))
                await jdbot.delete_messages(chat_id, msg)
            elif "M_WX_ADD_CART_" in event.message.text:
                RunCommound="jd_addCart.js"
                msg = await jdbot.send_message(chat_id, r"开始执行加购有礼脚本，请稍候")
                await cmd('{} {}'.format(TASK_CMD, RunCommound))
                await jdbot.delete_messages(chat_id, msg)
            elif "DAPAINEW" in event.message.text:
                RunCommound="jd_jinggengjcq_dapainew_tool.js"
                msg = await jdbot.send_message(chat_id, r"开始执行大牌联合脚本，请稍候")
                await cmd('{} {}'.format(TASK_CMD, RunCommound))
                await jdbot.delete_messages(chat_id, msg)
            elif "computer_activityIdList" in event.message.text:
                RunCommound="jd_computer.js"
                msg = await jdbot.send_message(chat_id, r"开始执行电脑配件脚本，请稍候")
                await cmd('{} {}'.format(TASK_CMD, RunCommound))
                await jdbot.delete_messages(chat_id, msg)
            else:
                await jdbot.edit_message(msg, f"看到这行字,是有严重BUG!")
        except ImportError:
            pass
    except Exception as e:
        title = "【💥错误💥】"
        name = "文件名：" + os.path.split(__file__)[-1].split(".")[0]
        function = "函数名：" + sys._getframe().f_code.co_name
        tip = '建议百度/谷歌进行查询'
        await jdbot.send_message(chat_id, f"{title}\n\n{name}\n{function}\n错误原因：{str(e)}\n\n{tip}")
        logger.error(f"错误--->{str(e)}")
    finally:
        # 清理 running_task 表
        try:
            open_sqlite('/ql/jbot/user/user.db')
            delete_sqlite("running_task")
            close_sqlite() 
            # user.close()
        except:
            pass
