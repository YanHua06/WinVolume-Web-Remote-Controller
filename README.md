# WinVolume-Web-Remote-Controller
A Python script to remotely control Windows system volume via Web UI over LAN.
##Use
To auto-launch with foobar2000, create a .bat file with the following content:
'''
@echo off
:: 启动后台服务
start "" pythonw "%~dp0app.py"

:: 启动播放器并等待它关闭 (/wait)
start /wait "" "C:\YOUR_PATH\foobar2000\foobar2000.exe"

:: 播放器关闭后，强行杀掉 Python 进程
taskkill /f /im pythonw.exe
exit
'''
