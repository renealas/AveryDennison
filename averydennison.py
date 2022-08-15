from fileinput import filename
from hashlib import new, sha256
from operator import mod
from pyexpat import model
from tokenize import Name
from turtle import title
import json
from bs4 import BeautifulSoup
from typing import Optional, List
from dataclasses import dataclass, field

from numpy import append, tile

from dataclasses_json import dataclass_json, config
import datetime
import requests
from datetime import datetime

from vdataclass import Firmware

MANIFEST_URL = 'https://printers.averydennison.com/en/home/resources/service-and-support.html'


@dataclass_json
@dataclass
class VendorMetadata:
    product_family: str
    model: str
    os: str
    landing_urls: Optional[List[str]] = field(
        default=None, metadata=config(exclude=lambda x: x is None)
    )
    firmware_urls: Optional[str] = field(
        default=None, metadata=config(exclude=lambda x: x is None)
    )
    bootloader_url: Optional[str] = field(
        default=None, metadata=config(exclude=lambda x: x is None)
    )
    release_notes_url: Optional[str] = field(
        default=None, metadata=config(exclude=lambda x: x is None)
    )
    md5_url: Optional[str] = field(
        default=None, metadata=config(exclude=lambda x: x is None)
    )
    data: Optional[str] = field(
        default=None, metadata=config(exclude=lambda x: x is None)
    )


def find_nth(haystack, needle, n):
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start+len(needle))
        n -= 1
    return start


def main():
    # Printing the List[Firmware] of the function output_firmware.
    manifest = get_manifest(MANIFEST_URL)
    output_firmware(manifest)

def find_nth(haystack, needle, n):
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start+len(needle))
        n -= 1
    return start

def output_firmware(manifest_url: str) -> List[Firmware]:
    vendor_firmwares = []

    firmwareInfoData = []
    for m in manifest_url:
        if m.data != None:
            firmwareInfoData.append(m.data)
    
    for data in firmwareInfoData:
         # web page with firmware list
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
        }
        response = requests.request("GET", data, headers=headers)
        html = response.content
        response.close()
        soup = BeautifulSoup(html, 'html.parser')

        # Here we get the Name of the Device for the Firmware
        title = soup.find('div', {'class': 'page-title'}).find('h1').text
        
        ays = soup.find_all('a')
        for a in ays:
            aText = a.text.strip()
            if 'firmware' in aText:
                firmwareInfoData = a
        
        # Here we get the URL of the Firmware 
        url = firmwareInfoData.get('href')

        #Get filename 
        lastSlash =  url.rfind('/')
        urlLength = len(url)

        filenameData = url[lastSlash + 1: urlLength]

        #Filename for the firmware
        filename = filenameData.replace('%20', '')

        #version of the firmware
        versionPosition = filename.find('Version')
        version = filename[versionPosition + 7 : versionPosition + 11]
        
        a = Firmware(
            version =  version,
            models = [title],
            filename = filename,
            url = url,
        )
        print(a)
        vendor_firmwares.append(a)

    return vendor_firmwares


def get_manifest(manifest_url: str) -> List[VendorMetadata]:

    averyDennison_models = []

    # web page with firmware list
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
    }
    response = requests.request("GET", manifest_url, headers=headers)
    html = response.content
    response.close()
    soup = BeautifulSoup(html, 'html.parser')

    devicesContainers = soup.find_all('div', {'class': 'row-align-middle'})

    for device in devicesContainers:
        name = device.find('b').text
        fullInfo = device.find('p').text
        description = fullInfo.replace(name, "").strip()

        if 'Firmware' in description:
            deviceUrl ='https://printers.averydennison.com' + device.find('div',{'class': 'button'}).find('a').get('href')
            a = VendorMetadata(
                product_family = None,
                model = name,
                os = None,
                data = deviceUrl,
            )
            averyDennison_models.append(a)  
    
    return averyDennison_models


if __name__ == "__main__":
    main()
