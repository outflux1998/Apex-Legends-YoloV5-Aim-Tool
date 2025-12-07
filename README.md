# Apex Legends YOLO Aimbot – Real-Time Aim Assist System

This project implements a **real-time aim-assist system** for *Apex Legends*, combining **YOLOv5 object detection**, a **PID-controlled aiming algorithm**, and an **external Raspberry Pi Pico HID mouse emulator**.  
The script captures frames, detects targets using a TensorRT-optimized YOLO model, computes smooth aim adjustments, and sends movement commands to a **listening Raspberry Pi Pico** over HTTP.  
The Pico acts as a USB HID mouse, enabling highly precise and isolated input control.

---

## ✨ Features

### 🎯 YOLOv5 Object Detection
- Custom TensorRT YOLO model (`.engine`) for extremely fast inference  
- Processes a cropped central region for higher FPS  
- Automatically selects the closest valid target  
- CUDA-accelerated processing  

---

### 🧠 PID-Based Aim Adjustment
- Smooth aim correction using a tunable PID controller  
- Independent X/Y error compensation  
- Fully configurable parameters via web UI:  
  - `Kp`, `Ki`, `Kd`  
  - `max_step`  
  - `offset`  
- Prevents jitter and overshoot using step bounding  
- Supports dynamic aim-speed switching via hotkey  

---

### 🖱️ Raspberry Pi Pico HID Mouse Emulation
This project uses a **Raspberry Pi Pico** acting as a USB HID mouse.

Workflow:
1. The Python script sends HTTP POST requests (`/sendxy/` and `/shoot/`)  
2. A Pico web server receives the payload  
3. The Pico outputs **real USB mouse movement** to the PC  

#### Benefits:
- Bypasses OS-level input restrictions  
- Minimizes latency and smoothing  
- Allows extremely fine-grained micro-adjustments  
- Separates the vision/processing pipeline from the input pipeline  

Endpoints:
- `POST /sendxy/` → Moves mouse  
- `POST /shoot/` → Simulates click  

---

### 🔫 Trigger Activation
- Toggles with `ALT`  
- Fires automatically when crosshair overlaps the detected target  
- Uses the Pico HID endpoint for precise click injection  

---

### 🎮 Aim Assist Mode
- Toggles with `P`  
- Activates only while holding the configured mouse button  
- Applies PID-based correction toward the detected target  
- Supports aim-speed modulation  
- Automatically adapts to screen resolution & sensitivity  

---

### 🖥️ High-Performance Capture Pipeline
- Uses **dxcam** for low-latency screen capture  
- Crops to center region for faster processing  
- YOLO inference optimized for smooth real-time performance  

---

### ⚙️ Built-In Flask Configuration Server
Accessible through a browser:

- Adjust PID values (`Kp`, `Ki`, `Kd`)  
- Change mouse button codes  
- Modify aim speed and sensitivity  
- Set offsets, limits, and activation ranges  
- Auto-saves to `config.cfg` without restart  

---

## ⌨️ Hotkeys

| Function | Key |
|---------|-----|
| Toggle Aim Assist | `P` |
| Toggle Trigger Mode | `ALT` |
| Aim-Speed Modifier | `` ` `` (backtick) |
| Shutdown Script | `END` |

---

## 🧩 Tech Stack

- Python  
- YOLOv5 (TensorRT engine)  
- PyTorch CUDA  
- dxcam  
- Flask  
- Win32 API  
- **Raspberry Pi Pico USB HID**  
- Custom PID Controller  

---

## ⚠️ Disclaimer
This project is provided **strictly for educational and research purposes**, especially in the fields of:
- computer vision  
- PID control  
- embedded HID design  
- real-time inference pipelines  

It is **not** intended for online gameplay, competitive use, or violation of any game’s terms of service.

---
**Developed by Rafael Augusto**
