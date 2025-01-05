import os
import sys
import tkinter
from tkinter.filedialog import *
from tkinter.ttk import *
import fitz  # PyMuPDF
import csv
from pdf_generator import utils
from pdf_generator.pdf_function import *
import json

asserts_dir = os.path.join(utils.get_base_path(), 'asserts')
# asserts_dir = os.path.join(utils.get_base_path(), 'demo/网上银行交易详细清单')


class PDFGen:
    def __init__(self):
        self._csv_path = None
        self._save_path = None
        self._font = os.path.join(utils.get_base_path(), "asserts/simsun.ttc")
        self._change_list_path = os.path.join(asserts_dir, "change_list.json")
        #============test=================
        # self._save_path = os.path.join(utils.get_base_path(), 'generate')
        # self._csv_path = os.path.join(asserts_dir, "context.csv")

        with open(self._change_list_path, "r", encoding="utf-8") as f:
            change_list_json = json.load(f)
            self._title = change_list_json["title"]
            self._base_pdf_path = os.path.join(asserts_dir, change_list_json["base_pdf"])
            self._change_list = change_list_json["change_list"]
            self._name_row = change_list_json["name_row"]
            self._change_length = len(self._change_list)


    def show_ui(self, root):
        root.title(self._title)
        root.geometry('400x80')
        root.resizable(width=False, height=False)

        # 选择CSV
        csv_path_set_btn = Button(root, text='选择CSV', width=12, command=self. set_csv_path)
        csv_path_set_btn.grid(row=0, column=0, sticky=tkinter.W)
        self._csv_path_label = Label(root, text='CSV路径：未选择')
        self._csv_path_label.grid(row=0, column=1, sticky=tkinter.W)

        # 选择保存路径
        save_path_set_btn = Button(root, text='选择保存路径', width=12, command=self.set_save_path)
        save_path_set_btn.grid(row=1, column=0, sticky=tkinter.W)
        self._save_path_label = Label(root, text='保存路径：未选择')
        self._save_path_label.grid(row=1, column=1, sticky=tkinter.W)

        #开始按钮
        # 选择保存路径
        save_path_set_btn = Button(root, text='开始批量生成', width=12, command=self.generate_pdf)
        save_path_set_btn.grid(row=2, column=0, sticky=tkinter.W)
        self._run_label = Label(root, text='当前状态：未开始')
        self._run_label.grid(row=2, column=1, sticky=tkinter.W)

        # self.generate_pdf()

    def run(self):
        root = tkinter.Tk()
        self.show_ui(root)
        root.protocol('WM_DELETE_WINDOW', lambda: sys.exit(0))
        root.mainloop()

    def set_csv_path(self):
        self._csv_path = askopenfilename(initialdir=os.getcwd(), title='选择CSV文件')
        self._csv_path_label.config(text="CSV路径：{}".format(self._csv_path))

    def set_save_path(self):
        self._save_path = askdirectory(initialdir=os.getcwd(), title='选择保存路径')
        self._save_path_label.config(text="保存路径：{}".format(self._save_path))

    def generate_pdf(self):
        if self._csv_path is None:
            self._run_label.config(text="当前状态：CSV文件未选择")
            return
        if self._save_path is None:
            self._run_label.config(text="当前状态：保存路径未选择")
            return
        with open(self._csv_path, mode='r') as file:
            csv_reader = csv.reader(file)
            header = next(csv_reader)
            for row in csv_reader:
                if len(row) != self._change_length:
                    print("CSV长度与预设长度不符")
                    continue
                document = fitz.open(self._base_pdf_path)

                for i in range(self._change_length):
                    change_info = self._change_list[i]
                    replace_text = row[i]
                    replace_pdf_text(document, change_info, replace_text)
                name = row[self._name_row]
                output_path = os.path.join(self._save_path, name)+".pdf"
                print(output_path)

                x = 365
                y = 445
                rect = fitz.Rect(x, y, x+74, y+50)
                document[0].insert_image(rect, filename=os.path.join(asserts_dir, "公章.png"))

                self._run_label.config(text="当前状态：正在生成{}".format(output_path))
                document.save(output_path)
                document.close()

        self._run_label.config(text="当前状态：完成")

