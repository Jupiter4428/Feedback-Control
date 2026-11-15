# รายละเอียดข้อกำหนดและคำอธิบายงานสำหรับ GitHub Issues (EI444 / CN360 Feedback Control)

เอกสารนี้รวบรวมเนื้อหาสำหรับสร้าง GitHub Issues ของ Lab 1 ถึง Lab 4 โดยไม่มีการใช้อิโมจิ พร้อมระบุไฟล์ที่ผู้รับผิดชอบต้องทำงานด้วยอย่างชัดเจน

---

## Issue 1: Lab 1 - Open Loop Control
- ผู้รับผิดชอบ (Assignee): saifadecha07
- หัวข้อ (Title): [Lab 1] Implement and Verify Open Loop Control System

### เนื้อหา (Body):
```markdown
### 1. วัตถุประสงค์ (Objective)
ศึกษาและพัฒนาการควบคุมระดับน้ำในถังแบบวงเปิด (Open Loop Control System) โดยใช้วิธีคำนวณระยะเวลาการเปิดวาล์วล่วงหน้า (Timer-based Control) จากแบบจำลองทางกายภาพ โดยไม่มีการใช้สัญญาณป้อนกลับ (Feedback) จากเซนเซอร์วัดระดับน้ำในระหว่างการทำงาน

### 2. ไฟล์ที่เกี่ยวข้องและต้องทำงานด้วย (Relevant Files)
- lab1_open_loop/open_loop_controller.py : ไฟล์หลักที่ต้องเขียนโค้ดและรันเพื่อควบคุมการเปิด-ปิดวาล์วตามเวลาที่คำนวณได้
- models/tank_model.py : โมเดลถังน้ำทางฟิสิกส์สำหรับจำลองพลศาสตร์การไหลของน้ำ (อ่านทำความเข้าใจและเรียกใช้งาน)
- README.md : บันทึกผลการทดลอง สรุปข้อดีและข้อจำกัดของระบบแบบ Open Loop

### 3. รายละเอียดงานที่ต้องดำเนินการ (Tasks and Requirements)
- การคำนวณทางทฤษฎีด้วยตนเอง (Manual Calculation):
  - กำหนดค่าเริ่มต้น: ระดับน้ำปัจจุบัน (h0) = 20 เมตร, ระดับน้ำเป้าหมาย (h_target) = 80 เมตร
  - กำหนดอัตราการปล่อยน้ำสูงสุดของวาล์ว: 1 เมตร/วินาที (เมื่อพื้นที่หน้าตัดถัง A = 1 ตารางเมตร)
  - คำนวณหาระยะเวลาในการเปิดวาล์ว T จากสูตร:
    T = (h_target - h0) / fill_rate = (80 - 20) / 1 = 60 วินาที
- การตรวจสอบและทดสอบโค้ดใน lab1_open_loop/open_loop_controller.py:
  - จำลองคำสั่ง digital(HIGH) เพื่อเปิดวาล์ว 100%
  - หน่วงเวลาตามค่า T ที่คำนวณได้ (sleep(T))
  - จำลองคำสั่ง digital(LOW) เพื่อปิดวาล์วเมื่อครบกำหนดเวลา
  - ตรวจสอบว่าระดับน้ำสุดท้ายถึง 80 เมตรตามเป้าหมายหรือไม่
- การวิเคราะห์ผลและข้อจำกัดของระบบ:
  - สังเกตและบันทึกผลว่า หากมีสัญญาณรบกวน (Disturbance) เช่น เกิดน้ำรั่วซึมออกจากถัง หรือค่าอัตราการไหลคลาดเคลื่อน ระบบ Open Loop จะไม่สามารถรับรู้และไม่สามารถชดเชยระดับน้ำให้ถูกต้องได้
```

---

## Issue 2: Lab 2 - ON/OFF Control with Threshold (Hysteresis)
- ผู้รับผิดชอบ (Assignee): Jupiter4428
- หัวข้อ (Title): [Lab 2] Implement ON/OFF Control with Hysteresis Threshold and Node-RED Flow

