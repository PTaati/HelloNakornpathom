# แผนผลิตโมเดล เกม และการทดสอบ

ใช้คู่กับ [GAME_AGENT_SYSTEM.md](GAME_AGENT_SYSTEM.md) และ [AGENTS.md](AGENTS.md)
ตัวเลข budget และกติกาที่ระบุว่า “ตั้งต้น” เป็นข้อเสนอสำหรับ prototype ยังไม่ใช่ผล benchmark

## 1. Reference และ art direction

อัปเดต: แยกภาพ Word แล้วที่ [ref/game-document](ref/game-document/README.md) และถอดข้อความไว้ใน [Game-Hello Nakornpathom.md](Game-Hello%20Nakornpathom.md) ให้ใช้ [MAP_LAYOUT.md](docs/design/MAP_LAYOUT.md) เป็นข้อกำหนดตำแหน่งสัมพันธ์: สถานีฝั่งซ้าย → ถนนกลาง/สะพาน → องค์พระฝั่งขวาของภาพ

ใช้ภาพจริงใน `ref/` แยกตามสถานที่ พร้อม index ระบุ `ref_id`, path, ที่มา, สิ่งที่ใช้อ้างอิง และข้อจำกัด ภาพ Word 2 ภาพช่วยวางพื้นที่องค์พระ แต่ยังไม่มีมุมด้านหน้าสถานี สะพาน ร้านงานวัด และตัวละคร
เริ่ม blockout จากข้อมูลที่มีได้ โดยติดป้าย provisional ไม่สร้างรายละเอียดสมมติแล้วอ้างว่าตรงสถานที่จริง ขั้น final art ต้องตรวจ landmark เทียบ ref

แนวภาพตั้งต้น: low-poly 3D สีอบอุ่น รูปทรงชัด รายละเอียดอ่านได้บนมือถือ วัสดุใช้ palette/atlas ร่วมกัน; องค์พระเป็น landmark หลัก ใช้ silhouette ช่วยนำทาง แสงงานวัดใช้ emissive และ baked lighting เป็นหลัก
เตรียม brief ของแต่ละ asset ให้มี gameplay purpose, ภาพอ้างอิง, มิติ, จุดตั้ง pivot, มุมที่เห็นในเกม, รายการ animation, collider และ budget ก่อนปั้น

## 2. รายการโมเดลและลำดับ

| กลุ่ม | Asset หลัก | ลำดับ / การตรวจสำคัญ |
|---|---|---|
| Calibration | Cube 1 เมตร, ลูกศรบอกด้านหน้า, rig ทดสอบ | P0; scale/axis/animation round-trip |
| ผู้เล่น | Base body, เสื้อสีไข่, กางเกงดำ, รองเท้าแตะ, หมวกคาวบอย | P0; rig เดียวกัน ไม่ทะลุกันขณะเดิน/นั่ง |
| สถานี | ชานชาลา ราง หลังคา ม้านั่ง ป้ายสถานี รถไฟและที่นั่ง | P0; ลงรถไฟได้ ประตู/พื้น/collider ตรงกัน |
| เส้นทาง | พื้นถนน ทางเท้า สะพานยักษ์ รถหลบสิ่งกีดขวาง | P1; จุดชนและช่องข้ามอ่านชัด |
| องค์พระ | องค์เจดีย์ ฐาน บันได ทางเดินบน/ล่าง จุดไหว้พระ | P1; silhouette, ทางเดิน, camera clearance |
| งานวัด | ร้าน modular ซุ้มปาลูกโป่ง ลูกโป่ง ลูกดอก ซุ้มโยนห่วง ห่วง/เป้า | P1; hit volume และ feedback ตรงภาพ |
| ของแต่งตัว | แว่นตา ร่ม กระเป๋า และตัวเลือกอีก 4 slot | P2; attachment point และ clipping |
| บรรยากาศ | ต้นไม้ โคมไฟ ของตกแต่ง NPC และท่าเต้น | P2; ลดจำนวนตัวเคลื่อนไหวพร้อมกันตาม profile |
| เนื้อหาเพิ่มเติม | กระทง พื้นที่เต้น ไม้ ปืน ท่อเหล็ก | P3; รอข้อสรุปการใช้งานก่อน final asset |

P0 = พิสูจน์ pipeline/vertical slice, P1 = core loop, P2 = ความครบถ้วนและตกแต่ง, P3 = เนื้อหาที่ยังไม่มีกติกาชัด

