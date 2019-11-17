import requests
from dotenv import load_dotenv
import os
import random


def load_image_from_url_to_file(url_internet, full_file_name):
    response = requests.get(url_internet, verify=False)
    response.raise_for_status()

    with open(full_file_name, 'wb') as file:
        file.write(response.content)


def get_numbers_xkcd():
    host_api = "https://xkcd.com/info.0.json"
    response = requests.get(host_api)
    response.raise_for_status()
    return response.json()["num"]


def get_xkcd_to_file(number_xkcd):
    host_api = "https://xkcd.com/{0}/info.0.json".format(number_xkcd)
    # print(host_api)
    response = requests.get(host_api)
    response.raise_for_status()
    info_number_xkcd = response.json()
    # print(info_number_xkcd)
    url_xkcd = info_number_xkcd["img"]
    comment_xkcd = info_number_xkcd["alt"]
    _, file_extension = os.path.splitext(url_xkcd)
    name_file_xkcd = "_file_{0}{1}".format(number_xkcd, file_extension)
    load_image_from_url_to_file(url_xkcd, name_file_xkcd)
    return {"name": name_file_xkcd, "comment": comment_xkcd}


def get_addres_for_load_pfoto():
    host = "https://api.vk.com/method/photos.getWallUploadServer"
    payload = {"access_token": access_token,
               "group_id": group_id,
               "v": "5.103"
               }
    response = requests.get(host, params=payload)
    return response.json()["response"]["upload_url"]


def load__pfoto_to_server_vk(https_addres_for_load_pfoto, name_file, comment_xkcd):
    with open(name_file, 'rb') as file:
        url = https_addres_for_load_pfoto
        files = {
            'photo': file,
        }
        response = requests.post(url, files=files)
        response.raise_for_status()
    vk_server = response.json()["server"]
    vk_photo = response.json()["photo"]
    vk_hash = response.json()["hash"]

    host = "https://api.vk.com/method/photos.saveWallPhoto"
    payload = {"access_token": access_token,
               "group_id": group_id,
               "photo": vk_photo,
               "server": vk_server,
               "hash": vk_hash,
               "caption": comment_xkcd,
               "v": "5.103"
               }
    response = requests.post(host, params=payload)
    rez = response.json()
    id_photo = response.json()["response"][0]["id"]
    id_owner = response.json()["response"][0]["owner_id"]
    id_attachments = "photo{0}_{1}".format(id_owner, id_photo)
    post_owner_id = "-{0}".format(group_id)
    host = "https://api.vk.com/method/wall.post"
    payload = {"access_token": access_token,
               "owner_id": post_owner_id,
               "friends_only": "0",
               "from_group": "0",
               "attachments": id_attachments,
               "v": "5.103"
               }
    response = requests.get(host, params=payload)
    rez = response.json()


def main():
    try:
        numbers_xkcd = get_numbers_xkcd()
    except requests.exceptions.HTTPError as error:
        exit("Не смогли узнать максимальное число комиксов с сервиса xkcd.com  \n{0}".format(error))
    if numbers_xkcd <= 0:
        print("Непонятная ошибка не смогли вычислить сколько комиксов !!!")
        return

    number_xkcd = random.randint(1, numbers_xkcd)
    try:
        current_xkcd = get_xkcd_to_file(number_xkcd)
    except requests.exceptions.HTTPError as error:
        exit("Не смогли получить данных о комиксе с сервиса xkcd.com \n{0}".format(error))
    name_file = current_xkcd["name"]
    comment_xkcd = current_xkcd["comment"]

    try:
        https_addres_for_load_pfoto = get_addres_for_load_pfoto()
    except requests.exceptions.HTTPError as error:
        exit("Не смогли получить адрес сервера phttps://api.vk.com/method/photos.getWallUploadServer  :\n{0}".format(
            error))

    try:
        load__pfoto_to_server_vk(https_addres_for_load_pfoto, name_file, comment_xkcd)
    except requests.exceptions.HTTPError as error:
        exit("Не смогли выгрузить Комикс в VK  :\n{0}".format(error))

    if os.path.isfile(name_file):
        os.remove(name_file)
    else:  ## Show an error ##
        print("Error: %s file not found" % name_file)


if __name__ == '__main__':
    load_dotenv()
    client_id = os.getenv("CLIENT_ID")
    group_id = os.getenv("GROUP_ID")
    access_token = os.getenv("ACCESS_TOKEN")
    main()