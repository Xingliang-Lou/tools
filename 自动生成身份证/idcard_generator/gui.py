import os
import sys
import tkinter
from tkinter.filedialog import *
from tkinter.messagebox import *
from tkinter.ttk import *

import PIL.Image as PImage
import cv2
import numpy
from PIL import ImageFont, ImageDraw

from idcard_generator import utils, id_card_utils
import csv

asserts_dir = os.path.join(utils.get_base_path(), 'asserts')
print("asserts_dir", asserts_dir)


def set_entry_value(entry, value):
    entry.delete(0, tkinter.END)
    entry.insert(0, value)


def change_background(img, img_back, zoom_size, center):
    # 缩放
    img = cv2.resize(img, zoom_size)
    rows, cols, channels = img.shape

    # 转换hsv
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # 获取mask
    # lower_blue = np.array([78, 43, 46])
    # upper_blue = np.array([110, 255, 255])
    diff = [5, 30, 30]
    gb = hsv[0, 0]
    lower_blue = numpy.array(gb - diff)
    upper_blue = numpy.array(gb + diff)
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    # cv2.imshow('Mask', mask)

    # 腐蚀膨胀
    erode = cv2.erode(mask, None, iterations=1)
    dilate = cv2.dilate(erode, None, iterations=1)

    # 粘贴
    for i in range(rows):
        for j in range(cols):
            if dilate[i, j] == 0:  # 0代表黑色的点
                img_back[center[0] + i, center[1] + j] = img[i, j]  # 此处替换颜色，为BGR通道

    return img_back


def paste(avatar, bg, zoom_size, center):
    avatar = cv2.resize(avatar, zoom_size)
    rows, cols, channels = avatar.shape
    for i in range(rows):
        for j in range(cols):
            bg[center[0] + i, center[1] + j] = avatar[i, j]
    return bg


