# เปิดเล่นแมพนครปฐมเวอร์ชันใหม่

อัปเดต HNP-ART-002: องค์พระเพรียวขึ้น ฐานแคบลง 12% และสูงขึ้น 23% พร้อมแสงอุ่นอ่อน ท้องฟ้าฟ้า สีเขียว/น้ำสดขึ้น และเงานุ่ม อ่านรูปทรงได้ชัดกว่าโทนส้มเดิม ดู [ภาพองค์พระล่าสุด](reports/world/approach.png)

เว็บล่าสุดอยู่ที่ **http://127.0.0.1:8080** ขณะ local server ทำงาน หากปิดแล้วเปิดใหม่ด้วย `python -m http.server 8080 --directory builds/web --bind 127.0.0.1`

ฉากล่าสุดคือ `hnp-game/Assets/_HNP/Scenes/NakornpathomWorld.unity` วางสถานีฝั่งซ้าย คลอง สะพาน ถนนกลาง และองค์พระฝั่งขวาตาม `ref/game-document/image2.png` สร้างองค์พระจาก `ref/jd.jpg` และใช้โทน low-poly แสงเย็นจาก `ref/style.jpg` ระยะเป็นสเกลย่อสำหรับเดินสำรวจ ไม่ใช่ขนาดสำรวจจริง

- กด **START EXPLORING**; WASD / ลูกศรเดิน, Shift วิ่ง, Space กระโดด
- มือถือแนวนอนใช้จอยซ้าย ลากพื้นที่ขวาหมุนกล้อง และปุ่ม JUMP / WALK-RUN
- กด **MAP / M** เปิด–ปิดแผนที่ และ **STATION** กลับจุดเริ่ม
- เดินผ่านตลาด ขึ้นบันได วนลานองค์พระ และไปลานงานวัดได้ ไม่มีเงื่อนไขบังคับจบการสำรวจ
- ใน Unity เปิดฉากล่าสุดแล้วกด Play; สร้างเว็บด้วย **HNP → Build Reference World Web** หลังออกจาก Play Mode

ดู [ภาพเล่นบนเว็บ](reports/world/web-desktop.png), [ภาพแมพ](reports/world/web-map.png), [ภาพองค์พระ](reports/world/approach.png) และ [ผลตรวจ](reports/world/validation.md)

Blender source: `art-source/world/Nakornpathom.blend`, `art-source/world/Traveller.blend`; FBX และภาพ preview อยู่ใน `art-export/world/` ตัวละครมีเสื้อผ้า หมวก กระเป๋า ใบหน้า และการแกว่งแขนขาขณะเดิน

ผ่านการเดินเส้นทางหลัก/รอบนอกใน Unity และทดสอบเว็บบน Chrome desktop แล้ว ยังไม่ได้ทดสอบมือถือจริงหรือวัด FPS ต่อเนื่องบนมือถือ ขนาดเว็บประมาณ 52.1 MB แบบไม่บีบอัด ยังมี build warnings จาก shader/toolchain ดูรายงานฉบับเต็ม

หมายเหตุ: `.gitignore` เดิมละทั้ง `hnp-game/` ไฟล์ Unity จึงมีอยู่ในเครื่องแต่ไม่ได้ถูกติดตามใน Git

---

# บันทึกฉากสถานีรุ่นก่อน

สร้างโมเดลม้านั่งใน Blender และฉาก `StationPrototype.unity` แล้ว ผู้ใช้อนุญาตให้ทำงานต่อ และเชื่อมต่อ Unity MCP สำเร็จอีกครั้ง การทดสอบ gameplay ใน Play Mode ผ่านแล้ว ดูหลักฐานที่ `reports/unity-play-tests.json`

Web build พร้อมที่ `builds/web/` และผ่านการเปิดเล่น/ตรวจภาพใน Chrome แล้ว ดู [ภาพเว็บล่าสุด](reports/web-desktop.png) และ [ผลตรวจ](reports/prototype-validation.md)
ระหว่าง local server ทำงาน เปิด **http://127.0.0.1:8080** จากเครื่องนี้ได้ หากปิด server แล้ว ให้ใช้คำสั่งในขั้นตอน 7 เพื่อเปิดใหม่

## ไฟล์พร้อมใช้งาน

