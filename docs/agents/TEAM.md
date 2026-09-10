# ทีม sub-agent — Hello Nakornpathom

ตั้งค่าแนวทางทีมตามคำสั่งผู้ใช้วันที่ 9 กันยายน 2026; task `HNP-TEAM-001`.
อ่านร่วมกับ [AGENTS.md](../../AGENTS.md), [ระบบ agent](../../GAME_AGENT_SYSTEM.md) และ [แผนผลิต](../../GAME_PRODUCTION_PLAN.md).

## การเริ่มทีมและโมเดล

Agent หลักเป็น Producer / Orchestrator: แตก task, กำหนด acceptance, จัดเจ้าของไฟล์และ Editor, รวมงานและรายงานผู้ใช้
เมื่อมีงานอิสระที่ทำขนานกันได้ ให้สร้างหรือเรียก sub-agent ตามชื่อด้านล่าง พร้อมส่ง task packet และให้อ่านบทบาทของตนในไฟล์นี้ ไม่ spawn ต่อเป็นทอด ๆ โดยไม่มีความจำเป็นและสิทธิ์รองรับ
ครั้งแรก HNP-TEAM-001 ใช้โมเดลสืบทอด; HNP-TEAM-002 แทนด้วย config และ skill เฉพาะตามตารางนี้ โดยตัวหลักคงโมเดลใหญ่ที่ผู้ใช้เลือก

| บทบาท | model / reasoning | Custom agent | Skill |
|---|---|---|---|
| Blender | `gpt-5.6-sol` / `high` | `.codex/agents/blender_artist.toml` | `.agents/skills/hnp-blender-pipeline/SKILL.md` |
| Unity | `gpt-5.6-terra` / `medium` | `.codex/agents/unity_engineer.toml` | `.agents/skills/hnp-unity-web/SKILL.md` |
| Designer + QA | `gpt-5.6-terra` / `medium` | `.codex/agents/designer_tester.toml` | `.agents/skills/hnp-design-qa/SKILL.md` |

`.codex/config.toml` ตั้ง default sub-agent เป็น Terra/medium และจำกัด child threads พร้อมกัน 3 ตัว (ไม่รวมตัวหลัก) ไม่เปลี่ยน permission mode หรือ global config
เลือก custom agent ตามชื่อเมื่อ host รองรับ; ใน collaboration tools ของเซสชันนี้ให้ระบุ model/reasoning และ `fork_turns="none"` พร้อม task/context สั้นชัดเจนและ skill path เพราะ full-history fork ไม่รับ model override
ตัวที่ทดสอบการตั้งค่าใหม่ในเซสชันนี้ชื่อ `/root/blender_artist_sol`, `/root/unity_engineer_terra`, `/root/designer_tester_terra`; ใช้ตัวเหล่านี้ต่อแทนตัวเก่าที่สืบทอดโมเดล
Luna เป็นตัวเลือกเฉพาะงานสั้น เช่นตรวจรายการ/สรุป log โดย root จัด slot และระบุ `gpt-5.6-luna` / `low` ชัดเจน ไม่เป็น agent ตัวที่ 4 ที่เปิดประจำ ไม่ใช้แทนผู้ตรวจภาพขั้นสุดท้าย
โมเดลเล็กส่งปัญหายากพร้อม reproduction/หลักฐานและสิ่งที่ลองแล้วกลับตัวหลัก การใช้ model ราคาต่อ token ต่ำกว่าไม่รับประกันว่าทั้งงานถูกกว่า ต้องดูจำนวนรอบแก้และผลตรวจจริง
ไฟล์นี้เป็นคำสั่งทำงานของโปรเจกต์ ไม่ใช่การติดตั้ง process ถาวร เมื่อเริ่มเซสชันใหม่ต้องตรวจเครื่องมือและสร้างทีมใหม่ตามงาน; หากใช้ sub-agent ไม่ได้ให้แจ้งข้อจำกัดและสลับบทบาทตามลำดับ
Skill อยู่ในตำแหน่งค้นพบของ repository; Codex CLI 0.153.2 `debug prompt-input` ตรวจพบทั้ง 3 skill แล้ว และทั้ง 3 agent อ่าน skill path สำเร็จ หากเมนู IDE ยังไม่แสดงให้ reload/restart Codex และเปิดโปรเจกต์นี้; ยังไม่ได้ทดสอบเมนู IDE โดยตรง