class IDGen:
    def random_data(self):
        set_entry_value(self.eName, "张三")
        set_entry_value(self.eSex, "男")
        set_entry_value(self.eNation, "汉")
        set_entry_value(self.eYear, "1995")
        set_entry_value(self.eMon, "7")
        set_entry_value(self.eDay, "17")
        set_entry_value(self.eAddr, "四川省成都市武侯区益州大道中段722号复城国际")
        set_entry_value(self.eIdn, id_card_utils.random_card_no(birth_date="19950717"))
        set_entry_value(self.eOrg, "四川省成都市锦江分局")
        set_entry_value(self.eLife, "2010.01.01-2020.12.12")

    def batch_generator(self):
        csv_path = askopenfilename(initialdir=os.getcwd(), title='选择CSV文件')
        with open(csv_path, mode='r') as file:
            csv_reader = csv.reader(file)
            header = next(csv_reader)
            for row in csv_reader:
                set_entry_value(self.eName, row[0])
                set_entry_value(self.eSex, row[1])
                set_entry_value(self.eNation, row[2])
                set_entry_value(self.eYear, row[3])
                set_entry_value(self.eMon, row[4])
                set_entry_value(self.eDay, row[5])
                set_entry_value(self.eAddr, row[6])
                set_entry_value(self.eIdn, row[7])
                set_entry_value(self.eOrg, row[8])
                set_entry_value(self.eLife, row[9])
                try:
                    self.generator(row[10], row[0])
                except Exception as e:
                    pass

    def generator(self, photo_path=None, name = None):
        if photo_path is None:
            f_name = askopenfilename(initialdir=os.getcwd(), title='选择头像')
            if len(f_name) == 0:
                return
        else:
            f_name = photo_path
        avatar = PImage.open(f_name).convert("RGBA")  # 确保图像是RGBA模式
        empty_image = PImage.open(os.path.join(asserts_dir, 'empty.png')).convert("RGBA")  # 确保背景图也是RGBA模式
        A4_image = PImage.open(os.path.join(asserts_dir, 'A4.jpg')).convert("RGBA")

        name_font = ImageFont.truetype(os.path.join(asserts_dir, 'fonts/hei.ttf'), 72)
        other_font = ImageFont.truetype(os.path.join(asserts_dir, 'fonts/hei.ttf'), 64)
        birth_date_font = ImageFont.truetype(os.path.join(asserts_dir, 'fonts/fzhei.ttf'), 60)
        id_font = ImageFont.truetype(os.path.join(asserts_dir, 'fonts/ocrb10bt.ttf'), 90)

        draw = ImageDraw.Draw(empty_image)
        draw.text((630, 690), self.eName.get(), fill=(0, 0, 0), font=name_font)
        draw.text((630, 840), self.eSex.get(), fill=(0, 0, 0), font=other_font)
        draw.text((1030, 840), self.eNation.get(), fill=(0, 0, 0), font=other_font)
        draw.text((630, 975), self.eYear.get(), fill=(0, 0, 0), font=birth_date_font)
        mon = self.eMon.get()
        if len(mon) == 1:
            draw.text((961, 975), mon, fill=(0, 0, 0), font=birth_date_font)
        else:
            draw.text((949, 975), mon, fill=(0, 0, 0), font=birth_date_font)
        day = self.eDay.get()
        if len(day) == 1:
            draw.text((1154, 975), self.eDay.get(), fill=(0, 0, 0), font=birth_date_font)
        else:
            draw.text((1140, 975), self.eDay.get(), fill=(0, 0, 0), font=birth_date_font)

        # 住址
        addr_loc_y = 1115
        addr_lines = self.get_addr_lines()
        for addr_line in addr_lines:
            draw.text((630, addr_loc_y), addr_line, fill=(0, 0, 0), font=other_font)
            addr_loc_y += 100

        # 身份证号
        draw.text((900, 1475), self.eIdn.get(), fill=(0, 0, 0), font=id_font)

        # 背面
        draw.text((1050, 2750), self.eOrg.get(), fill=(0, 0, 0), font=other_font)
        life = self.eLife.get()
        life_split = life.split(".")
        draw.text((1050, 2895), life_split[0]+".", fill=(0, 0, 0), font=other_font)
        draw.text((1195, 2895), life_split[1]+".", fill=(0, 0, 0), font=other_font)
        draw.text((1275, 2895), life_split[2]+".", fill=(0, 0, 0), font=other_font)
        draw.text((1515, 2895), life_split[3]+".", fill=(0, 0, 0), font=other_font)
        draw.text((1595, 2895), life_split[4], fill=(0, 0, 0), font=other_font)

        if self.eBgvar.get():
            avatar = cv2.cvtColor(numpy.asarray(avatar), cv2.COLOR_RGBA2BGRA)
            empty_image = cv2.cvtColor(numpy.asarray(empty_image), cv2.COLOR_RGBA2BGRA)
            empty_image = change_background(avatar, empty_image, (500, 670), (690, 1500))
            empty_image = PImage.fromarray(cv2.cvtColor(empty_image, cv2.COLOR_BGRA2RGBA))
        else:
            avatar = avatar.resize((500, 670))
            avatar = avatar.convert('RGBA')
            empty_image.paste(avatar, (1500, 690), mask=avatar)
            # im = paste(avatar, im, (500, 670), (690, 1500))


        resized_image = empty_image.resize((1330, 1882))
        A4_image.paste(resized_image, (570, 690), mask=resized_image)
        # resized_image = empty_image.resize((5000, 5000))
        if name is None:
            A4_image.save('color.png', format='PNG')
            A4_image.convert('L').save('bw.png', format='PNG')
        else:
            A4_image.save('{}_color.png'.format(name), format='PNG')
            A4_image.convert('L').save('{}_bw.png'.format(name), format='PNG')
        # showinfo('成功', '文件已生成到目录下,黑白bw.png和彩色color.png')

    def show_ui(self, root):
        root.title('身份证图片生成器')
        # root.geometry('640x480')
        root.resizable(width=False, height=False)
        # link = Label(root, text='请遵守法律法规，获取帮助:', cursor='hand2', foreground="#FF0000")
        # link.grid(row=0, column=0, sticky=tkinter.W, padx=3, pady=3, columnspan=3)
        # link.bind("<Button-1>", utils.open_url)

        # link = Label(root, text='https://github.com/bzsome', cursor='hand2', foreground="blue")
        # link.grid(row=0, column=2, sticky=tkinter.W, padx=26, pady=3, columnspan=4)
        #link.bind("<Button-1>", utils.open_url)

        Label(root, text='姓名:').grid(row=1, column=0, sticky=tkinter.W, padx=3, pady=3)
        self.eName = Entry(root, width=8)
        self.eName.grid(row=1, column=1, sticky=tkinter.W, padx=3, pady=3)
        Label(root, text='性别:').grid(row=1, column=2, sticky=tkinter.W, padx=3, pady=3)
        self.eSex = Entry(root, width=8)
        self.eSex.grid(row=1, column=3, sticky=tkinter.W, padx=3, pady=3)
        Label(root, text='民族:').grid(row=1, column=4, sticky=tkinter.W, padx=3, pady=3)
        self.eNation = Entry(root, width=8)
        self.eNation.grid(row=1, column=5, sticky=tkinter.W, padx=3, pady=3)
        Label(root, text='出生年:').grid(row=2, column=0, sticky=tkinter.W, padx=3, pady=3)
        self.eYear = Entry(root, width=8)
        self.eYear.grid(row=2, column=1, sticky=tkinter.W, padx=3, pady=3)
        Label(root, text='月:').grid(row=2, column=2, sticky=tkinter.W, padx=3, pady=3)
        self.eMon = Entry(root, width=8)
        self.eMon.grid(row=2, column=3, sticky=tkinter.W, padx=3, pady=3)
        Label(root, text='日:').grid(row=2, column=4, sticky=tkinter.W, padx=3, pady=3)
        self.eDay = Entry(root, width=8)
        self.eDay.grid(row=2, column=5, sticky=tkinter.W, padx=3, pady=3)
        Label(root, text='住址:').grid(row=3, column=0, sticky=tkinter.W, padx=3, pady=3)
        self.eAddr = Entry(root, width=32)
        self.eAddr.grid(row=3, column=1, sticky=tkinter.W, padx=3, pady=3, columnspan=5)
        Label(root, text='证件号码:').grid(row=4, column=0, sticky=tkinter.W, padx=3, pady=3)
        self.eIdn = Entry(root, width=32)
        self.eIdn.grid(row=4, column=1, sticky=tkinter.W, padx=3, pady=3, columnspan=5)
        Label(root, text='签发机关:').grid(row=5, column=0, sticky=tkinter.W, padx=3, pady=3)
        self.eOrg = Entry(root, width=32)
        self.eOrg.grid(row=5, column=1, sticky=tkinter.W, padx=3, pady=3, columnspan=5)
        Label(root, text='有效期限:').grid(row=6, column=0, sticky=tkinter.W, padx=3, pady=3)
        self.eLife = Entry(root, width=32)
        self.eLife.grid(row=6, column=1, sticky=tkinter.W, padx=3, pady=3, columnspan=5)
        Label(root, text='选项:').grid(row=7, column=0, sticky=tkinter.W, padx=3, pady=3)
        self.eBgvar = tkinter.IntVar()
        self.ebg = Checkbutton(root, text='自动抠图', variable=self.eBgvar)
        self.ebg.grid(row=7, column=1, sticky=tkinter.W, padx=3, pady=3, columnspan=5)

        # random_btn = Button(root, text='随机', width=8, command=self.random_data)
        random_btn = Button(root, text='批量生成', width=8, command=self.batch_generator)
        random_btn.grid(row=8, column=0, sticky=tkinter.W, padx=16, pady=3, columnspan=2)
        generator_btn = Button(root, text='选择头像并生成', width=24, command=self.generator)
        generator_btn.grid(row=8, column=2, sticky=tkinter.W, padx=1, pady=3, columnspan=4)

    # 获得要显示的住址数组
    def get_addr_lines(self):
        addr = self.eAddr.get()
        addr_lines = []
        start = 0
        while start < utils.get_show_len(addr):
            show_txt = utils.get_show_txt(addr, start, start + 22)
            addr_lines.append(show_txt)
            start = start + 22

        return addr_lines

    def run(self):
        root = tkinter.Tk()
        self.show_ui(root)
        ico_path = os.path.join(asserts_dir, 'ico.ico')
        root.iconbitmap(ico_path)
        root.protocol('WM_DELETE_WINDOW', lambda: sys.exit(0))
        root.mainloop()
