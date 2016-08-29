#! /usr/bin/python3.4
# -*- coding: utf-8 -*-

import asyncio, os, json, time
import aiohttp_jinja2
import jinja2
import urllib.request
import RPi.GPIO as GPIO
from aiohttp import web
from urllib.parse import unquote
import configparser
import threading
ttim=0

stapwd='abc'
setpwd='lmf2016'
softPath='/home/pi/lmf4/'

kconfig=configparser.ConfigParser()
kconfig.read(softPath+"setting.ini")
shell_ud_t1_set=kconfig.getint("yp","shell_ud_t1_set")
shell_ud_t2u_set=kconfig.getint("yp","shell_ud_t2u_set")
shell_ud_t2d_set=kconfig.getint("yp","shell_ud_t2d_set")
shell_ud_t3_set=kconfig.getint("yp","shell_ud_t3_set")
shell_sdu = kconfig.getint("yp","shell_sdu")
shell_sdd = kconfig.getint("yp","shell_sdd")
stapwd = kconfig.get("yp","stapwd")

seled_cai=[]

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
io_sk=7 #烧烤
io_zq=8 #蒸汽
io_jr=25 #加热管
io_bw=24 #保温
io_hx=23 #回吸
io_ss=18 #上水
io_e3=15 #
io_e4=14 #
GPIO.setup(io_bw, GPIO.OUT)
GPIO.setup(io_jr, GPIO.OUT)
GPIO.setup(io_zq, GPIO.OUT)
GPIO.setup(io_sk, GPIO.OUT)
GPIO.setup(io_hx, GPIO.OUT)
GPIO.setup(io_ss, GPIO.OUT)
GPIO.setup(io_e3, GPIO.OUT)
GPIO.setup(io_e4, GPIO.OUT)
GPIO.output(io_bw, 1)
GPIO.output(io_jr, 1)
GPIO.output(io_zq, 1)
GPIO.output(io_sk, 1)
GPIO.output(io_hx, 1)
GPIO.output(io_ss, 1)
GPIO.output(io_e3, 1)
GPIO.output(io_e4, 1)

moto_1_p=13 #脉宽输出
moto_1_f=19 #正转
moto_1_r=26 #反转
GPIO.setup(moto_1_f, GPIO.OUT)
GPIO.setup(moto_1_r, GPIO.OUT)
GPIO.setup(moto_1_p, GPIO.OUT)
p = GPIO.PWM(moto_1_p, 1500)
p.start(0)

moto_2_p=21 #脉宽输出
moto_2_f=20 #正转
moto_2_r=16 #反转
GPIO.setup(moto_2_f, GPIO.OUT)
GPIO.setup(moto_2_r, GPIO.OUT)
GPIO.setup(moto_2_p, GPIO.OUT)
p2 = GPIO.PWM(moto_2_p, 50)
p2.start(0)

huixiqi=-1
watchdog=0
eTimer1=False
eIntval1=5
eTimer2=False
eIntval2=8
sta_shell=0
sta_onoff=0
shell_up_down=0

'''
shell_sta
0 top stop
1 running
2 bottom stop

shell_up_down
0 to up
2 to bottom

running_sta
0 stop
1 running
'''