### เนื้อหา (Body):
```markdown
### 1. วัตถุประสงค์ (Objective)
พัฒนาระบบควบคุมระดับน้ำแบบป้อนกลับชนิดปิด-เปิด (Closed-Loop ON/OFF Control) พร้อมประยุกต์ใช้แถบควบคุมฮิสเทอรีซิส (Hysteresis Band / Threshold +-10%) เพื่อป้องกันปัญหาหน้าสัมผัสสวิตช์หรือวาล์วตัดต่อถี่เกินไป (Chattering/Oscillation) จากการกระเพื่อมของผิวน้ำ

### 2. ไฟล์ที่เกี่ยวข้องและต้องทำงานด้วย (Relevant Files)
- lab2_on_off/on_off_controller.py : ไฟล์หลักสำหรับเขียนคลาส OnOffController กำหนดตรรกะ Upper/Lower Threshold และรันลูปควบคุม
- nodered/flows.json : ไฟล์โฟลว์ Node-RED สำหรับนำเข้า (Import) เพื่อสร้างบล็อกควบคุมและหน้าจอสั่งการผ่าน MQTT
- models/tank_model.py : ใช้อ่านค่าเซนเซอร์ระดับน้ำและสั่งงานวาล์วน้ำในแบบจำลอง
- README.md : บันทึกผลการทดลองและรูปแบบของ Limit Cycle ที่เกิดขึ้น

### 3. รายละเอียดงานที่ต้องดำเนินการ (Tasks and Requirements)
- พัฒนาตรรกะ Hysteresis (+-10% Threshold):
  - กำหนดระดับน้ำเป้าหมาย (Target) เช่น 50 เมตร
  - คำนวณ Upper Threshold = Target * 1.10 = 55 เมตร
  - คำนวณ Lower Threshold = Target * 0.90 = 45 เมตร
  - เงื่อนไขการสั่งงานวาล์ว:
    - หากระดับน้ำ <= Lower Threshold ให้สั่งเปิดวาล์ว 100% (ON)
    - หากระดับน้ำ >= Upper Threshold ให้สั่งปิดวาล์ว 0% (OFF)
    - หากระดับน้ำอยู่ในช่วงระหว่าง Lower และ Upper Threshold ให้คงสถานะวาล์วล่าสุดไว้
- การเชื่อมต่อกับ Node-RED และจำลองน้ำไหลออก:
  - กำหนดตัวแปรอัตราการไหลออก (Outflow) ให้น้อยกว่าอัตราการไหลเข้าสูงสุด
  - ตรวจสอบฟังก์ชันควบคุมใน nodered/flows.json ให้ทำงานตรงกับตรรกะ Hysteresis
- การทดสอบและประเมินผล:
  - รันการทดสอบผ่าน lab2_on_off/on_off_controller.py
  - ตรวจสอบว่าระบบสามารถรักษาระดับน้ำให้อยู่ในกรอบ 45 - 55 เมตรได้โดยที่วาล์วไม่เกิดการสลับถี่ผิดปกติ
```

---

## Issue 3: Lab 3 - Proportional (P) Controller
- ผู้รับผิดชอบ (Assignee): Montrinut
- หัวข้อ (Title): [Lab 3] Implement and Evaluate Proportional (P) Controller

