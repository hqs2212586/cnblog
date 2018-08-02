# -*- coding:utf-8 -*-
__author__ = 'Qiushi Huang'

import random


def get_random_color():
    # 随机颜色
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))


def get_valid_code_imge(request):
    # 方式一：不推荐把程序写死了
    # with open("lufei.jpg", "rb") as f:
    #     data = f.read()

    # 方式二：pip3 install pillow
    # from PIL import Image
    # img = Image.new("RGB", (270, 40), color=get_random_color())  # 得到img对象，颜色三要素：红绿蓝
    #
    # with open("validCode.png", "wb") as f:
    #     img.save(f, "png")    # 保存动态生成的图片
    #
    # with open("validCode.png", "rb") as f:
    #     data = f.read()

    # 方式三：需要引入BytesIO
    # from PIL import Image
    # from io import BytesIO
    # img = Image.new("RGB", (270, 40), color=get_random_color())  # 得到img对象，颜色三要素：红绿蓝
    #
    # # f为内存句柄
    # f= BytesIO()    #
    # # 保存图片
    # img.save(f, "png")
    # data = f.getvalue()

    # 方式四：添加验证码文字信息
    # from PIL import Image, ImageDraw,ImageFont
    # from io import BytesIO
    #
    # img = Image.new("RGB", (270, 40), color=get_random_color())  # 得到img对象，颜色三要素：红绿蓝
    # # 创建Draw对象
    # draw = ImageDraw.Draw(img)
    # # 创建Font对象
    # kumo_font = ImageFont.truetype("static/font/kumo.ttf", size=26)
    # draw.text((0,5), "python", get_random_color(), font=kumo_font)
    # """
    # draw.text()   写文字
    #     参数：  xy:坐标   text:文本内容   fill:文本颜色  font：文本样式
    # draw.line()   画线
    # draw.point()  画点
    # """
    # f = BytesIO()   # f为内存句柄
    # img.save(f, "png")
    # data = f.getvalue()

    # 方式五：修改为随机字符串
    from PIL import Image, ImageDraw, ImageFont
    from io import BytesIO

    img = Image.new("RGB", (270, 40), color=get_random_color())  # 得到img对象，颜色三要素：红绿蓝
    # 创建Draw对象
    draw = ImageDraw.Draw(img)
    # 创建Font对象
    kumo_font = ImageFont.truetype("static/font/kumo.ttf", size=28)

    # 随机字母：
    """
    >>> chr(65)
    'A'
    >>> chr(90)
    'Z'
    >>> chr(97)
    'a'
    >>> chr(122)
    'z'
    """
    valid_code_str = ""

    for i in range(5):
        random_num = str(random.randint(0, 9))  # 随机数字
        random_low_alpha = chr(random.randint(95, 122))  # 随机小写字母
        random_upper_alpha = chr(random.randint(65, 90))  # 随机大写字母

        # 三选一：choice() 方法返回一个列表，元组或字符串的随机项。注意：choice()是不能直接访问的，需要导入 random 模块，然后通过 random 静态对象调用该方法。
        random_char = random.choice([random_num, random_low_alpha, random_upper_alpha])
        draw.text((i * 50 + 20, 5), random_char, get_random_color(), font=kumo_font)  # 坐标错开间距

        # 保存验证码字符串
        valid_code_str += random_char

    # 给验证码图片添加噪点噪线
    # width = 270
    # height = 40
    # for i in range(10):
    #     x1 = random.randint(0, width)
    #     x2 = random.randint(0, width)
    #     y1 = random.randint(0, height)
    #     y2 = random.randint(0, height)
    #     draw.line((x1, y1, x2, y2), fill = get_random_color())   # 画出一条线
    #
    # for i in range(50):
    #     draw.point([random.randint(0, width), random.randint(0, height)], fill=get_random_color())   # 画点
    #     x = random.randint(0, width)
    #     y = random.randint(0, height)
    #     draw.arc((x, y, x + 4, y +4), 0, 90, fill=get_random_color())

    print("valid_code_str", valid_code_str)  # valid_code_str Ms4v0

    # 为什么用request.session：
    # 因为session本身就是一个会话跟踪，能够保存上一次做的行为、操作、数据，因此利用它能完成验证码验证
    request.session["valid_code_str"] = valid_code_str
    """
    1 生成一个随机字符串
    2 设置一个COOKIE，{"sessionid":"刚刚生成的随机字符串"}
    3 django-session表中存储 session-key     session-data
                            随机字符串       {"valid_code_str": "随机验证码字符"}
    """

    f = BytesIO()  # f为内存句柄
    img.save(f, "png")
    data = f.getvalue()

    return data