@asyncio.coroutine
def return_sta(request):
    global eTimer1,eIntval1,eTimer2,eIntval2,sta_onoff,watchdog
    global shell_up_down,sta_shell,huixiqi
    global stapwd,setpwd,softPath,tempeture_1,tempeture_2,ttim,t

    hhdd=[('Access-Control-Allow-Origin','*')]
    po = yield from request.post()
    if po['p'] == stapwd:
        
        if po['m'] == 'login':
            sta_shell=0
            sta_onoff=0
            tbody= '{"p":"ok"}'
            return web.Response(headers=hhdd ,body=tbody.encode('utf-8'))
        
        elif po['m'] == 'sta':
            watchdog=0
            tbody= '{"shell_sta":'+str(sta_shell)+',"running_sta":'+str(sta_onoff)
            tbody+= ',"tmp1":'+str(tempeture_1)+',"tmp2":'+str(tempeture_2)+'}'
            return web.Response(headers=hhdd ,body=tbody.encode('utf-8'))
        
        elif po['m'] == 'addtime':
            watchdog=0
            #print('old stop at'+str(eIntval1))
            eIntval1+=int(po['d'])
            #print('shall stop at '+str(eIntval1))
            tbody= '{"addtime":'+str(eIntval1-int(time.time()))+'}'
            return web.Response(headers=hhdd ,body=tbody.encode('utf-8'))
                
        elif po['m'] == 'gpioon':
            delaytime=po['t']
            eTimer1=True
            eIntval1=int(time.time())+int(delaytime)
            ttim=time.time()
            print('eTimer1 start')
            #sta_shell=1
            sta_onoff=1
            huixiqi=0
            if po['d']== 'fm':
                GPIO.output(io_zq, 0)
                GPIO.output(io_jr, 0)
                tbody= '{"a":"zq+jr","b":"on"}'
            elif po['d']== 'zq':
                GPIO.output(io_zq, 0)
                tbody= '{"a":"zq","b":"on"}'
            elif po['d']== 'bw':
                GPIO.output(io_bw, 0)
                tbody= '{"a":"bw","b":"on"}'
            elif po['d']== 'sk':
                GPIO.output(io_sk, 0)
                GPIO.output(io_hx, 0)
                tbody= '{"a":"sk+hx","b":"on"}'
            elif po['d']== 'ss':
                GPIO.output(io_ss, 0)
                tbody= '{"a":"ss","b":"on"}'
            print(tbody)
            return web.Response(headers=hhdd ,body=tbody.encode('utf-8'))
                
        elif po['m'] == 'gpiooff':
            if po['d']== 'all':
                sta_onoff=0
                GPIO.output(io_zq, 1)
                GPIO.output(io_jr, 1)
                GPIO.output(io_bw, 1)
                GPIO.output(io_sk, 1)
                GPIO.output(io_ss, 1)
                eTimer1=False
                huixiqi=400
                GPIO.output(io_hx, 0)
                print('huixi on alloff')
                tbody= '{"a":"all","b":"off"}'
            elif po['d']== 'fs':
                GPIO.output(io_bw, 1)
                tbody= '{"a":"bw","b":"off"}'
            elif po['d']== 'sk':
                GPIO.output(io_sk, 1)
                tbody= '{"a":"sk","b":"off"}'
            elif po['d']== 'ms':
                GPIO.output(io_zq, 1)
                GPIO.output(io_jr, 1)
                tbody= '{"a":"ms","b":"off"}'
            print(tbody)
            return web.Response(headers=hhdd ,body=tbody.encode('utf-8'))
                
        elif po['m'] == 'shell':
            if po['d']== 'up' and sta_shell!=1:
                t = threading.Timer(shell_ud_t1_set/1000, tt2)
                GPIO.output(moto_1_r, 0)
                GPIO.output(moto_1_f, 1)
                p.ChangeDutyCycle(100)
                t.start()
                shell_up_down=0
                sta_shell=1
                tbody= '{"a":"shell","b":"up"}'
            elif po['d']== 'dw' and sta_shell!=1:
                t = threading.Timer(shell_ud_t1_set/1000, tt2)
                GPIO.output(moto_1_r, 1)
                GPIO.output(moto_1_f, 0)
                p.ChangeDutyCycle(100)
                t.start()
                shell_up_down=2
                sta_shell=1
                tbody= '{"a":"shell","b":"dw"}'
            elif sta_shell==1:
                tbody= '{"a":"shell","b":"stop"}'
            print(tbody)
            ttim=time.time()
            return web.Response(headers=hhdd ,body=tbody.encode('utf-8'))

        elif po['m'] == 'pump2':
            GPIO.output(moto_2_f, 0)
            GPIO.output(moto_2_r, 1)
            p2.ChangeDutyCycle(int(po['spd']))
            tbody= '{"a":"pump2","b":"'+po['spd']+'"}'
            print(tbody)
            return web.Response(headers=hhdd ,body=tbody.encode('utf-8'))

    else:
        tbody= '{"p":"error"}'
        return web.Response(headers=hhdd ,body=tbody.encode('utf-8'))


def tt2():
    global t,shell_ud_t2d_set,shell_ud_t2u_set,shell_up_down
    if shell_up_down==0:
        shell_t2=shell_ud_t2u_set/1000
    else:
        shell_t2=shell_ud_t2d_set/1000
    t = threading.Timer(shell_t2, tt3)
    p.ChangeDutyCycle(100)
    t.start()
    #print('tt2 '+str(ttim-time.time()))

def tt3():
    global t,shell_ud_t3_set,shell_up_down
    t = threading.Timer(shell_ud_t3_set/1000, ttfin)
    if shell_up_down==0:
        p.ChangeDutyCycle(50)
    else:
        p.ChangeDutyCycle(25)
    t.start()
    #print('tt3 '+str(ttim-time.time()))

def tt4():
    global t
    t = threading.Timer(3, ttfin)
    t.start()
    p.ChangeDutyCycle(4)
    #print('tt4 '+str(ttim-time.time()))

def ttfin():
    global ttim,shell_up_down,sta_shell
    p.ChangeDutyCycle(0)
    sta_shell=shell_up_down
    print('shell run end '+str(ttim-time.time()))