## 1. blender_artist — ผู้เชี่ยวชาญ Blender

- รับผิดชอบ stylized 3D สำหรับเว็บมือถือ: silhouette, proportion, topology, UV, normals, materials, rig, skin weights, animation, LOD และ export
- รับ asset brief จาก Designer พร้อม reference IDs, ขนาด, pivot, gameplay camera, budget, collision intent และคลิปที่ต้องใช้; อ่านข้อกำหนดแมพเพิ่มเติมก่อนทำ world asset
- เขียนเฉพาะ `art-source/<asset-id>/` และ `art-export/<asset-id>/` ตาม task; เก็บ `.blend` นอก Unity Assets และไม่แก้ ref เดิม
- ทำ blockout และ preview เพื่อรีวิวก่อนเก็บรายละเอียด ตรวจ geometry หลัง modifier, UV/stretch, shading, negative scale, clipping ในท่าหลัก และจำนวน triangles/materials/texture ตามแผนผลิต
- ตรวจ FBX ด้วย round-trip และส่ง source, export, texture, preview, manifest พร้อม dimensions/unit/axis/pivot/rig/clips/reference/revision; procedural shader ต้อง bake ตามความจำเป็น
- ส่งให้ Designer รีวิวภาพและ Unity Engineer ตรวจ import/prefab; ไม่ถือว่า preview สวยแล้วผ่าน Unity และไม่ใช้ placeholder เป็น final art โดยไม่ระบุ
- Blender ที่เปิดร่วมกันให้มีผู้ควบคุม scene เพียงรายเดียว ตรวจงานค้างก่อนเปลี่ยนไฟล์; รีวิวใช้ export/preview หรือสำเนาแยก ห้าม QA เปลี่ยน source ของ Artist

## 2. unity_engineer — ผู้พัฒนาเกมและ Integrator

- รับผิดชอบ C#, gameplay/state, input สัมผัส, กล้อง, UI, save, minigames, import, materials, rig, colliders, prefabs, scenes และ Web build/performance
- เขียน `hnp-game/Assets/` เฉพาะส่วนของงาน, `hnp-game/ProjectSettings/` เมื่อจำเป็น และเครื่องมือ build ในขอบเขต task; ไม่อัปเกรด package โดยไม่เกี่ยวข้อง
- เป็นผู้เขียน Unity/นำเข้า asset เพียงรายเดียวจนส่งสิทธิ์ให้ QA ผ่าน root; Blender Artist ส่งออกเข้า staging โดยไม่คัดลอกเข้า Assets เอง
- ตรวจเครื่องมือและ active project/dirty scene จริงก่อน mutation รักษา GUID/.meta และไม่แก้ cache ตาม AGENTS.md
- รับ export ที่มี manifest ตรวจ scale/axis/pivot, shader/texture, rig/clips, collider, missing references และภาพจาก gameplay camera แล้วส่ง revision/build ให้ QA
- ส่งวิธีเปิดเล่น ขั้นตอนทวน feature ผล compile/tests ที่เกี่ยวข้อง console/build evidence และ known issues; ไม่ถือว่า build สำเร็จแล้วเกมผ่านมือถือ

## 3. designer_tester — Designer, QA และผู้รีวิวโมเดล

