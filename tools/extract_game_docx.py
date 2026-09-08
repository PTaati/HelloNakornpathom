"""Extract source paragraphs and embedded images without rewriting game requirements."""
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'Game-Hello Nakornpathom.docx'
TARGET = ROOT / 'Game-Hello Nakornpathom.md'
MEDIA = ROOT / 'ref/game-document'
NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
      'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
      'v': 'urn:schemas-microsoft-com:vml'}

def main():
    MEDIA.mkdir(parents=True, exist_ok=True)
    with ZipFile(SOURCE) as archive:
        document = ET.fromstring(archive.read('word/document.xml'))
        relationships = ET.fromstring(archive.read('word/_rels/document.xml.rels'))
        image_rels = {r.attrib['Id']: r.attrib['Target'] for r in relationships
                      if r.attrib.get('Type', '').endswith('/image') and r.attrib.get('TargetMode') != 'External'}
        entries = []
        for name in archive.namelist():
            if not name.startswith('word/media/') or name.endswith('/'):
                continue
            data = archive.read(name)
            destination = MEDIA / Path(name).name
            if destination.exists() and destination.read_bytes() != data:
                raise RuntimeError(f'Refusing to replace changed reference: {destination}')
            destination.write_bytes(data)
            entries.append({'source_entry': name, 'path': destination.relative_to(ROOT).as_posix(),
                            'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
        lines = ['# GameDesign: Hello Nakornpathom', '',
                 '> ถอดข้อความและภาพจาก `Game-Hello Nakornpathom.docx` ตามลำดับในเอกสาร ไม่แก้คำสะกดหรือข้อขัดแย้งของต้นฉบับ', '',
                 '> คำอธิบายตำแหน่งสถานีและเส้นทางที่ผู้ใช้เพิ่มเติมแยกไว้ใน [ข้อกำหนดแผนที่](docs/design/MAP_LAYOUT.md)', '',
                 '## เนื้อหาต้นฉบับ', '']
        paragraphs = []
        used = set()
        for paragraph in document.findall('.//w:body//w:p', NS):
            pieces = []
            for node in paragraph.iter():
                if node.tag == '{'+NS['w']+'}t': pieces.append(node.text or '')
                elif node.tag == '{'+NS['w']+'}tab': pieces.append('\t')
                elif node.tag == '{'+NS['w']+'}br': pieces.append('\n')
            value = ''.join(pieces)
            if value.strip():
                paragraphs.append(value)
                # Escape Markdown list punctuation so the original numbering stays visible.
                import re
                rendered = re.sub(r'^(\d+)([.)])(?=\s)', r'\1\\\2', value.strip())
                lines.extend([rendered, ''])
            nodes = list(paragraph.findall('.//a:blip', NS)) + list(paragraph.findall('.//v:imagedata', NS))
            for node in nodes:
                rid = node.get('{'+NS['r']+'}embed') or node.get('{'+NS['r']+'}id')
                if rid not in image_rels: continue
                filename = Path(image_rels[rid]).name
                used.add(filename)
                lines.extend([f'![ภาพจากเอกสาร: {filename}](ref/game-document/{filename})', ''])
        unused = [e for e in entries if Path(e['path']).name not in used]
        if unused:
            lines.extend(['## ภาพฝังเพิ่มเติม', ''])
            for entry in unused:
                lines.extend([f"![ภาพจากเอกสาร]({entry['path']})", ''])
        TARGET.write_text('\n'.join(lines), encoding='utf-8')
        manifest = {'source': SOURCE.name, 'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                    'markdown': TARGET.name, 'nonempty_paragraphs': len(paragraphs), 'images': entries}
        (MEDIA/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps(manifest,ensure_ascii=True,indent=2))

if __name__ == '__main__': main()
