from django.shortcuts import render
from urllib.request import urlretrieve
from bs4 import BeautifulSoup
from pathlib import Path
import os
import requests
from django.conf import settings
from .models import Product, Product_Color

ktshop_url = "https://shop.kt.com/smart/agncyInfoView.do?vndrNo=AA01344&sortProd=SALE"

def mall_product_list(request):
    item_name = {}
    item_price = {}
    item_code = {}
    thumbs_link = {}
    color_name = {}
    color_code = {}
    #local_imgs_path = "/home/honeycomms/honeycomms_presite/mall/static/imgs/device_imgs/"
    #local_device_imgs_path = Path("/static/imgs/device_imgs/")
    local_device_imgs_path = os.path.join(settings.STATIC_ROOT, "imgs/device_imgs/")
    local_device_imgs_list = os.listdir(local_device_imgs_path)

    req = requests.get(ktshop_url)
    bsObj = BeautifulSoup(req.text, "html.parser")
    thumbs_blocks = bsObj.findAll("div", {"class": "thumbs"})
    prodInfo_blocks = bsObj.findAll("div", {"class": "prodInfo"})

    for idx, prodInfo in enumerate(prodInfo_blocks):
        item_name[idx] = prodInfo.ul.find("li", {"class": "prodName"}).text
        item_price[idx] = prodInfo.ul.find("li", {"class": "prodPrice"}).span.text
        href_value = prodInfo.ul.find("li", {"class": "prodSupport"}).findAll("a")[0].attrs['href']
        item_code[idx] = href_value[25:35]

    for idx, thumbs in enumerate(thumbs_blocks):
        thumbs_link[idx] = thumbs.findAll("img")[0].attrs['src']
        color_blocks = thumbs.find("ul", {"class": "optColor"}).findAll("li")

        # 기종사진 폴더에 이 기종의 이미지 파일이 없으면, 지금 읽어들인 링크의 단말이미지를 저장
        if (item_name[idx] + ".png") not in local_device_imgs_list:
            print("%s image file saving...\n", item_name[idx])
            urlretrieve(thumbs_link[idx], local_device_imgs_path + item_name[idx] + ".png")

        for idx2, color_blocks in enumerate(color_blocks):
            color_name[idx2] = color_blocks.find("span").text
            temp_color_code = color_blocks.find("span").attrs['style']
            color_code[idx2] = temp_color_code[17:24]

            # 기존 DB에 지금의 기종명+색상명과 일치하는 row가 없으면, 지금의 기종명+색상명 데이터를 Product_Color 테이블의 새로운 레코드로 추가
            if len(Product_Color.objects.filter(combi_name=item_name[idx]+"-"+color_name[idx2]))==0:
                Product_Color(combi_name=item_name[idx]+"-"+color_name[idx2], device_name=item_name[idx], color_name=color_name[idx2], color_code=color_code[idx2]).save()

        # 기존 DB에 이 기종명+가격과 일치하는 row가 없으면
        if len(Product.objects.filter(device_name=item_name[idx], device_price=item_price[idx]))==0:

            # 기존 DB에 이 기종명과 일치하는 row가 없으면, 지금의 전체 정보(기종명,가격,코드,이미지위치)를 Product 테이블의 새로운 레코드로 추가
            if len(Product.objects.filter(device_name=item_name[idx])) == 0:
                print("%s info saving...\n", item_name[idx])
                Product(device_name=item_name[idx], device_price=item_price[idx], device_code=item_code[idx], img_link=local_device_imgs_path+item_name[idx]+".png").save()
            # 기존 DB에 이 기종명과 일치하는 row가 있으면, 가격정보만 업데이트
            else:
                print("%s price updating...\n", item_name[idx])
                product = Product.objects.get(device_name=item_name[idx])
                product.device_price = item_price[idx]
                product.save()


    products = Product.objects.filter()
    product_colors = Product_Color.objects.filter()

    return render(request, 'mall/mall_main.html', {'products': products, 'product_colors': product_colors})