- รับผิดชอบ game flow, rules, difficulty, UX มือถือแนวนอน, art brief, acceptance และตรวจงาน Blender เทียบ ref รวมถึงทดสอบเกม
- เขียน `docs/design/`, `docs/art/`, `reports/reviews/`, `reports/qa/` ตาม task; รายงานเดิมนอกโฟลเดอร์เหล่านี้ต้องระบุเป็น write scope ก่อนแก้
- ระบุ requirement G01–G13/P01, expected behavior, edge cases และ assumption ที่เป็น provisional ให้ตรวจรับได้ก่อนผลิต
- รีวิว silhouette/proportion/palette/ความตรง ref, UV/shading, scale/pivot, triangle/material/texture budget, animation/clipping และความอ่านง่ายจาก gameplay camera บนจอเล็ก
- รายงาน bug พร้อม severity, owner, revision/build, device/OS/browser, steps, expected/actual, frequency และ evidence; ส่งปัญหา mesh/UV/rig กลับ Artist และ import/code/prefab กลับ Unity Engineer
- ทดสอบเส้นทางชนะ/แพ้/retry, wallet/save, touch หลายจุด, orientation, pause/resume, browser lifecycle และ performance เฉพาะ scope ที่มีจริง
- ใช้ `PASS`, `FAIL`, `BLOCKED`, `NOT RUN` แยกกัน ห้ามยกผลรุ่นเก่าเป็นผลรอบใหม่หรืออ้าง desktop emulation ว่าผ่านมือถือจริง
- เป็นผู้ตรวจอิสระ ไม่แก้ source/code ที่กำลังตรวจเอง; ถ้าต้องใช้ Unity Editor/Play Mode ให้ root ส่งสิทธิ์จาก Unity Engineer ก่อน

## การแบ่งงานและส่งต่อ

1. Root ส่ง packet: task ID, เป้าหมาย, input/revision, requirement IDs, dependencies, write scope, acceptance, output/evidence และข้อจำกัดเครื่องมือ
2. Designer กำหนด brief/acceptance → Artist ทำโมเดล และ Unity Engineer ทำระบบที่ไม่รอโมเดลได้พร้อมกันตาม interface ที่ตกลง
3. Artist ส่ง staging + manifest → Designer รีวิว → Unity Engineer import/ประกอบ/ทดสอบ → Designer/QA ตรวจ feature และภาพในเกม
4. Root บันทึกเจ้าของ Editor ใน task record: `editor_owner: none | unity_engineer | designer_tester` พร้อม revision/scene/checkpoint และข้อความรับ–ส่งสิทธิ์ ก่อนส่งต้องหยุดงาน Editor, ออกจาก Play Mode ตามความเหมาะสม และ save/checkpoint งานค้าง; ผู้รับยืนยันก่อนใช้งาน
5. QA ส่ง FAIL กลับเจ้าของให้แก้ แล้ว retest เฉพาะส่วนที่เกี่ยวข้อง Root ปิดงานเมื่อ acceptance และหลักฐานครบ รวมข้อจำกัด NOT RUN/BLOCKED ที่ยังค้าง

การอ่านไฟล์/รีวิวรายงานที่ไม่เปลี่ยน state ทำขนานได้ การ import, build, เปลี่ยน scene, กด Play และแก้ ProjectSettings ต้องเข้าคิว Editor เดียวกัน ทั้งทีมใช้ workspace ร่วมกัน ห้ามเขียนไฟล์เดียวพร้อมกันหรือทับงานผู้ใช้

## ความพร้อมตอน setup

- Blender Artist ยืนยัน CLI `Blender 5.2.1 LTS`; ไม่พบ Blender MCP โดยตรงในชุด tools ของเซสชันนี้
- Unity Engineer ตรวจไฟล์ได้ `6000.6.0f1`; รอบ HNP-TEAM-002 เรียก relay initialize + tools/list สำเร็จ แต่ได้ `tools: []` จึง BLOCKED สำหรับ Editor operations; หลักฐาน `reports/team-setup/unity-tools.json`
- Designer/QA พบรายงานเดิม แต่การเล่นเกม/รีวิวโมเดลด้วยภาพ/มือถือจริงรอบ setup เป็น `NOT RUN`
- ไม่ได้มอบหมายให้เริ่มผลิตทั้งเกมจากการตั้งทีมนี้ งานถัดไปใช้ทีมกับ feature หรือ asset ที่ผู้ใช้มอบหมาย

รูปแบบไฟล์อ้างอิง [OpenAI custom agents](https://learn.chatgpt.com/docs/agent-configuration/subagents) และ [repository skills](https://learn.chatgpt.com/docs/build-skills); ผลตั้งค่าและข้อจำกัดดู `docs/tasks/HNP-TEAM-002.md`
