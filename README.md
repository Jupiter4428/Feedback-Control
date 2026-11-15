# Feedback Control (EI444 / CN360)

คลังโค้ดสำหรับการทดลองระบบควบคุมป้อนกลับ (Feedback Control System) โดยจำลองระดับน้ำในถังน้ำ (Water Tank Simulation) พร้อมการเชื่อมต่อผ่าน MQTT, Node-RED และ ThingsBoard ตามสไลด์การเรียนการสอนรายวิชา EI444 / CN360

---

## ซอฟต์แวร์และเครื่องมือที่ต้องใช้ในการทดลอง

ระบบการทดลองนี้ประกอบด้วยซอฟต์แวร์หลัก 4 ส่วนที่ทำงานร่วมกันผ่านโปรโตคอล MQTT ตามแผนภาพสถาปัตยกรรมในเอกสารการสอน:

### 1. Python 3 (พร้อมไลบรารี paho-mqtt)
- หน้าที่: รันแบบจำลองทางกายภาพของถังน้ำ (Physical Model Simulation) ตามสมการอนุพันธ์ (dh/dt)*A = c*u - outflow และประมวลผลอัลกอริทึมควบคุม
- การติดตั้งไลบรารี:
  ```bash
  pip install -r requirements.txt
  ```

### 2. MQTT Broker (แนะนำ Eclipse Mosquitto)
- หน้าที่: ทำหน้าที่เป็นตัวกลางรับ-ส่งข้อมูล (Message Broker) เชื่อมต่อระหว่าง Python Model, Node-RED และ ThingsBoard (พอร์ตเริ่มต้น: 1883)
- รูปแบบการสื่อสาร:
  - ส่งค่าเซนเซอร์ระดับน้ำจาก Python Model ไปยัง Node-RED และ ThingsBoard
  - ส่งคำสั่งควบคุมเปอร์เซ็นต์การเปิดวาล์วจาก Node-RED กลับมายัง Python Model

### 3. Node-RED
- หน้าที่: ทำหน้าที่เป็น Controller Logic ตามสไลด์หน้า 12 และ 15, 21
  - รับข้อมูลระดับน้ำจากแบบจำลองผ่าน MQTT
  - ประมวลผลตรรกะการควบคุมในแต่ละแล็บ (Open-Loop, ON/OFF with Hysteresis, P, PI)
  - ส่งสัญญาณควบคุมวาล์ว (Control Signal) กลับไปสั่งการแบบจำลอง
- การเปิดใช้งาน:
  - เข้าใช้งานผ่านเว็บเบราว์เซอร์ที่: http://localhost:1880
  - นำเข้าไฟล์คอนฟิกจาก `nodered/flows.json`

### 4. ThingsBoard (IoT Dashboard)
- หน้าที่: ทำหน้าที่เป็นหน้าจอแสดงผลข้อมูลการทำงานแบบเรียลไทม์ (Visualization / Dashboard) ตามสไลด์หน้า 12-13
  - แสดงผลระดับน้ำต่อเนื่อง (Water Level Gauge / Timeseries Chart: `water_sensor_depth`)
  - แสดงสถานะเซนเซอร์ดิจิทัล (Digital Limit Switch: `water_sensor_limit_switch`)
  - รับข้อมูลผ่าน MQTT Topic: `v1/devices/me/telemetry`

---

## แผนภาพการเชื่อมต่อระบบ (System Architecture)

```text
  [ ผู้ใช้งานระบุ Target ]
             |
             v
      +--------------+      MQTT (Topic: tank/control/valve)      +------------------+
      |   Node-RED   | -----------------------------------------> |   Python Model   |
      | (Controller) | <----------------------------------------- | (Tank Simulator) |
      +--------------+     MQTT (Sensor: water_sensor_depth)      +------------------+
                                                                            |
                                                                            | MQTT Telemetry
                                                                            v
                                                                  +------------------+
                                                                  |   ThingsBoard    |
                                                                  | (Dashboard UI)   |
                                                                  +------------------+
```

---

## โครงสร้าง Repository (Project Structure)