- [Blender source](art-source/station/HNP_Prop_StationBench_A.blend)
- [ภาพม้านั่ง](art-export/station/bench-preview.png)
- [FBX](art-export/station/HNP_Prop_StationBench_A.fbx) — นำสำเนาไปไว้ใน Unity Assets แล้ว
- [รายละเอียดโมเดล](art-export/station/bench-manifest.json): 836 triangles, 2 materials, กว้าง 1.8 เมตร
- [Unity scene builder](hnp-game/Assets/_HNP/Editor/HnpPrototypeBuilder.cs)
- [Gameplay](hnp-game/Assets/_HNP/Scripts/Prototype/HnpStationGame.cs) และ [touch control](hnp-game/Assets/_HNP/Scripts/Prototype/HnpTouchPad.cs)
- [Web template](hnp-game/Assets/WebGLTemplates/HNP/index.html)
- [ผลตรวจ environment](reports/environment.md)

## เปิดจาก Unity ด้วยตนเอง

1. เปิด `hnp-game` ด้วย Unity 6000.6.0f1 รอ compile แล้วตรวจ Console
2. เปิด `Assets/_HNP/Scenes/StationPrototype.unity`
3. มี prefab ม้านั่งที่ `Assets/_HNP/Prefabs/StationBench.prefab` แล้ว เมนู **HNP → Create Station Prototype** ใช้เฉพาะเมื่อยังไม่มี scene เพื่อป้องกันเขียนทับงานเดิม
4. กด Play แล้ว **START EXPLORING** เดินด้วย WASD, กระโดด Space, ลากพื้นที่ด้านขวาเพื่อหมุนกล้อง หรือใช้ปุ่มบนจอ
5. เก็บโปสการ์ดสีทอง 3 ใบ เดินไปซุ้ม **TO THE FAIR** แล้วกด E / GO เพื่อจบการทดลอง เลือก **EXPLORE AGAIN** เพื่อเริ่มใหม่
6. ออกจาก Play Mode แล้วเลือก **HNP → Build Web Prototype** เพื่อ build ลง `builds/web/` การ build ครั้งแรกอาจใช้เวลาหลายนาที
7. เปิดผ่าน local HTTP server ไม่ใช่ `file://` เช่น `python -m http.server 8080 --directory builds/web --bind 127.0.0.1` แล้วเข้า `http://127.0.0.1:8080`

Play Mode ผ่านการตรวจ movement, jump/landing, เก็บของไม่ซ้ำ, เงื่อนไขจบเกม, restart และขนาด/วัสดุ/collider ม้านั่ง โมเดลผู้เล่น/รถไฟ/อาคารเป็น primitive blockout ส่วนม้านั่งเป็นโมเดลจาก Blender จริง UI ในเกมทดลองเป็นภาษาอังกฤษ; หน้าโหลดและข้อความหมุนเครื่องเป็นภาษาไทย การทดสอบบนมือถือจริงยังไม่ได้รัน

Web ใช้ Mobile URP และ WebGL2 ชัดเจนเพื่อให้โมเดลแสดงถูกต้อง ขนาด build ประมาณ 50.4 MB แบบไม่บีบอัดสำหรับทดสอบ local ยังไม่ใช่รุ่นปรับประสิทธิภาพสำหรับเผยแพร่ และยังมี warning จาก shader/package ที่ติดตั้งเดิม

## ตรวจ MCP ต่อ

Unity ใช้ relay ที่ติดตั้งมากับ package: เปิด **Edit → Project Settings → AI → Unity MCP Server** ตรวจว่า bridge Running แล้วใช้ `python tools/unity_mcp.py --code-file tools/unity_preflight.cs --output reports/unity-preflight.json` ภายใต้สิทธิ์ที่อนุญาต
หากมี Pending Connections ให้ผู้ใช้ตรวจชื่อ **HNP Prototype Client** และอนุญาตใน Unity ตามหน้าจอ server

Blender ยังต้องทราบ add-on และ endpoint/คำสั่งของ MCP ที่ต้องการใช้ ไม่ได้ติดตั้ง add-on หรืออ้างว่า CLI เป็น MCP

## อ้างอิงเทคนิค

- Unity MCP setup: เอกสารที่ติดตั้งใน `hnp-game/Library/PackageCache/com.unity.ai.assistant@8d1e3e89e3a7/Documentation~/integration/unity-mcp-get-started.md`
- [Unity Input System UI module](https://docs.unity.cn/Packages/com.unity.inputsystem%401.10/api/UnityEngine.InputSystem.UI.InputSystemUIInputModule.html)
- [Unity Web templates](https://docs.unity.cn/Manual/webgl-templates.html)
