﻿# lmf 8位继电器版,串口测温，2路测温
更新clone下来的代码 git pull，视频要手动

# lmf4
要装的程序

$ sudo apt-get update
$ sudo apt-get install ttf-wqy-zenhei samba-common-bin samba python3-rpi.gpio
$ sudo pip3 install pexpect aiohttp aiohttp_jinja2

禁用屏保和休眠
$ sudo leafpad /etc/lightdm/lightdm.conf 行xserver-command=X -s o -dpms

samba文件共享
$ sudo leafpad /etc/samba/smb.conf  [homes]段
browseable = yes

read only = no
create mask = 0755
directory mask = 0755

增加samba用户
sudo smbpasswd -a pi 输入两次密码，重启

开机运行Python脚本
sudo pcmanfm 复制desktop文件到 /home/pi/.config/autostart

设定有线固定IP，设置中文，设置时区，设置背景,关闭设置里接口，开启1-wire

可以直接在图形界面设置固定IP

设定有线即可
sudo leafpad /etc/network/interfaces

iface eth0 inet static

address 192.168.1.105
netmask 255.255.255.0
gateway 192.168.1.1

# 备用
HDMI输出声音
$ sudo leafpad /boot/config.txt 里面设置HDMI_DRIVER=2,参数是：-o hdmi

/boot/config.txt添加下面 
dtoverlay=w1-gpio-pullup,gpiopin=4
