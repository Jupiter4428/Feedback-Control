# Feedback Control (EI444 / CN360)

คลังโค้ดสำหรับการทดลองระบบควบคุมป้อนกลับ (Feedback Control System) โดยจำลองระดับน้ำในถังน้ำ (Water Tank Simulation) พร้อมการเชื่อมต่อผ่าน MQTT, Node-RED และ Thingsboard ตามสไลด์การเรียนการสอนรายวิชา EI444 / CN360

---

## 📂 โครงสร้าง Repository (Project Structure)

```text
Feedback Control/
├── models/
│   └── tank_model.py                # แบบจำลองทางกายภาพของถังน้ำ (Water Tank Physical Model)
├── lab1_open_loop/
│   └── open_loop_controller.py      # Lab 1: การควบคุมแบบ Open Loop (คำนวณเวลา Timer เพื่อเปิด/ปิดวาล์ว)
├── lab2_on_off/
│   └── on_off_controller.py         # Lab 2: การควบคุมแบบ ON/OFF พร้อม Hysteresis (Threshold +-10%)
├── lab3_p_control/
│   └── p_controller.py              # Lab 3: การควบคุมแบบ Proportional (P Controller)
├── lab4_pi_control/
│   └── pi_controller.py             # Lab 4: การควบคุมแบบ Proportional-Integral (PI Controller)
├── mqtt_thingsboard/
│   └── tank_mqtt_service.py         # เซอร์วิสจำลองพร้อมส่งข้อมูล Telemetry ไปยัง Thingsboard/MQTT
├── nodered/
│   └── flows.json                   # ตัวอย่าง Flow สำหรับ Import ใช้งานใน Node-RED
├── requirements.txt                 # รายการ Dependencies สำหรับ Python
└── README.md
```

---

## 🧪 รายละเอียดการทดลอง (Lab 1 - Lab 4)

### 📌 Lab 1: Open Loop Control
- **แนวคิด**: คำนวณระยะเวลาในการเปิดวาล์วล่วงหน้าแบบรอบเดียว (Open Loop) โดยไม่ใช้ Feedback จากเซนเซอร์
- **สูตร**:
  $$T = \frac{\text{Target Level} - \text{Initial Level}}{\text{Flow Rate}}$$
- **การทำงาน**:
  ```python
  digital(HIGH)  # สั่งเปิดวาล์ว 100%
  sleep(T)       # หน่วงเวลาตามที่คำนวณได้
  digital(LOW)   # สั่งปิดวาล์ว
  ```
- **รันแล็บ**:
  ```bash
  python lab1_open_loop/open_loop_controller.py
  ```

---

### 📌 Lab 2: ON/OFF Control with Threshold (Hysteresis)
- **แนวคิด**: เพื่อแก้ปัญหาการสลับเปิด/ปิดวาล์วถี่เกินไป (Chattering) จากการกระเพื่อมของน้ำ มีการใช้ Threshold $\pm 10\%$
  - **Upper Threshold** = $\text{Target} \times 1.10$ (เมื่อระดับน้ำถึงจุดนี้จะสั่งปิดวาล์ว)
  - **Lower Threshold** = $\text{Target} \times 0.90$ (เมื่อระดับน้ำลดต่ำกว่าจุดนี้จะสั่งเปิดวาล์ว)
- **รันแล็บ**:
  ```bash
  python lab2_on_off/on_off_controller.py
  ```

---

### 📌 Lab 3: Proportional (P) Controller
- **แนวคิด**: ปรับขนาดการเปิดวาล์วให้แปรผันตรงกับค่าความคลาดเคลื่อน (Error)
  $$\text{Error} = \text{Target} - \text{Current Level}$$
  $$\text{Valve (\%)} = K_p \times \text{Error}$$
- **รันแล็บ**:
  ```bash
  python lab3_p_control/p_controller.py
  ```

---

### 📌 Lab 4: Proportional-Integral (PI) Controller
- **แนวคิด**: ขจัดปัญหา Steady-State Error (ค่าคลาดเคลื่อนคงค้างจากน้ำที่ไหลออกคงที่) โดยเพิ่ม Integral Term
  $$\text{Actuator} = K_p \times \text{Error} + K_i \times \sum (\text{Error} \times \Delta t)$$
- **รันแล็บ**:
  ```bash
  python lab4_pi_control/pi_controller.py
  ```

---

## 🌐 การเชื่อมต่อ MQTT, ThingsBoard และ Node-RED

### 1. ติดตั้ง Dependencies
```bash
pip install -r requirements.txt
```

### 2. รัน Service จำลองพร้อมส่งข้อมูล MQTT / Thingsboard
```bash
python mqtt_thingsboard/tank_mqtt_service.py
```
- ข้อมูล Telemetry จะส่งไปยัง Topic: `v1/devices/me/telemetry`
- รองรับการแสดงผล:
  - `water_sensor_depth` (ระดับน้ำแบบต่อเนื่อง)
  - `water_sensor_limit_switch` (เซนเซอร์ดิจิทัล 0 หรือ 1)
  - `valve_position` (เปอร์เซ็นต์การเปิดวาล์ว)

### 3. นำเข้า Flow ใน Node-RED
- เปิดโปรแกรม Node-RED (พอร์ตปกติคือ `http://localhost:1880`)
- ไปที่เมนู **Import** แล้วเลือกไฟล์ `nodered/flows.json`
