#!/usr/bin/env python3
import os
import sys
import json
from glossary import load_glossary, select_terms_for_chunk, format_terms_for_prompt
from chunk_context import get_neighbor_context, format_for_prompt

def get_args(temp_dir, chunk_filename):
    glossary_path = os.path.join(temp_dir, 'glossary.json')
    glossary = load_glossary(glossary_path)
    
    chunk_path = os.path.join(temp_dir, chunk_filename)
    with open(chunk_path, 'r', encoding='utf-8') as f:
        chunk_text = f.read()
        
    terms = select_terms_for_chunk(glossary, chunk_text)
    term_table = format_terms_for_prompt(terms)
    
    context = get_neighbor_context(temp_dir, chunk_filename)
    neighbor_context = format_for_prompt(context)
    
    term_table_part = ""
    if term_table:
        term_table_part = f"\n\n4. **ความสอดคล้องของคำศัพท์ (Term Consistency):**\n   - หากมีตารางคำศัพท์ด้านล่างนี้ คุณต้องแปลศัพท์ดังกล่าวให้ตรงตามตารางอย่างเคร่งครัด:\n\n{term_table}\n"
        
    neighbor_part = ""
    if neighbor_context:
        neighbor_part = f"\n\n5. **บริบทข้างเคียง (Neighbor Context - สำหรับอ้างอิงเท่านั้น):**\n   - ใช้บริบทข้างเคียงด้านล่างเพื่อช่วยในการอ้างอิงสรรพนาม เพศของตัวละคร หรือความสอดคล้องของคำแปลเท่านั้น (ห้ามแปล ห้ามคัดลอก หรือรวมบริบทนี้เข้าในผลลัพธ์สุดท้าย):\n\n{neighbor_context}\n"

    custom_instr_part = ""
    
    prompt = f"""คุณคือระบบ Agent แปลหนังสืออัจฉริยะ โปรดแปลไฟล์ Markdown นี้เป็นภาษา Thai (ภาษาไทย) โดยทำตามบทบาทและเวิร์กโฟลว์ 3 ขั้นตอนดังต่อไปนี้ในใจของคุณก่อนสรุปและส่งมอบคำแปลที่เป็นผลลัพธ์สุดท้าย:

1. **Translator Agent (เอเจนต์ผู้แปล):**
   - แปลเนื้อหาแบบประโยคต่อประโยค ย่อหน้าต่อย่อหน้าอย่างละเอียด
   - **ห้ามสรุปเนื้อหา:** ต้องเก็บรายละเอียดให้ครบถ้วน 100% รวมถึงฟุตโน้ต (Footnotes) ท้ายบท (Endnotes) และมุกตลก/การอ้างอิงของผู้เขียน
   - กรณีคำศัพท์เฉพาะทาง ให้แปลเป็นคำไทยที่เข้าใจง่าย หรือทับศัพท์ตามความเหมาะสม พร้อมวงเล็บภาษาอังกฤษในครั้งแรกที่ปรากฏ (เช่น ปัญญาประดิษฐ์ (Artificial Intelligence))
   - รักษาโครงสร้าง Markdown ดั้งเดิมไว้ทั้งหมด (หัวข้อ, ตัวหนา, ตัวเอียง, ลิงก์, โค้ด)
   - ลบคำว่า "OceanofPDF.com" หรือ "Ocean of PDF" ออกจากเนื้อหาและฟุตโน้ตทั้งหมด

2. **Editor & Polisher Agent (เอเจนต์บรรณาธิการและเกลาสำนวน):**
   - ปรับปรุงสำนวนภาษาไทยที่แปลมาให้สละสลวย มีชีวิตชีวา และไหลลื่น
   - **สไตล์การเขียน:** ใช้โทนเสียงแบบหนังสือแนว Pop-Sci หรือ How-to (เช่น หนังสือของสำนักพิมพ์ WE LEARN หรือ Bookscape) ที่อ่านสนุก เป็นกันเองแต่สุภาพ เข้าใจง่าย ไม่แข็งทื่อเป็นภาษาแปลกูเกิล (Translationese)
   - หลีกเลี่ยงโครงสร้างประโยคแบบภาษาอังกฤษที่ซับซ้อนเกินไปในภาษาไทย (เช่น การใช้ passive voice หรือประโยคขยายที่ยาวเกินจำเป็น)
   - ตรวจสอบความสอดคล้องของการใช้คำศัพท์เฉพาะทางตลอดทั้งบท

3. **QA & Formatting Reviewer Agent (เอเจนต์ตรวจสอบคุณภาพและความถูกต้อง):**
   - เปรียบเทียบต้นฉบับภาษาอังกฤษกับเวอร์ชันภาษาไทยสุดท้ายเพื่อตรวจทานความถูกต้องและความครบถ้วน (ไม่มีประโยคหรือย่อหน้าใดตกหล่น)
   - ตรวจสอบความถูกต้องของระบบตัวเลข ฟุตโน้ต ลิงก์ และฟอร์แมต Markdown ทั้งหมด
   - ตรวจหาคำสะกดผิดและไวยากรณ์ภาษาไทยให้ถูกต้อง 100%

ข้อกำหนดทางเทคนิคเพิ่มเติม (IMPORTANT TECHNICAL REQUIREMENTS):
1. **การรักษาไฟล์ภาพ (Image References):**
   - ต้องคงโครงสร้างรูปภาพ `![alt](path)` ไว้อย่างครบถ้วน ห้ามลบหรือข้ามเด็ดขาด
   - ห้ามแก้ไขชื่อไฟล์และโฟลเดอร์ของรูปภาพ (เช่น `media/image-001.png` ต้องไว้เหมือนเดิม)
   - สามารถแปลคำอธิบายภาพ (alt text) ได้แต่ต้องยังคงรูปแบบ Markdown สำหรับรูปภาพไว้
   - หากมีแท็ก HTML ของรูปภาพหรือลิงก์ดั้งเดิม (เช่น `<img alt="..." />`, `<a title="...">`) ให้แปลงเครื่องหมายอัญประกาศภายในแอตทริบิวต์ให้ปลอดภัยตามภาษาปลายทาง (เช่น ใช้เครื่องหมายอัญประกาศคู่ภาษาไทย `“` `”` หรือใช้ HTML entities `&quot;` เพื่อไม่ให้โครงสร้าง HTML เสียหาย)
     ตัวอย่างแอตทริบิวต์ HTML ที่ปลอดภัย:
     - ตัวอย่างที่ผิด: alt="อลิซถือขวดที่เขียนว่า"ดื่มฉัน"" (อัญประกาศซ้อนกันทำให้โครงสร้างพัง)
     - ตัวอย่างที่ถูก: alt="อลิซถือขวดที่เขียนว่า“ดื่มฉัน”" หรือ alt="อลิซถือขวดที่เขียนว่า&quot;ดื่มฉัน&quot;"
2. **การจัดการระดับหัวข้อ (Headers):**
   - วิเคราะห์ระดับหัวข้อในเนื้อหาอย่างเหมาะสมและใส่เครื่องหมาย Markdown (#) ดังนี้:
     - ชื่อหนังสือ/ชื่อบทหลัก: ใช้ `#`
     - หัวข้อหลักในบท: ใช้ `##`
     - หัวข้อย่อยระดับแรก: ใช้ `###`
     - หัวข้อย่อยระดับสอง: ใช้ `####`
     - หัวข้อย่อยระดับสามหรือต่ำกว่า: ใช้ `#####`
   - กฎการระบุหัวข้อ:
     - ข้อความบรรทัดเดียวที่ค่อนข้างสั้น (ปกติสั้นกว่า 50 ตัวอักษร)
     - ข้อความที่เป็นการสรุปภาพรวมหรือประเด็น
     - ทำหน้าที่จัดแบ่งโครงสร้างของเอกสาร
     - ขนาดตัวอักษรหรือรูปแบบแตกต่างจากข้อความปกติอย่างเห็นได้ชัด
     - มีตัวเลขบทหรือข้อประกอบ (เช่น "1.1 ภาพรวม", "บทที่ 3" เป็นต้น)
   - ข้อควรระวัง:
     - อย่าใส่เครื่องหมายหัวข้อกับข้อความย่อหน้าปกติเด็ดขาด
     - หากต้นฉบับมีเครื่องหมายหัวข้อ Markdown อยู่แล้ว ให้คงโครงสร้างระดับหัวข้อนั้นไว้{term_table_part}{neighbor_part}

โปรดแปลไฟล์ {chunk_path} และบันทึกคำแปล Markdown เป็นไฟล์ภาษาไทยที่ {os.path.join(temp_dir, 'output_' + chunk_filename)}
และเขียนผลลัพธ์ข้อมูลการตรวจสอบเอนทิตีและการแปลเป็นไฟล์ JSON ที่ {os.path.join(temp_dir, 'output_' + chunk_filename.replace('.md', '.meta.json'))} ในรูปแบบ schema ดังนี้:
{{
  "schema_version": 1,
  "new_entities": [],
  "alias_hypotheses": [],
  "attribute_hypotheses": [],
  "used_term_sources": [],
  "conflicts": []
}}
โปรดแสดงเฉพาะผลลัพธ์คำแปลไฟล์ Markdown สุดท้ายเท่านั้น ห้ามเขียนอธิบาย ทักทาย แนะนำ หรือแสดงข้อความพูดคุยอื่นๆ ใดๆ ทั้งสิ้น
"""
    return prompt

if __name__ == '__main__':
    temp_dir = sys.argv[1]
    start = int(sys.argv[2])
    end = int(sys.argv[3])
    
    subagents = []
    for i in range(start, end + 1):
        chunk_filename = f"chunk{i:04d}.md"
        prompt = get_args(temp_dir, chunk_filename)
        subagents.append({
            "TypeName": "self",
            "Role": f"Translator for chunk{i:04d}",
            "Prompt": prompt
        })
    print(json.dumps(subagents, ensure_ascii=False, indent=2))
