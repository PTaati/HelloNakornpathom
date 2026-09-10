# Hello Nakornpathom — กติกาการทำงานของ AI agent

## อ่านก่อนเริ่มงาน

1. อ่าน [GAME_AGENT_SYSTEM.md](GAME_AGENT_SYSTEM.md) สำหรับข้อกำหนดเกม บทบาท และการส่งต่องาน
2. อ่าน [GAME_PRODUCTION_PLAN.md](GAME_PRODUCTION_PLAN.md) สำหรับมาตรฐานโมเดล ลำดับพัฒนา และเกณฑ์ทดสอบ
3. ตรวจไฟล์จริงก่อนแก้ไข: `Game-Hello Nakornpathom.docx` เป็นรายละเอียดต้นฉบับ, `ref/` เก็บภาพอ้างอิง, `hnp-game/` เป็น Unity project
4. คำสั่งล่าสุดของผู้ใช้มีลำดับสูงสุด โดยแพลตฟอร์มหลักคือเว็บบนมือถือแนวนอน แม้ต้นฉบับจะกล่าวถึงผู้เล่นคอมพิวเตอร์
5. อ่านฉบับถอดข้อความ [Game-Hello Nakornpathom.md](Game-Hello%20Nakornpathom.md) และ [MAP_LAYOUT.md](docs/design/MAP_LAYOUT.md) ก่อนทำแมพ ใช้ภาพที่แยกจาก Word ใน `ref/game-document/`; สถานีอยู่ฝั่งซ้าย ออกสู่ถนนกลางและตรงไปองค์พระตามคำอธิบายล่าสุดของผู้ใช้

## ขอบเขต

เอกสารชุดนี้ออกแบบ AI agent สำหรับกระบวนการผลิตเกม ไม่ได้กำหนดให้มี LLM หรือบริการ AI ทำงานขณะผู้เล่นเล่นเกม
การมีแผนนี้ไม่ถือเป็นคำสั่งให้เริ่มสร้างเกมทั้งหมดทันที ให้ทำตามขอบเขตงานที่ผู้ใช้มอบหมายในแต่ละครั้ง
ผู้ใช้อนุญาตให้แบ่งงานเป็น sub-agent 3 บทบาท: `blender_artist`, `unity_engineer`, `designer_tester` โดย agent หลักเป็นผู้ประสานงาน อ่าน [คู่มือทีม](docs/agents/TEAM.md) ก่อนแบ่งงาน
เมื่อมีงานที่แยกทำพร้อมกันได้ ให้มอบหมายตามบทบาทและขอบเขตไฟล์ในคู่มือ ใช้ agent เดิมต่อในเซสชันเมื่อทำได้; งานเล็กหรือมี dependency ให้ทำตามลำดับ ไม่จำเป็นต้องเปิดทุกบทบาททุกครั้ง และต้องเป็นไปตามเครื่องมือ/สิทธิ์ของเซสชันนั้น

## โมเดลและ skill ประจำทีม

- ตัวหลักคงโมเดลใหญ่ที่ผู้ใช้เลือก; `blender_artist` ใช้ `gpt-5.6-sol` / `high`, `unity_engineer` และ `designer_tester` ใช้ `gpt-5.6-terra` / `medium` ตาม `.codex/agents/*.toml`
- เมื่อเครื่องมือ spawn ของเซสชันไม่รองรับ custom agent profile โดยตรง ให้ส่ง `model` และ `reasoning_effort` ตามรายการข้างต้นอย่างชัดเจน พร้อม task packet และ path ของ skill; ใช้ `fork_turns="none"` หรือประวัติเท่าที่จำเป็น เพราะ full-history fork สืบทอดโมเดลหลัก ห้ามเรียก agent เก่าที่ใช้โมเดลเดิมแล้วอ้างว่าเปลี่ยนโมเดลแล้ว
- Blender อ่าน [hnp-blender-pipeline](.agents/skills/hnp-blender-pipeline/SKILL.md), Unity อ่าน [hnp-unity-web](.agents/skills/hnp-unity-web/SKILL.md), Designer/QA อ่าน [hnp-design-qa](.agents/skills/hnp-design-qa/SKILL.md) เมื่อทำงานตรงบทบาท Skill ติดตั้งระดับ repository และเลือกอัตโนมัติได้
- ใช้ Luna เฉพาะงานอ่าน log/ตรวจรายการที่ root แตกเป็นงานสั้นชัดเจนเมื่อช่วยประหยัดจริง ไม่เปิด agent เพิ่มค้างไว้; งานยากให้ส่งหลักฐานกลับตัวหลักก่อนเพิ่มระดับโมเดล