## 3. Blender → Unity pipeline

1. สร้าง blockout เทียบ reference และขนาดผู้เล่น ส่ง preview ก่อนเพิ่มรายละเอียด
2. ใช้หน่วยเมตร ตกลง pivot ที่ฐานสำหรับ prop/อาคาร และ root ของตัวละคร; ตั้งชื่อ `HNP_<Category>_<Name>_<Variant>`
3. ทำ mesh/UV ตรวจ normals, geometry ที่ผิดปกติ และ faces ที่ไม่จำเป็น; rig และ skin ต้องทดสอบท่าที่งอมากที่สุด
4. เก็บ master `.blend` ใน `art-source/<asset-id>/` พร้อมสคริปต์สร้างถ้ามี สคริปต์ต้องจำกัดการล้าง object เฉพาะ collection ของงานตนเอง
5. Bake procedural material ที่จำเป็นเป็น texture เพื่อสร้าง Unity material ใหม่ ไม่สมมติว่า Blender shader node จะทำงานเหมือนเดิมใน Unity
6. Export เฉพาะ mesh/armature ที่ใช้จริงเป็น FBX ไป staging ใช้ preset ตั้งต้น Forward `-Z`, Up `Y`, ไม่เพิ่ม leaf bones และ bake animation ที่ต้องใช้; ผลจาก calibration เป็นเกณฑ์ตัดสินค่าจริง โดยเฉพาะ rig
7. ตรวจ export โดย re-import/รายงาน geometry และ preview; บันทึก triangle count หลัง modifier ไม่ใช่เฉพาะก่อน export
8. Integrator นำเข้า `hnp-game/Assets/_HNP/Art/` ผ่าน Unity ตั้ง material/texture/rig/clip แล้วสร้าง prefab wrapper แยกจาก model import
9. ตรวจใน Unity ว่า 1 เมตรถูกต้อง ตั้งตรง หันหน้าได้ตาม controller, pivot/animation/material/collider ถูก และไม่มี missing reference
10. จับภาพจาก gameplay camera และเทียบกับ brief ก่อน VERIFIED; ถ้าไม่ผ่านส่ง bug กลับตาม source ของปัญหา

