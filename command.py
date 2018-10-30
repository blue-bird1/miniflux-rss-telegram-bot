#codoing:utf-8
import io
import json
import telegram 
from inspect import *
from client import new_client
from constant import NO_BIND_MSG, CREATE_OK_MSG, ADD_FEED_OK_MSG, ID_NO_INT_MSG
from telegram import InputFile
from client import new_client
from module import DBSession
from module.user import User
from config import admin_client
from miniflux import ClientError


def start(bot, update):
    """
    欢迎使用rss机器人,使用/help获取更多帮助
    """
    bot.send_message(chat_id=update.message.chat_id, text=getdoc(globals()[getframeinfo(currentframe()).function]))

def bind(bot, update, args):
    """
    usage: /bind username password
    """
    if len(args) != 2:
       bot.send_message(chat_id=update.message.chat_id, text=getdoc(globals()[getframeinfo(currentframe()).function]))
       return
    session = DBSession()
    user = User(id=update.message.chat_id, username=args[0], password=args[1]) 
    session.merge(user)
    session.commit()
    session.close()
    bot.send_message(chat_id=update.message.chat_id, text=BIND_OK_MSG)

def new_user(bot, update, args):
    """
    usage: /new_user username password
    """
    if len(args) != 2:
       bot.send_message(chat_id=update.message.chat_id, text=getdoc(globals()[getframeinfo(currentframe()).function]))
       return
    try:
        admin_client.create_user(args[0],args[1], False)    
    except ClientError as e: # pylint: disable=invalid-name
        bot.send_message(chat_id=update.message.chat_id, text=e.get_error_reason())
        return 
    bot.send_message(chat_id=update.message.chat_id, text=CREATE_OK_MSG)
    
def add_feed(bot, update, args):
    """
    usage: /addfeed url category_id
    """
    if len(args) != 2: 
       bot.send_message(chat_id=update.message.chat_id, text=ADD_FEED_USAGE_MSG)
       return
    if not args[1].isdecimal():
       bot.send_message(chat_id=update.message.chat_id, text=ID_NO_INT_MSG)
       return
    try:
        client = new_client(update.message.chat_id)
    except UserNotBindError as e: # pylint: disable=invalid-name
        bot.send_message(chat_id=update.message.chat_id, text=NO_BIND_MSG)
        return    
    try:
        client.create_feed(args[0], int(args[1]))
    except ClientError as e: # pylint: disable=invalid-name
        bot.send_message(chat_id=update.message.chat_id, text=e.get_error_reason())
        return
    bot.send_message(chat_id=update.message.chat_id, text=ADD_FEED_OK_MSG)


def export(bot, update):
    """
    export user feed to opml file
    """
    try:
        client = new_client(update.message.chat_id)
    except UserNotBindError:
        bot.send_message(chat_id=update.message.chat_id, text=NO_BIND_MSG)
        return    
    try:
         _ = client.export()
    except ClientError as error: 
        bot.send_message(chat_id=update.message.chat_id, text=error.get_error_reason())
        return
    opml_file = io.BytesIO(bytes(_,'utf-8'))
    bot.send_document(chat_id=update.message.chat_id, document=opml_file, filename="export.opml")
    opml_file.close()

def discover(bot, update, args):
    """    
    usage: /discover url
    """
    if len(args) != 1: 
       bot.send_message(chat_id=update.message.chat_id, text=getdoc(globals()[getframeinfo(currentframe()).function]))
       return
    try:
        client = new_client(update.message.chat_id)
    except UserNotBindError:
        bot.send_message(chat_id=update.message.chat_id, text=NO_BIND_MSG)
        return    
    try:
        ret  = client.discover(args[0])
    except ClientError as error: 
        bot.send_message(chat_id=update.message.chat_id, text=error.get_error_reason())
        return
    bot.send_message(chat_id=update.message.chat_id,text="发现成功 订阅地址{}".format(ret[0]['url'])) 

def get_entries(bot, update, args):
    """
    usage: /get_entries num
    """
    if len(args) != 1: 
       bot.send_message(chat_id=update.message.chat_id, text=getdoc(globals()[getframeinfo(currentframe()).function]))
       return
    try:
        client = new_client(update.message.chat_id)
    except UserNotBindError:
        bot.send_message(chat_id=update.message.chat_id, text=NO_BIND_MSG)
        return    
    try:
        ret  = client.get_entries(limit=args[0])
    except ClientError as error: 
        bot.send_message(chat_id=update.message.chat_id, text=error.get_error_reason())
        return
    for _ in ret['entries']:
        bot.send_message(chat_id=update.message.chat_id,text=_['url'],parse_mode=telegram.ParseMode.HTML)
     
