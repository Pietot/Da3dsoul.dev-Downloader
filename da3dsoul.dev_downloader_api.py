"""
Downloads images from the first to the latest from https://da3dsoul.dev using it's API
"""


# By Pietot
# Discord : Piétôt#1754
# Start : 18/08/2023 at 00h13 FR
# End : 25/08/2023 FR


import winsound
import shutil
import time
import json
import os
import re

import natsort as nat
import requests as r


def get_download_path() -> str:
    """ Get the download path 

    Returns:
        str: The download path 
    """
    if os.path.exists('settings.json'):
        with open('settings.json', encoding='utf-8') as data:
            settings: dict[str, str] = json.load(data)
        return settings.get('download_path', 'Download path is not defined in settings.json')
    while True:
        download_folder = input(
            'Paste a path to a directory where images will be downloaded:\n')
        if os.path.isdir(download_folder):
            break
        print('Directory you entered is invalid')
    with open('settings.json', 'a+', encoding='utf-8') as data:
        data.seek(0)
        settings = {'download_path': download_folder}
        json.dump(settings, data)
    return settings.get('download_path', 'Download path is not defined in settings.json')


def get_last_id_downloaded() -> int:
    """ Function to retrieve the last id we've downloaded

    Returns:
        int: The last id we've downloaded
    """
    with open('Log.txt', 'a+', encoding='utf-8') as filout:
        filout.seek(0)
        return len(filout.readlines()) + 1


def get_last_id() -> int:
    """ Function that retrieves the last id of the last image posted on the site

    Returns:
        int: The id of the last image posted
    """
    while (source_code := r.get('https://da3dsoul.dev/Search', timeout=10)).status_code != 200:
        continue
    source_code = source_code.content.decode('utf-8')
    source_code = re.split(
        'content="https://da3dsoul.dev/api/Image/|\\?size=small', source_code)[1]
    return int(source_code.split('/')[0])


def get_key_image(img_id: int) -> str:
    """ Get the key of an image. Example : https://da3dsoul.dev/api/Image/1/92243038_p1.jpg,
        92243038_p1.jpg is the key

    Args:
        img_id (int): The number of an image like the first, the 28th or the 4725th

    Returns:
        str: The key or KeyError if there is no key
    """
    json_data: dict[str, list[dict[str, str]]] = json.loads(
        r.get(f'https://da3dsoul.dev/api/Image/{img_id}', timeout=10).content.decode('utf-8'))
    for source in json_data["sources"]:
        if (key := source.get('originalFilename')):
            return key
    return 'KeyError'


def download_image(key: str) -> None:
    """ Download an image

    Args:
        key (str): The key of the image we want to download

    Returns:
        None
    """
    img_link = f'https://da3dsoul.dev/api/Image/{current_id}/{key}'
    if key == 'KeyError':
        with open('Log.txt', 'a', encoding='utf-8') as filout:
            filout.write(
                f"{img_link} > Code Error : Key Error > Image is no longer on the site !\n")
        return None
    try:
        request = r.get(img_link, stream=True, timeout=20)
    except r.exceptions.ReadTimeout:
        if r.get('https://da3dsoul.dev', timeout=10).status_code:
            with open('Log.txt', 'a', encoding='utf-8') as filout:
                filout.write(
                    f"{img_link} > Code Error : Image Error > Image is undownloadable !\n")
                return None
        print('https://da3dsoul.dev/ is down, waiting one hour, you can close and relaunch later')
        time.sleep(3600)
        download_image(key)
        return None
    filename = str(current_id) + key[-4:]
    with open(filename, 'wb') as download_img:
        shutil.copyfileobj(request.raw, download_img)
    print(filename, 'Downloaded !')
    move_file(filename, img_link)
    return None


def move_file(filename: str, link: str) -> None:
    """ Move the image from the exe's directory to the download path

    Args:
        filename (str): The name of the file
        link (str): The link of the image
    """
    while True:
        try:
            shutil.move(
                filename, f'{DOWNLOAD_PATH}\\Pack #{number_subfile}')
            break
        except (shutil.Error, PermissionError):
            try:
                os.remove(filename)
                with open(
                        'Error File.txt', 'a+', encoding='utf-8') as filout:
                    filout.seek(0)
                    filout.write(f'{link} > Shifting Error\n')
                break
            except (shutil.Error, PermissionError):
                pass
    with open('Log.txt', 'a', encoding='utf-8') as filout:
        filout.write(
            f'{link} > Successfully Downloaded ! > {filename}\n')


if __name__ == "__main__":
    DOWNLOAD_PATH = get_download_path()
    current_id = get_last_id_downloaded()
    last_id = get_last_id()
    if (sub_files := os.listdir(DOWNLOAD_PATH)) != []:
        number_subfile = int(nat.natsorted(sub_files)[-1].split('#')[-1])
    else:
        os.mkdir(f'{DOWNLOAD_PATH}\\Pack #1')
        number_subfile: int = 1
    while current_id <= last_id:
        img_key = get_key_image(current_id)
        download_image(img_key)
        if current_id == last_id:
            new_last_id = get_last_id()
            if new_last_id > last_id:
                last_id = new_last_id
            else:
                winsound.MessageBeep()
                print(
                    'All images are downloaded, you can close the console and relaunch it tomorrow')
        current_id += 1
        if current_id % 50000 == 0:
            number_subfile += 1
            os.mkdir(f'{DOWNLOAD_PATH}\\Pack #{number_subfile}')
input()
