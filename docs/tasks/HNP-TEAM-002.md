# HNP-TEAM-002 — โมเดลแยกบทบาทและ skill เฉพาะเกม

- Date: 2026-09-09
- Owner: root / Producer
- Status: DONE
- Goal: ใช้โมเดลย่อยตามความยากและติดตั้ง skill Blender, Unity, Designer/QA ให้ใช้งานในโปรเจกต์ได้จริง
- Inputs: คำสั่งผู้ใช้ให้ setup ตามข้อเสนอ, baseline 3 เอกสาร, source/export/ref/project/tools จริง และ OpenAI Docs
- Write scope: `.codex/config.toml`, `.codex/agents/*.toml`, `.agents/skills/hnp-*/SKILL.md`, `AGENTS.md`, `docs/agents/TEAM.md`, task นี้ และ `reports/team-setup/`
- Validation dependency: PyYAML 6.0.3 ติดตั้งเฉพาะ `tools/.python/` ที่ gitignore อยู่ เพื่อรันตัวตรวจ skill; ไม่เปลี่ยน package Unity หรือ Python global
- Editor owner: none; ไม่มี import/Play Mode/scene change/build

## ผลตั้งค่า

| บทบาท | Model | Reasoning | Skill |
|---|---|---|---|
| ตัวหลัก | คงโมเดลใหญ่ที่ผู้ใช้เลือก | คงค่าเดิม | ใช้ skill ตาม task |
| Blender | gpt-5.6-sol | high | hnp-blender-pipeline |
| Unity | gpt-5.6-terra | medium | hnp-unity-web |
| Designer + QA | gpt-5.6-terra | medium | hnp-design-qa |

Child default Terra/medium, limit 3 child threads ไม่รวม root. Luna/low เป็นตัวเลือกงานสั้นอ่าน log/ตรวจรายการเมื่อ root แตกงานชัดเจน ไม่เปิดเพิ่มประจำ
ตั้งค่า custom agent ระดับ repository ตามเอกสารปัจจุบัน; ไม่เปลี่ยน global settings, permission mode หรือโมเดลหลัก

## Acceptance / evidence

| ตรวจ | สถานะ | หลักฐาน |
|---|---|---|
| TOML 4 ไฟล์ parse และ profile/skill path ครบ | PASS | `reports/team-setup/validation.json` |
| Skill 3 ชุดผ่าน official quick_validate.py | PASS | `reports/team-setup/validation.json`; PyYAML ใน tools/.python |
| Codex ค้นพบ skill จริง | PASS | CLI 0.153.2 `debug prompt-input` ผ่าน installed node entrypoint exit 0 และพบชื่อทั้ง 3; prompt content ไม่เก็บเพื่อไม่คัดลอก context ส่วนตัว |
| Spawn ด้วยโมเดลใหม่และอ่าน skill จริง | PASS | collaboration.spawn_agent ใช้ fork_turns=none, explicit model/reasoning; `/root/blender_artist_sol`, `/root/unity_engineer_terra`, `/root/designer_tester_terra` ส่งผลกลับครบ |
| ทดลองใช้ skill แบบ read-only | PASS | `reports/team-setup/validation.md` สรุปโจทย์ ผลสังเกต และขอบเขตที่ไม่ได้รัน |
| กติกา Editor owner/model escalation/handoff | PASS | TEAM.md และ AGENTS.md; Unity agent ใช้ staging และรอส่งสิทธิ์ก่อน import |

## ข้อจำกัดเครื่องมือ (แยกจาก acceptance งานติดตั้ง)

- PASS: Blender CLI 5.2.1 LTS ใช้งานได้จาก executable จริง
- PASS: Unity relay initialize และ tools/list ตอบกลับ; `reports/team-setup/unity-tools.json`
- BLOCKED: Unity Editor operations ผ่าน MCP เพราะ relay คืน tools ว่าง; ยังไม่ได้พิสูจน์ import/prefab/Play Mode/build
- NOT RUN: IDE skill selector UI, Blender scene/FBX round-trip, เกม Web และมือถือจริง งานนี้ตรวจ setup ไม่ใช่ release gate

ตอนตรวจ CLI พบ PowerShell ปิดการรัน npm .ps1; ใช้ .cmd สำหรับ version และ node entrypoint จริงสำหรับ prompt discovery สำเร็จ โดยไม่เปลี่ยน ExecutionPolicy
Sandbox ไม่ให้ pip ออกเครือข่าย; การติดตั้ง PyYAML เฉพาะโปรเจกต์ผ่าน approval review แล้วสำเร็จ ไม่มี approval rejection ค้าง

Next action: ใช้ทีมใหม่กับ task feature/asset ถัดไป; เมื่อจำเป็นต้องใช้ Unity Editor ให้ตรวจการลงทะเบียนเครื่องมือของ Editor กับ relay ก่อน ไม่มีการทดสอบเกมที่อ้าง PASS จากงานนี้

Sources: [OpenAI custom agents](https://learn.chatgpt.com/docs/agent-configuration/subagents), [repository skills](https://learn.chatgpt.com/docs/build-skills)
