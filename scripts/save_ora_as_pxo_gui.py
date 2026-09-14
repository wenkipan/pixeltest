#!/usr/bin/env python3
"""Open an ORA in Pixelorama and save it as a native PXO using GUI automation.

Usage: save_ora_as_pxo_gui.py DISPLAY_NUM input.ora output.pxo
Set PIXELORAMA_BIN to the Pixelorama executable.
"""
import os,sys,time,subprocess
from pathlib import Path

if len(sys.argv)<4:
    raise SystemExit('usage: save_ora_as_pxo_gui.py DISPLAY_NUM ora_path pxo_path')
display_num=int(sys.argv[1]); ora=Path(sys.argv[2]).resolve(); pxo=Path(sys.argv[3]).resolve()
pxo.parent.mkdir(parents=True,exist_ok=True)
exe=Path(os.environ.get('PIXELORAMA_BIN','/mnt/data/pixelorama_install/Pixelorama-Linux-64bit/Pixelorama.x86_64')).resolve()
if not exe.exists(): raise SystemExit(f'Pixelorama binary not found: {exe}')
disp=f':{display_num}'
lock=Path(f'/tmp/.X{display_num}-lock')
if lock.exists(): lock.unlink()
auth=Path('/tmp/pixelorama_xauth'); auth.touch(exist_ok=True)
env=os.environ.copy(); env['DISPLAY']=disp; env['XAUTHORITY']=str(auth)
xvfb=subprocess.Popen(['Xvfb',disp,'-screen','0','1280x768x24','-ac'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,env=env)
time.sleep(1)
app=subprocess.Popen([str(exe),str(ora)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,env=env)
try:
    time.sleep(float(os.environ.get('PIXELORAMA_STARTUP_WAIT','5')))
    code=f'''import pyautogui,time\npyautogui.PAUSE=.18\npyautogui.press("esc")\ntime.sleep(.5)\npyautogui.hotkey("ctrl","shift","s")\ntime.sleep(1.2)\npyautogui.click(650,205)\npyautogui.hotkey("ctrl","a")\npyautogui.write({str(pxo.parent)!r}, interval=.001)\npyautogui.press("enter")\ntime.sleep(.8)\npyautogui.click(625,518)\npyautogui.hotkey("ctrl","a")\npyautogui.write({pxo.name!r}, interval=.001)\ntime.sleep(.3)\npyautogui.click(762,563)\ntime.sleep(4)\n'''
    subprocess.run([sys.executable,'-c',code],env=env,check=True)
    if not pxo.exists(): raise SystemExit(f'pxo not created: {pxo}')
    print(f'created {pxo} ({pxo.stat().st_size} bytes)')
finally:
    app.terminate(); time.sleep(.5)
    if app.poll() is None: app.kill()
    xvfb.terminate(); time.sleep(.3)
    if xvfb.poll() is None: xvfb.kill()
