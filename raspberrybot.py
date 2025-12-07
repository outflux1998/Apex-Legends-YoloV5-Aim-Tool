import dxcam
import torch
import win32api
import cv2
import numpy as np
import time
import math
import requests
import keyboard
from PID import PID
import winsound
import flask
import configparser
from ctypes import windll
from flask import Flask, request, render_template, jsonify
import threading

app = Flask(__name__)
server_running = True


config = configparser.ConfigParser()
config.read('config.cfg')

MONITOR_WIDTH = float(config['Settings']['width'])
MONITOR_HEIGHT = float(config['Settings']['height'])
SENS = int(config['Settings']['sens'])
AIM_SPEED = (float(config['Settings']['aim_speed']))*(1/SENS)
MBLOAD = int(config['Settings']['mb'])
MBLOAD2 = int(config['Settings']['mb2'])
MOUSE_BUTTON_CODE = int(str(MBLOAD), 16)
MOUSE_BUTTON_CODE2 = int(str(MBLOAD2), 16)
PREV_AIM_SPEED = AIM_SPEED
PID_time = 0.015
Kp = 2
Ki = 0.08
Kd = 0
max_step = 25  # 每次位移的最大步长
offset = 4
pid = PID(PID_time, max_step, -max_step, Kp, Ki, Kd)

target_multiply = [0,1.01,1.025,1.05,1.05,1.05,1.05,1.05,1.05,1.05,1.05]
activation_range = 90
first_button_pressed = False
aim_assist = False
aim_assist_toggle = [True]
triggerbot = False
triggerbot_toggle = [True]
server_ip = "192.168.15.118:80"
url = f"http://{server_ip}/sendxy/"
url2 = f"http://{server_ip}/shoot/"


MONITOR_SCALE = 5 #how much the screen shot is downsized by eg. 5 would be one fifth of the monitor dimensions
region = (int(MONITOR_WIDTH/2-MONITOR_WIDTH/MONITOR_SCALE/2),int(MONITOR_HEIGHT/2-MONITOR_HEIGHT/MONITOR_SCALE/2),int(MONITOR_WIDTH/2+MONITOR_WIDTH/MONITOR_SCALE/2),int(MONITOR_HEIGHT/2+MONITOR_HEIGHT/MONITOR_SCALE/2))
x,y,width,height = region
screenshot_center = [int((width-x)/2), int((height-y)/2)]

model = torch.hub.load(r'C:\Users\Shade\yolov5', 'custom', path=r'C:\Users\Shade\Documents\cheats\models\bestL.engine', source='local').cuda()
model.conf = 0.2
model.iou = 0.45
model.maxdet = 1
model.apm = True
#model.classes = [0]
camera = dxcam.create(device_idx=0, output_idx=0, output_color="BGRA")

#start_time = time.time()
x = 1
#counter = 0

print("")
print("")
print("")
print("")
print("CONFIG CARREGADA: ")
print("RESOLUCAO = " + str(MONITOR_WIDTH) + "x" + str(MONITOR_HEIGHT))
print("SENSIBILIDADE = " + str(SENS))
print("VELOCIDADE DA MIRA (BOTAO ESQUERDO) = " + str(AIM_SPEED))
print("")
print("")

# SERVER PARA UPDATEAR A CONFIG

@app.route('/update_settings', methods=['POST'])
def update_settings():
    data = request.get_json()
    
    new_button_code = data.get('MOUSE_BUTTON_CODE')
    new_button_code2 = data.get('MOUSE_BUTTON_CODE2')
    new_Kp = data.get('Kp')
    new_Ki = data.get('Ki')
    new_Kd = data.get('Kd')
    new_max_step = data.get('max_step')
    new_offset = data.get('offset')
    global Kp
    global Ki
    global Kd
    global max_step
    global pid
    global offset

    if new_Kp is not None:
        Kp = float(new_Kp)
        

    if new_Ki is not None:
        Ki = float(new_Ki)
        

    if new_Kd is not None:
        Kd = float(new_Kd)
        

    if new_max_step is not None:
        max_step = int(new_max_step)

    if new_offset is not None:
        global offset
        offset = int(new_offset)
        

    if new_button_code is not None:
        global MOUSE_BUTTON_CODE
        MOUSE_BUTTON_CODE = int(str(new_button_code), 16)
        config['Settings']['mb'] = str(new_button_code)

    if new_button_code2 is not None:
        global MOUSE_BUTTON_CODE2
        MOUSE_BUTTON_CODE2 = int(str(new_button_code2), 16)
        config['Settings']['mb2'] = str(new_button_code2)

    pid = PID(PID_time, max_step, -max_step, Kp, Ki, Kd)
    
    with open('config.cfg', 'w') as configfile:
        config.write(configfile)
    
    return jsonify({'message': 'Update feito com sucesso!'})