### เนื้อหา (Body):
```markdown
### 1. วัตถุประสงค์ (Objective)
ศึกษาระบบควบคุมแบบป้อนกลับชนิดสัดส่วน (Proportional Control: P Control) โดยควบคุมการเปิดของวาล์วน้ำแบบต่อเนื่อง (0% - 100%) ให้แปรผันตรงกับขนาดของค่าความคลาดเคลื่อน (Error) พร้อมสังเกตพฤติกรรม Steady-State Error

### 2. ไฟล์ที่เกี่ยวข้องและต้องทำงานด้วย (Relevant Files)
- lab3_p_control/p_controller.py : ไฟล์หลักสำหรับพัฒนาคลาส PController, ฟังก์ชันคำนวณ Error และการขยายสัญญาณ Kp
- models/tank_model.py : โมเดลถังน้ำที่ต้องรับค่าการเปิดวาล์วแบบเปอร์เซ็นต์ (Continuous Input)
- README.md : บันทึกผลการทดสอบการปรับค่า Kp และสรุปสาเหตุการเกิด Steady-State Error

### 3. รายละเอียดงานที่ต้องดำเนินการ (Tasks and Requirements)
- พัฒนา P Controller Logic:
  - คำนวณค่า Error: Error = Target - Current Level
  - คำนวณสัญญาณควบคุมส่งไปยังวาล์ว: Actuator = Kp * Error
  - ทำการจำกัดขอบเขตค่าสัญญาณควบคุม (Clamping) ให้อยู่ในช่วง 0.0 ถึง 1.0 (0% ถึง 100%) เสมอ
- การทดลองปรับค่าเกนขยาย Kp (Gain Tuning):
  - ทดสอบรัน lab3_p_control/p_controller.py ด้วยค่า Kp ที่แตกต่างกัน (เช่น 0.02, 0.05, 0.1)
  - สังเกตความเร็วในการตอบสนอง (Rise Time) และการแกว่ง (Overshoot)
- การทดลองและวิเคราะห์ Steady-State Error:
  - กำหนดให้ถังน้ำมีอัตราการไหลออกคงที่ (Constant Outflow เช่น 0.3 ลูกบาศก์เมตร/วินาที)
  - สังเกตและอธิบายว่าทำไมระดับน้ำจึงหยุดนิ่งต่ำกว่าเป้าหมายเสมอเมื่อใช้เพียง P Controller เพียงอย่างเดียว (เกิด Offset ค้าง)
```

---

## Issue 4: Lab 4 - Proportional-Integral (PI) Controller
- ผู้รับผิดชอบ (Assignee): 6710615151
- หัวข้อ (Title): [Lab 4] Implement PI Controller and Eliminate Steady-State Error

### เนื้อหา (Body):
```markdown
### 1. วัตถุประสงค์ (Objective)
พัฒนาระบบควบคุมระดับน้ำแบบสัดส่วนและปริพันธ์ (Proportional-Integral Control: PI Control) เพื่อขจัดค่าความคลาดเคลื่อนคงค้าง (Steady-State Error) ที่พบจากการทดลองใน Lab 3 ให้ระดับน้ำลู่เข้าสู่ค่าเป้าหมายได้อย่างแม่นยำ

### 2. ไฟล์ที่เกี่ยวข้องและต้องทำงานด้วย (Relevant Files)
- lab4_pi_control/pi_controller.py : ไฟล์หลักสำหรับพัฒนาคลาส PIController, การคำนวณผลรวม Error สะสม และระบบป้องกัน Integral Windup
- mqtt_thingsboard/tank_mqtt_service.py : ตรวจสอบการส่งค่าตัวแปรของ PI Controller ขึ้นสู่ระบบ MQTT/ThingsBoard
- nodered/flows.json : ตรวจสอบตรรกะในฟังก์ชันของ Node-RED ในโหมด 'pi'
- README.md : บันทึกผลการเปรียบเทียบประสิทธิภาพระหว่าง P Controller และ PI Controller

### 3. รายละเอียดงานที่ต้องดำเนินการ (Tasks and Requirements)
- พัฒนา PI Controller Logic:
  - คำนวณเทอมสัดส่วน: Term_P = Kp * Error
  - คำนวณเทอมปริพันธ์: Integral = Integral + (Error * dt)
  - คำนวณเทอมสะสม: Term_I = Ki * Integral
  - สัญญาณควบคุมรวม: Valve Output = Term_P + Term_I
  - ใส่ระบบจำกัดค่าผลรวม (Anti-windup Clamping) เพื่อไม่ให้ค่า Integral สะสมเกินขนาดจนเกิด Overshoot รุนแรง
- การทดสอบและปรับแต่งค่า Kp และ Ki:
  - ทดสอบรัน lab4_pi_control/pi_controller.py ร่วมกับสภาวะที่มี Outflow คงที่
  - สังเกตพฤติกรรมว่าเทอม Integral สามารถดันระดับน้ำให้ขจัด Steady-State Error จนระดับน้ำเข้าสู่ค่าเป้าหมายได้อย่างสมบูรณ์ (Error ลู่เข้าสู่ 0)
- การสรุปและเปรียบเทียบผล:
  - เปรียบเทียบกราฟการตอบสนองเชิงเวลา (Time Response) ระหว่าง Lab 3 (Pure P) และ Lab 4 (PI)
```