```text
Feedback Control/
|-- models/
|   |-- __init__.py
|   `-- tank_model.py                # แบบจำลองทางกายภาพของถังน้ำ (Water Tank Physical Model)
|-- lab1_open_loop/
|   `-- open_loop_controller.py      # Lab 1: การควบคุมแบบ Open Loop (Timer-based)
|-- lab2_on_off/
|   `-- on_off_controller.py         # Lab 2: การควบคุมแบบ ON/OFF พร้อม Hysteresis (+-10%)
|-- lab3_p_control/
|   `-- p_controller.py              # Lab 3: การควบคุมแบบ Proportional (P Controller)
|-- lab4_pi_control/
|   `-- pi_controller.py             # Lab 4: การควบคุมแบบ Proportional-Integral (PI Controller)
|-- mqtt_thingsboard/
|   `-- tank_mqtt_service.py         # เซอร์วิสจำลองพร้อมส่งข้อมูล Telemetry ไปยัง ThingsBoard/MQTT
|-- nodered/
|   `-- flows.json                   # Flow สำหรับนำเข้า (Import) ใน Node-RED
|-- docs/
|   `-- issue_templates.md           # รายละเอียดข้อกำหนดของแต่ละ Issue สำหรับผู้รับผิดชอบ
|-- scripts/
|   `-- create_issues.ps1            # สคริปต์สร้าง GitHub Issues อัตโนมัติ
|-- requirements.txt                 # รายการ Dependencies สำหรับ Python
`-- README.md
```

---

## รายละเอียดการทดลอง (Lab 1 - Lab 4)

### Lab 1: Open Loop Control
- แนวคิด: คำนวณระยะเวลาในการเปิดวาล์วล่วงหน้าแบบรอบเดียว (Open Loop) โดยไม่ใช้ Feedback จากเซนเซอร์
- สูตรคำนวณ:
  T = (Target Level - Initial Level) / Fill Rate
- ขั้นตอนการทำงาน:
  1. digital(HIGH) : สั่งเปิดวาล์ว 100%
  2. sleep(T) : หน่วงเวลาตามค่า T ที่คำนวณได้
  3. digital(LOW) : สั่งปิดวาล์ว
- คำสั่งทดสอบ:
  ```bash
  python lab1_open_loop/open_loop_controller.py
  ```

---

### Lab 2: ON/OFF Control with Threshold (Hysteresis)
- แนวคิด: ป้องกันปัญหาหน้าสัมผัสตัดต่อถี่เกินไป (Chattering) จากการกระเพื่อมของน้ำ โดยใช้ Threshold +-10%
  - Upper Threshold = Target * 1.10 (เมื่อระดับน้ำถึงจุดนี้จะสั่งปิดวาล์ว)
  - Lower Threshold = Target * 0.90 (เมื่อระดับน้ำลดต่ำกว่าจุดนี้จะสั่งเปิดวาล์ว)
- คำสั่งทดสอบ:
  ```bash
  python lab2_on_off/on_off_controller.py
  ```

---

### Lab 3: Proportional (P) Controller
- แนวคิด: ปรับขนาดการเปิดวาล์วให้แปรผันตรงกับค่าความคลาดเคลื่อน (Error)
  - Error = Target - Current Level
  - Valve (%) = Kp * Error
- คำสั่งทดสอบ:
  ```bash
  python lab3_p_control/p_controller.py
  ```

---

### Lab 4: Proportional-Integral (PI) Controller
- แนวคิด: กำจัด Steady-State Error (ค่าคลาดเคลื่อนคงค้างจากน้ำที่ไหลออกคงที่) โดยเพิ่ม Integral Action
  - Actuator = (Kp * Error) + (Ki * sum(Error * dt))
- คำสั่งทดสอบ:
  ```bash
  python lab4_pi_control/pi_controller.py
  ```

---

## การเชื่อมต่อ MQTT, ThingsBoard และ Node-RED

1. ติดตั้ง Dependencies ของ Python:
   ```bash
   pip install -r requirements.txt
   ```

2. รันเซอร์วิสจำลองถังน้ำและส่งข้อมูล MQTT:
   ```bash
   python mqtt_thingsboard/tank_mqtt_service.py
   ```

3. นำเข้า Flow ใน Node-RED:
   - เปิด Node-RED ที่ http://localhost:1880
   - ไปที่เมนู Import แล้วเลือกไฟล์ `nodered/flows.json`