## วิธีทำงาน

- ก่อนแก้ไข สรุป task ID, เป้าหมาย, input, ไฟล์ที่จะเขียน และ acceptance criteria
- ตรวจสถานะเครื่องมือจริง ห้ามเดาชื่อ MCP tool, endpoint, port หรือรายงานว่าเชื่อมต่อสำเร็จโดยไม่มีผลเรียกใช้งาน
- ใช้ Blender สร้างโมเดลต้นฉบับ เก็บ `.blend` นอก Unity Assets และส่งออก FBX/texture ให้ Unity
- ใช้ Unity MCP ที่ค้นพบจริงสำหรับตรวจ scene, import, prefab, Play Mode, console และ test ตาม capability ที่มี
- งานที่แก้ Unity Editor, scene, prefab, ProjectSettings หรือ import asset ให้มีผู้เขียนเพียงหนึ่งรายในเวลาเดียวกัน
- ห้ามแก้ `Library/`, `Temp/`, `Obj/`, `Logs/`, `UserSettings/` หรือ package cache เพื่อเป็น implementation
- รักษา `.meta` และ GUID ของ asset เดิม ย้าย asset ผ่าน Unity เมื่อทำได้ ห้ามสร้าง `.meta` ด้วย GUID ที่เดาเอง
- อย่าเขียนทับ scene ที่มีงานค้างใน Editor ตรวจ dirty state และ save/checkpoint ก่อนเปลี่ยนฉาก
- อย่าอัปเกรด Unity หรือ package โดยไม่เกี่ยวกับงาน ใช้เวอร์ชันในโปรเจกต์เป็นฐาน
- เก็บ ref เดิมโดยไม่แก้ไข ระบุ source ของโมเดลและภาพที่ใช้ทุกครั้ง ข้อมูลที่ยังไม่มีให้ติดป้าย `provisional`
- ทำงานย่อยให้ครบวงจร: สร้าง → ตรวจใน Blender → import → ตรวจใน Unity → ทดสอบ Web build เมื่อเกี่ยวข้อง
- เมื่อไม่ผ่าน ให้บันทึกสาเหตุ แก้ แล้วทดสอบซ้ำเฉพาะส่วนที่เกี่ยวข้อง หากเกิด blocker เดิมซ้ำ 3 ครั้งให้เก็บ log และเปลี่ยนวิธีหรือรายงานข้อมูลที่ขาด
- แยกสถานะ `PASS`, `FAIL`, `BLOCKED`, `NOT RUN` เสมอ screenshot อย่างเดียวไม่ใช่หลักฐานว่าเกมทำงานครบ
- ห้ามรายงานว่าผ่านมือถือจริงจากการใช้ desktop emulator หรือ Unity Game View

## การส่งมอบ

รายงานไฟล์ที่เปลี่ยน ผลทดสอบพร้อมตำแหน่งหลักฐาน ข้อจำกัด และงานถัดไป อัปเดต task record หลังจบงาน
งานโมเดลต้องมี source, export, preview, ขนาด/triangle/material report และผลตรวจ prefab ใน Unity
งานเกมต้องมีวิธีเล่นเพื่อทวนผล งานทดสอบต้องระบุ build, device, browser, ขั้นตอน และ expected/actual
