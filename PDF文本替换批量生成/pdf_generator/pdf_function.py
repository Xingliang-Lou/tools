import os
from pdf_generator import utils

font = os.path.join(utils.get_base_path(), 'asserts/simsun.ttc')

def get_text_details(document, target_text):
    for page in document:
            # 获取页面上的所有文本块
            text_instances = page.search_for(target_text)
            for inst in text_instances:
                # 获取文本块的矩形区域
                rect = inst
                # 提取文本内容
                text = page.get_textbox(rect)
                if target_text in text:
                    # 获取文本块中的字体信息
                    blocks = page.get_text("dict")["blocks"]
                    for block in blocks:
                        if "lines" in block:
                            for line in block["lines"]:
                                for span in line["spans"]:
                                    if target_text in span["text"]:
                                        font_size = span["size"]
                                        font_name = span["font"]
                                        position = (rect.x0, rect.y0, rect.x1, rect.y1)
                                        return {
                                            "font_size": font_size,
                                            "font_name": font_name,
                                            "position": position
                                        }
    return None

def replace_pdf_text(document, target_text, replace_text, dx, dy, distance):
    for page in document:
        text_instances = page.search_for(target_text)
        for inst in text_instances:
            # 删除旧文本
            page.add_redact_annot(inst, fill=(1, 1, 1))
            page.apply_redactions()

            if distance == 0:
                page.insert_text((inst.x0+dx, inst.y1+dy), replace_text, fontsize=9, overlay=True, fontname="song", fontfile=font)
            else:
                for i in range(len(replace_text)):
                    single_text = replace_text[i]
                    this_dx = dx + i * distance
                    page.insert_text((inst.x0+this_dx, inst.y1+dy), single_text, fontsize=9, overlay=True, fontname="song", fontfile=font)