การแปลงแกนเป็นส่วนหนึ่งของ FBX export ที่ต้องตั้งให้ตรง application ปลายทาง ดู [Blender FBX manual](https://docs.blender.org/manual/en/5.2/files/import_export/fbx_legacy.html) และ [FBX exporter defaults](https://github.com/blender/blender-addons/blob/main/io_scene_fbx/__init__.py) ทั้งนี้ให้ยืนยัน exporter ที่มีใน Blender เวอร์ชันที่ติดตั้งจริง

### Budget โมเดลตั้งต้น

| ประเภท | Triangles ต่อชิ้น LOD0 | Material / texture |
|---|---:|---|
| ผู้เล่นรวมชุดเริ่มต้น | ≤ 12,000 | ≤ 3 materials, texture ≤ 1024 ต่อชุดหลัก |
| NPC | ≤ 6,000 | ≤ 2 materials, atlas ร่วม |
| Prop เล็ก / ร้าน modular | 100–2,000 / ≤ 5,000 | 1–2 materials, 512–1024 |
| รถไฟต่อชุดที่มองเห็น / landmark หลัก | ≤ 20,000 / ≤ 30,000 | ใช้ atlas; 2048 เฉพาะเมื่อภาพพิสูจน์ว่าจำเป็น |

วัตถุใหญ่ทำ LOD เมื่อช่วย performance และตรวจการเปลี่ยนระดับจาก gameplay camera; collider ใช้ primitive/compound เป็นหลัก รายการเกิน budget ต้องมีผล profile และเหตุผล ไม่ลดรูปทรงสำคัญเพียงเพื่อให้ผ่านตัวเลข
Animation ขั้นต่ำ: Idle, Walk, Jump, Sit, Dance, LieDown, Celebrate; ระบบนั่งรถไฟและสลับเครื่องแต่งกายต้องใช้ rig/attachment contract เดียวกัน

## 4. เว็บเต็มจอและมือถือแนวนอน

ผู้เล่นเปิด URL → เห็น loading/progress → แตะ “เริ่มเล่น” → เปิดเสียงและขอ fullscreen ตาม capability → แสดงเกมแนวนอน เมื่อถือแนวตั้งให้แสดงภาพ/ข้อความหมุนเครื่องและพัก input/timer จนกลับแนวนอน

Fullscreen API ต้องอาศัยการกระทำของผู้ใช้ และ orientation lock ใช้ไม่ได้เหมือนกันทุก browser จึงต้องมี fallback เป็น canvas เต็มพื้นที่ browser ที่มองเห็น พร้อมข้อความหมุนเครื่องด้วยตนเอง การซ่อนแถบ browser แบบ native fullscreen ทุกเครื่องไม่ใช่เงื่อนไขที่เว็บรับประกันได้ ดู [requestFullscreen](https://developer.mozilla.org/en-US/docs/Web/API/Element/requestFullscreen) และ [orientation lock](https://developer.mozilla.org/en-US/docs/Web/API/ScreenOrientation/lock)

- Web template ใช้ responsive viewport, `100dvh` พร้อม fallback และ safe-area inset; resize ทั้ง canvas และ UI เมื่อ browser bar/ขนาดหน้าจอเปลี่ยน
- Touch: joystick ซ้าย, ลากกล้องด้านขวา, ปุ่มกระโดด/โต้ตอบ; UI ปุ่มเริ่มต้นไม่น้อยกว่า 48 CSS px และไม่อยู่ใต้ notch/home indicator
- แยก pointer ID ของ joystick/camera/button ให้เดิน หมุนกล้อง และกระโดดพร้อมกันได้ ไม่ให้การแตะ UI ทะลุเข้า gameplay
- ปุ่ม zoom/สลับกล้องและ map เข้าถึงได้โดยไม่บังการเดิน; minigame เปลี่ยน control ตามบริบท
- Desktop: WASD, mouse camera, jump/interact พร้อมคำแนะนำที่ตรง input mode
- Pause เมื่อ page hidden/เสีย focus และล้าง input ค้าง; resume หลังผู้เล่นพร้อม ห้ามปล่อย timer มินิเกมวิ่งเสียเปรียบขณะอยู่แท็บอื่น
- Web loader แสดงข้อผิดพลาดและปุ่มลองใหม่ ไม่ค้างที่ progress 90%; จัดการ audio หลัง interaction และกรณี storage ใช้ไม่ได้
- ตรวจ texture format, compression response headers, MIME ของ Wasm และ cache version กับ hosting จริง ใช้ HTTP(S) ในการทดสอบ build
- ตรวจ browser support กับ [Unity 6000.6 Web browser compatibility](https://docs.unity3d.com/6000.6/Documentation/Manual/webgl-browsercompatibility.html) ก่อนกำหนดรายชื่อเครื่องรองรับขั้นสุดท้าย

### Budget runtime ตั้งต้น

| ตัวชี้วัด | เป้าหมาย / วิธีตรวจ |
|---|---|
| Frame rate | อย่างน้อย 30 FPS โดย P95 frame time ≤ 33.3 ms ในช่วง gameplay 5 นาที; desktop เป้า 60 FPS |
| ปริมาณฉาก | เริ่มที่ ≤ 150,000 visible triangles และ ≤ 100 draw calls ในมุมใช้งานหลัก แล้วปรับจาก profile |
| Download แรก | ข้อมูลที่จำเป็นก่อนเล่น ≤ 30 MB แบบ compressed; วัดจาก network แบบ cold cache |
| เวลาเริ่มเล่น | ≤ 20 วินาที ที่จำลองเครือข่าย 20 Mbps / RTT 100 ms; วัดถึงควบคุมตัวละครได้ |
| Memory | ตั้งเป้า Unity tracked memory ≤ 256 MB; บันทึก browser/process memory เพิ่มเมื่อวัดได้ เพราะไม่ใช่ metric เดียวกัน |
| ความเสถียร | เล่นวนกิจกรรม/เปลี่ยนโซน 15 นาที ไม่มี crash, tab reload จาก memory หรือ memory โตต่อเนื่องทุก loop |

เริ่มด้วย render scale ต่ำบนมือถือ ลดเงา realtime, post-processing, transparent overdraw และ NPC ก่อนเพิ่ม asset detail ต้องระบุเครื่องจริงและ browser version ในผล ไม่ถือว่าตัวเลขเหล่านี้ผ่านแล้ว

## 5. Roadmap พร้อม gate

| ID / ช่วง | งาน | พึ่งพา | เกณฑ์ออกจากช่วง |
|---|---|---|---|
| HNP-001 Preflight | ตรวจ MCP/Blender/Web support, build scene เล็กบนมือถือ | ไม่มี | มี environment report และ Web smoke test; blocker ระบุชัด |
| HNP-002 Design baseline | Reference index, route blockout, art brief, data contracts | อ่านต้นฉบับ | G01–G13/P01 มี spec หรือ assumption และ acceptance |
| HNP-003 Asset pipeline | Cube/rig calibration, ผู้เล่นและชานชาลา Blender | 001, 002 | export เข้า Unity ถูก scale/axis/material/animation |
| HNP-004 Vertical slice | Intro รถไฟ → เดินในสถานี → โต้ตอบหนึ่งจุด พร้อม touch/fullscreen | 003 | เล่น Web build บน Android/iPhone และจับหลักฐานได้ |
| HNP-005 Journey | Route, crossing, องค์พระบน/ล่าง, map, prayer | 004 | เล่นต่อจากสถานีจนไหว้พระได้; fail/retry ไม่ติดค้าง |
| HNP-006 Festival | Wallet, ปาลูกโป่ง, โยนห่วง, return/ending/GameOver | 005 | complete core loop และเงินหมดได้; ไม่เก็บเงิน/รางวัลซ้ำ |
| HNP-007 Player systems | ซื้อ/เก็บของ, แต่งตัว, ท่าทาง, กล้อง, save | 006 | G07–G11 ผ่าน functional test และ reload consistency |
| HNP-008 Content completion | เพิ่ม NPC/ตกแต่ง และกิจกรรม G13 เมื่อมีกติกา | 006, spec ของกิจกรรมนั้น | เนื้อหาที่ตกลงเข้ารุ่นนี้มี tests และ budget |
| HNP-009 Release candidate | Optimize, browser/device regression, hosting validation | 007 และ scope ที่เลือกจาก 008 | Gate QA ผ่าน ไม่มี blocker; รายการ deferred ชัดเจน |

Vertical slice เป็น milestone ทดลองระบบ ไม่ใช่เกมฉบับสมบูรณ์ ห้ามตัดรายการต้นฉบับเงียบ ๆ หากเลื่อน G13 หรือส่วนอื่นต้องแสดงใน release scope ว่ายังไม่เสร็จ

## 6. แผนทดสอบ

| ระดับ | สิ่งที่ทดสอบ | Expected result / หลักฐาน |
|---|---|---|
| Asset validation | Dimensions, triangles, UV, normals, materials, clips | ผ่าน brief/budget; manifest + Blender preview + Unity screenshot |
| EditMode | Wallet หัก/เพิ่ม/ยอดศูนย์, duplicate result, objective order, save migration/corrupt data | ไม่ติดลบ/ไม่ซ้ำ, เปลี่ยน GameOver ครั้งเดียว, recover ตาม spec; test XML |
| PlayMode | Intro จบ, เปลี่ยนโซน, trigger, pause/resume, input maps, minigame cleanup | state/input/camera กลับถูกต้อง, service ไม่ซ้ำ; test report + console |
| Gameplay Web | G01–G12 เล่นเส้นทางชนะและแพ้ครบ | เล่นจบ/เริ่มใหม่ได้, เงิน/ของ/แผนที่ถูก; video หรือขั้นตอนพร้อมภาพ |
| Touch Web | เดิน+หมุน+กระโดด, tap รัว, pointer cancel, แตะ UI | ไม่ค้าง ไม่ซื้อซ้ำ ไม่ยิงผ่าน UI; device report |
| Orientation | เข้าเว็บแนวตั้ง/นอน หมุนระหว่างมินิเกม fullscreen ถูกปฏิเสธและออก fullscreen | ไม่มี UI ถูกตัด, timer พัก, fallback เล่นต่อได้ |
| Browser lifecycle | สลับแท็บ lock/unlock เครื่อง, resize, reload, เสียงถูก block | ไม่มี input ค้าง, resume ได้, save คืนค่าที่ commit แล้ว |
| Delivery | cold/warm cache, failed download, build ใหม่บน cache เก่า | progress/error ชัด โหลด retry ได้ ไม่ผสม asset คนละรุ่น |
| Performance | เทศกาลมุมหนักสุดและวนเปลี่ยนโซน 15 นาที | วัดตาม budget พร้อม device/browser/build ID |

### Device matrix

- Android Chrome บนมือถือระดับกลางจริงอย่างน้อย 1 รุ่น: ลงรุ่น/RAM/OS/browser ให้ชัดก่อนใช้เป็น baseline
- iPhone Safari จริงอย่างน้อย 1 รุ่น: ตรวจ fullscreen fallback, orientation, audio, safe area และ memory เป็นพิเศษ
- Desktop Chrome และ Edge สำหรับ functional regression; Safari desktop เพิ่มเมื่อมีเครื่อง
- จำลอง viewport แนวนอน 667×375, 844×390 และ 932×430 CSS px เพื่อตรวจ layout; เป็นส่วนเสริม ไม่แทนการทดสอบมือถือจริง
- ถ้าไม่มีเครื่องหรือ remote device service ให้สถานะ device test เป็น `NOT RUN` และยังไม่ผ่าน mobile release gate

### ขั้นตอน end-to-end หลัก

1. ล้าง save เริ่มเกมในแนวตั้ง หมุนเครื่องและกดเริ่ม ตรวจ loading/เสียง/fullscreen หรือ fallback
2. ดูรถไฟจอด ลงรถไฟ เดินและหมุนกล้องพร้อมกัน เปิดแผนที่ตรวจตำแหน่ง
3. ทดสอบชนรถหนึ่งครั้งแล้ว retry; ข้ามสำเร็จ เดินไปองค์พระ
4. ทดสอบ prayer ทั้งผ่านและพลาด เดินรอบบนและลงไปงานวัด
5. เล่นปาลูกโป่ง/โยนห่วง ตรวจเงินก่อน/หลัง คะแนน และการกดย้ำปุ่มเริ่ม/จบ
6. ซื้อและใส่ของหนึ่งชิ้น เก็บของ ทดสอบท่าและกล้อง จากนั้น reload ตรวจ save
7. ทำ objective บังคับครบ กลับสถานีขึ้นรถไฟ ดู ending แล้วเริ่มใหม่
8. ทดสอบอีกรอบให้เงินถึงศูนย์ ต้องเข้า GameOver ครั้งเดียว และเริ่มใหม่โดยไม่มี state เก่าค้าง

### รูปแบบ bug report

`BUG-ID`, task/requirement ID, severity, build hash, device/OS/browser, precondition/save/seed, steps, expected, actual, frequency, evidence path, owner, retest status
ใช้ Critical = crash/data loss, High = เล่นต่อหรือจบเกมไม่ได้/เงินผิด, Medium = feature เสียบางกรณี, Low = cosmetic
QA ส่งปัญหา mesh/UV/rig ให้ Blender Artist, import/prefab ให้ Integrator, rules/state ให้ Gameplay, browser/performance ให้ Web Engineer

## 7. Definition of Done

- Feature ตรง spec ที่ trace กลับ requirement ได้ และไม่มี assumption สำคัญซ่อนอยู่
- Source/export/code และ `.meta` ที่เกี่ยวข้องครบ เปิดโปรเจกต์ใหม่แล้วไม่มี missing asset/script
- Tests ที่เกี่ยวข้อง PASS พร้อมหลักฐาน; รายการ NOT RUN/BLOCKED แสดงชัดและไม่ถูกนับว่าผ่าน
- Web build เล่นเส้นทางหลักและเส้นทางแพ้ได้บน device matrix ที่ตกลง ไม่มี Critical/High ค้าง
- UI แนวนอนภาษาไทยอ่านได้ ฟอนต์ไม่หาย ปุ่มไม่ติดขอบ และ fullscreen fallback ผ่าน
- Performance วัดจากเครื่องจริงตาม budget หรือมีการปรับ budget พร้อมเหตุผลบันทึกไว้
- ส่ง build ID, วิธีเปิดเล่น, test report, known issues, deferred requirements และ task ถัดไป

## 8. คำสั่งเริ่มงานตัวอย่าง

> อ่าน AGENTS.md, GAME_AGENT_SYSTEM.md และ GAME_PRODUCTION_PLAN.md แล้วเริ่ม HNP-001 กับ HNP-002 ตรวจ Unity MCP และ Blender ที่เข้าถึงได้จริง สร้าง environment report, reference index และ task records จากนั้นทำ calibration asset และ Web smoke build ตาม dependency เก็บหลักฐานจริงและรายงาน blocker โดยไม่อ้างว่าผ่านสิ่งที่ยังไม่ได้ทดสอบ

เอกสารนี้ยังไม่ได้รันคำสั่งตัวอย่าง ยังไม่ได้ทดสอบ Unity/Blender/Mobile และไม่ได้สร้างโฟลเดอร์ในแผนที่ยังไม่จำเป็นต่อการออกแบบ
