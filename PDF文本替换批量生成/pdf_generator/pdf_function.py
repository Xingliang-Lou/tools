import os
from pdf_generator import utils
import math

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

def add_text_to_page(page, text, x0, y0, character_space, font_size):
    if character_space is None:
        page.insert_text((x0, y0), text, fontsize=font_size, overlay=True,
                         fontname="song", fontfile=font)
    else:
        for i in range(len(text)):
            single_text = text[i]
            dx = i * character_space
            page.insert_text((x0 + dx, y0), single_text, fontsize=font_size, overlay=True,
                             fontname="song", fontfile=font)



def count_chinese_and_non_chinese(s):
    chinese_count = 0
    non_chinese_count = 0

    for char in s:
        if '\u4e00' <= char <= '\u9fff':
            chinese_count += 1
        else:
            non_chinese_count += 1

    return chinese_count, non_chinese_count

def replace_pdf_text(document, change_info, replace_text):
    target_text = change_info.get("target_text")
    dx = change_info.get("dx")
    if dx is None:
        dx = 0

    dy = change_info.get("dy")
    if dy is None:
        dy = 0

    for page in document:
        text_instances = page.search_for(target_text)

        for inst in text_instances:
            # 删除旧文本
            page.add_redact_annot(inst, fill=(1, 1, 1))
            page.apply_redactions()

            # 自动计算字体
            font_size = change_info.get("font_size")
            if font_size is None:
                font_size = min(inst.height, inst.width)

            # 计算新文本行数
            line_limit = change_info.get("line_limit")
            if line_limit is None:
                line_num = 1
            else:
                line_num = math.ceil(len(replace_text)/line_limit)
            line_space = change_info.get("line_space")
            if line_space is None:
                line_space = 1.5

            # 计算y0起点
            vertical_align = change_info.get("vertical_align")
            if vertical_align == "center":
                y0 = (inst.y0 + inst.y1 + font_size - (line_num-1)*font_size*line_space)/2
            else:
                y0 = inst.y1

            # 从y0开始一行行往下加字段
            for i in range(line_num):
                replace_text_this_line = replace_text[:line_limit]
                character_space = change_info.get("character_space")
                if character_space == "auto":
                    character_space = max(inst.height, inst.width) / len(target_text)

                horizontal_align = change_info.get("horizontal_align")
                if horizontal_align == "center":
                    chinese_count, non_chinese_count = count_chinese_and_non_chinese(replace_text_this_line)
                    x0 = (inst.x0 + inst.x1)/2 - (chinese_count * font_size + non_chinese_count * font_size /2)/2
                else:
                    x0 = inst.x0
                add_text_to_page(page, replace_text_this_line, x0 + dx,  y0 + dy, character_space, font_size)
                replace_text = replace_text[line_limit:]
                y0 += font_size*line_space