@asyncio.coroutine
def setting(request):
    global shell_ud_t1_set,shell_ud_t2u_set,shell_ud_t2d_set,shell_ud_t3_set
    global shell_sdu,shell_sdd
    global stapwd,setpwd,softPath,seled_cai
    hhdd=[('Access-Control-Allow-Origin','*')]
    tbody= '{"p":"error"}'

    po = yield from request.post()
    if po['m'] == 'l' and po['p'] == setpwd:
        tbody= '{"p":"ok"}'
        return web.Response(headers=hhdd ,body=tbody.encode('utf-8'))

    if po['m'] == 'get' and po['p'] == setpwd:
        tbody = '{"p":"ok",'
        tbody+= '"t1":"'+str(shell_ud_t1_set)+'",'
        tbody+= '"t2u":"'+str(shell_ud_t2u_set)+'",'
        tbody+= '"t2d":"'+str(shell_ud_t2d_set)+'",'
        tbody+= '"t3":"'+str(shell_ud_t3_set)+'",'
        tbody+= '"sdu":"'+str(shell_sdu)+'",'
        tbody+= '"sdd":"'+str(shell_sdd)+'",'
        tbody+= '"stapwd":"'+str(stapwd)+'"}'
        return web.Response(headers=hhdd ,body=tbody.encode('utf-8'))

    if po['m'] == 'w' and po['p'] == setpwd:
        shell_ud_t1_set=int(po['t1'])
        shell_ud_t2u_set=int(po['t2u'])
        shell_ud_t2d_set=int(po['t2d'])
        shell_ud_t3_set=int(po['t3'])
        shell_sdu=po['sdu']
        shell_sdd=po['sdd']
        stapwd=po['stapwd']
        kconfig.set("yp","shell_ud_t1_set",po['t1'])
        kconfig.set("yp","shell_ud_t2u_set",po['t2u'])
        kconfig.set("yp","shell_ud_t2d_set",po['t2d'])
        kconfig.set("yp","shell_ud_t3_set",po['t3'])
        kconfig.set("yp","shell_sdu",str(shell_sdu))
        kconfig.set("yp","shell_sdd",str(shell_sdd))
        kconfig.set("yp","stapwd",stapwd)
        kconfig.write(open(softPath+"setting.ini","w"))
        tbody= '{"p":"ok","w":"ok"}'
        return web.Response(headers=hhdd ,body=tbody.encode('utf-8'))

    if po['m'] == 'addcai':
        scai=po['c']
        if po['s'] == 'true':
            seled_cai.remove(scai)
            #print(seled_cai)
            tbody= '{"p":"dec"}'
        else:
            seled_cai.append(scai)
            #print(seled_cai)
            tbody= '{"p":"add"}'

    if po['m'] == 'get_added_cai':
        tbody= '~'
        for i in seled_cai:
            tbody = tbody+i+';'
        tbody= str(tbody)
        #print(tbody)
        #return tbody
        
    return web.Response(headers=hhdd ,body=tbody.encode('utf-8'))


import serial
tempeture_1=0
tempeture_2=0
@asyncio.coroutine
def get_temp():
    global tempeture_1
    global tempeture_2
    while True:
        # 打开串口  
        ser = serial.Serial("/dev/ttyUSB0",parity=serial.PARITY_ODD,timeout=1)
        ser.write(b'\x01\x03\x00\x00\x00\x04\x44\x09')
        # 获得接收缓冲区字符  
        recv = ser.read(7)
        #print(recv)
        if recv and recv[2]==8:
            tempeture_1=(recv[3]*255+recv[4])/10
            tempeture_2=(recv[5]*255+recv[6])/10
            #print(tempeture_1)
            #print((recv[5]*255+recv[6])/10)
        else:
            print('no data')

        ser.close()
        yield from asyncio.sleep(0.8)    


@asyncio.coroutine
def loop_info():
    global eTimer1,eIntval1,eTimer2,eIntval2,sta_shell,sta_onoff
    global watchdog,huixiqi,p,ttim
    while True:
        yield from asyncio.sleep(0.05)
        watchdog+=1
        if watchdog>100:
            watchdog=0;
            sta_onoff=0
            print('watchdog')
            GPIO.output(io_bw, 1)
            GPIO.output(io_jr, 1)
            GPIO.output(io_zq, 1)
            GPIO.output(io_sk, 1)
            GPIO.output(io_hx, 1)
            
        if huixiqi>0:
            huixiqi-=1
        elif huixiqi==0:
            huixiqi=-1
            GPIO.output(io_hx, 1)
            print('huixiqi stop')
                   
        if eTimer1==True:
            #sta_shell=1
            if int(time.time())>=int(eIntval1):
                sta_onoff=0
                sta_shell=2
                GPIO.output(io_jr, 1)
                GPIO.output(io_zq, 1)
                print('eTimer1 end '+str(time.time()-ttim))
                eTimer1=False
                sta_shell=2
                sta_onoff=0
                huixiqi=400
                GPIO.output(io_hx, 0)
                print('huixiqi on')
                
    return 1


@asyncio.coroutine
def init(loop):    
    global softPath
    app = web.Application(loop=loop)    
    #使用aiohttp_jinja2
    aiohttp_jinja2.setup(app,loader=jinja2.FileSystemLoader(softPath+'templates'))
    
    app.router.add_route('POST', '/sta', return_sta)
    app.router.add_route('POST', '/setting', setting)
    srv = yield from loop.create_server(app.make_handler(), '0.0.0.0', 9001)
    print(' v4 server started at http://0.0.0.0:9001...')               
    return srv

loop = asyncio.get_event_loop()
tasks = [init(loop), loop_info(), get_temp()]#loop_info持续发送状态
loop.run_until_complete(asyncio.wait(tasks))
loop.run_forever()