@app.route('/')
def index():
    return render_template('index.html', Kp=Kp, Ki=Ki, Kd=Kd, max_step=max_step, MOUSE_BUTTON_CODE=MOUSE_BUTTON_CODE, MOUSE_BUTTON_CODE2=MOUSE_BUTTON_CODE2, offset=offset)

def run_flask_server():
    app.run(host='192.168.15.85', port=80)

if __name__ == '__main__':
    flask_thread = threading.Thread(target=run_flask_server)
    flask_thread.start()

def cooldown(cooldown_bool,wait):
    time.sleep(wait)
    cooldown_bool[0] = True

while True:
        if keyboard.is_pressed('end'):
                server_running = False
                flask_thread.join()
                break

        if keyboard.is_pressed('`'):
            if (first_button_pressed):
                 AIM_SPEED = PREV_AIM_SPEED  # Set AIM_SPEED back to its original value
                 winsound.Beep(1000, 200)  # Play a beep sound
                 first_button_pressed = False

            else:
                PREV_AIM_SPEED = AIM_SPEED
                AIM_SPEED = 7*(1/SENS)  # Set AIM_SPEED to 4.0
                winsound.Beep(1000, 200)  # Play a beep sound
                first_button_pressed = True  # Set the flag
            

        closest_part_distance = 100000
        closest_part = -1
        screenshot = camera.grab(region)
        if screenshot is None: continue
        df = model(screenshot, size=(640, 640)).pandas().xyxy[0]

        #counter+=1
        #if(time.time()-start_time) > x:
        #    fps = "fps:" + str(int(counter/(time.time()-start_time)))
        #    print(fps)
        #    counter = 0
        #    start_time = time.time()
            

        for i in range(0,2):
            try:
                xmin = int(df.iloc[i,0])
                ymin = int(df.iloc[i,1])
                xmax = int(df.iloc[i,2])
                ymax = int(df.iloc[i,3])

                centerX = (xmax-xmin)/2+xmin
                centerY = (ymax-ymin)/2+ymin

                distance = math.dist([centerX,centerY],screenshot_center)

                if int(distance) < closest_part_distance:
                    closest_part_distance = distance
                    closest_part = i

            except:
                print("", end="")

        if keyboard.is_pressed('alt'):
            if triggerbot_toggle[0] == True:
                triggerbot = not triggerbot
                print(triggerbot)
                triggerbot_toggle[0] = False
                thread = threading.Thread(target=cooldown, args=(triggerbot_toggle,0.2,))
                thread.start()

        if keyboard.is_pressed('p'):
            if aim_assist_toggle[0] == True:
                aim_assist = not aim_assist
                print(aim_assist)
                aim_assist_toggle[0] = False
                thread = threading.Thread(target=cooldown, args=(aim_assist_toggle,0.2,))
                thread.start()

        if closest_part != -1:
            xmin = df.iloc[closest_part,0]
            ymin = df.iloc[closest_part,1]
            xmax = df.iloc[closest_part,2]
            ymax = df.iloc[closest_part,3]
            head_center_list = [(xmax-xmin)/2+xmin,(ymax-ymin)/2+ymin]
            if triggerbot == True and win32api.GetAsyncKeyState(MOUSE_BUTTON_CODE2) < 0:
                if screenshot_center[0] in range(int(xmin),int(xmax)) and screenshot_center[1] in range(int(ymin),int(ymax)):
                    try:
                        response = requests.post(url2)

                    except Exception as e:
                        print(f"An error occurred: {str(e)}")

            if aim_assist == True and closest_part_distance < activation_range and win32api.GetKeyState(MOUSE_BUTTON_CODE) < 0:
                xdif = (head_center_list[0] - screenshot_center[0])
                ydif = (head_center_list[1] - screenshot_center[1])
  #w              if abs(xdif) > 20:
  #                  xdif *= 0.2
 #               else:
 #                  xdif *= 0.4
  #              if abs(ydif) > 20:
  #                  ydif *= 0.2
 #               else:
 #                   ydif *= 0.4

                pid_x = int(pid.calculate(xdif, 0))
                pid_y = int(pid.calculate(ydif, 0))

                #if (pid_x > 0): 
                #    pid_x = pid_x + offset
                
                #if (pid_x < 0):
                #    pid_x = pid_x - offset
                    
                payload = {'x': str(pid_x), 'y': str(pid_y)}
                try:
                    # Send the POST request to the server
                    response = requests.post(url, data=payload)
                    
                except Exception as e:
                    print(f"An error occurred: {str(e)}")