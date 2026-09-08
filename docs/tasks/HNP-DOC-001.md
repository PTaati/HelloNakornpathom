# HNP-DOC-001 — แปลง Word และแยกภาพแผนที่

Status: DONE

Input: `Game-Hello Nakornpathom.docx` และคำอธิบายล่าสุดของผู้ใช้เรื่องสถานีอยู่ฝั่งซ้าย/ถนนกลางตรงไปองค์พระ
Write scope: Markdown ที่ root, `ref/game-document/`, `docs/design/MAP_LAYOUT.md`, script แปลงเอกสาร และลิงก์ในเอกสารแนวทาง

ผลส่งมอบ:

- `Game-Hello Nakornpathom.md`: ถอด 44 ย่อหน้าที่มีข้อความ พร้อมภาพตามลำดับต้นฉบับ คงข้อความเดิม ปรับช่องว่างนำหน้าเพื่อไม่ให้ Markdown แสดงเป็น code block
- แยกภาพ 2 ภาพโดยคง bytes ต้นฉบับ พร้อม source hash และ image hashes ใน manifest
- `MAP_LAYOUT.md`: บันทึกเส้นทางและเกณฑ์ blockout แยกคำอธิบายผู้ใช้ออกจากสิ่งที่เห็นในภาพ
- ไม่แก้ Word และไม่เปลี่ยนฉาก Unity ในงานแปลงเอกสารนี้

Validation: ตรวจว่าภาพตรงกับ bytes ใน DOCX, ย่อหน้าครบ, image links ชี้ไฟล์จริง และ source hash ไม่เปลี่ยนหลังแปลง
