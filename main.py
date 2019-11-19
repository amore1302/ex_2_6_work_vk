import requests
from dotenv import load_dotenv
import os
import random

def remove_local_file(name_file):
    if os.path.isfile(name_file):
        os.remove(name_file)
    else:
        print("Error: %s file not found" % name_file)


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
    response = requests.get(host_api)
    response.raise_for_status()
    info_number_xkcd = response.json()
    url_xkcd = info_number_xkcd["img"]
    comment_xkcd = info_number_xkcd["alt"]
    _, file_extension = os.path.splitext(url_xkcd)
    name_file_xkcd = "_file_{0}{1}".format(number_xkcd, file_extension)
    load_image_from_url_to_file(url_xkcd, name_file_xkcd)
    return {"name": name_file_xkcd, "comment": comment_xkcd}


def get_address_for_load_photo():
    host = "https://api.vk.com/method/photos.getWallUploadServer"
    payload = {"access_token": access_token,
               "group_id": group_id,
               "v": "5.103"
               }
    response = requests.get(host, params=payload)
    if response.text.find("upload_url")  <= 0 :
        return None
    return response.json()["response"]["upload_url"]

def  photo_to_server_vk( https_address_for_load_photo, name_file):
    with open(name_file, 'rb') as file:
        url = https_address_for_load_photo
        files = {
            'photo': file,
        }
        response = requests.post(url, files=files)

    if response.text.find("photo")  <= 0 :
        return None
    return response.json()

def    photo_to_wall(vk_server, vk_photo, vk_hash, comment_xkcd):
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

    if response.text.find("response")  <= 0 :
        return None
    return response.json()

def    photo_to_post_wall(post_owner_id, id_attachments ):
    host = "https://api.vk.com/method/wall.post"
    payload = {"access_token": access_token,
               "owner_id": post_owner_id,
               "friends_only": "0",
               "from_group": "0",
               "attachments": id_attachments,
               "v": "5.103"
               }
    response = requests.get(host, params=payload)
    return "Ok"

def load__photo_to_server_vk( name_file, comment_xkcd):
    https_address_for_load_photo = get_address_for_load_photo()
    if https_address_for_load_photo == None:
        print("ОШИБКА Vk не вернул правильный адрес для загрузки фото Все Остановили")
        return None

    vk_answer = photo_to_server_vk( https_address_for_load_photo, name_file)
    if vk_answer == None:
        print("ОШИБКА Vk не смог выгрузить картинку на сервер Vk Остановили")
        return None

    vk_server = vk_answer["server"]
    vk_photo  = vk_answer["photo"]
    vk_hash   = vk_answer["hash"]

    vk_save_wall_photo = photo_to_wall(vk_server, vk_photo, vk_hash, comment_xkcd)
    if vk_save_wall_photo == None:
        print("ОШИБКА Не смогли  Загрузить файл-картинку на стену Vk.   Все Остановили")
        return None

    vk_save_wall_photo_response = vk_save_wall_photo["response"][0]
    id_photo = vk_save_wall_photo_response["id"]
    id_owner = vk_save_wall_photo_response["owner_id"]
    id_attachments = "photo{0}_{1}".format(id_owner, id_photo)
    post_owner_id = "-{0}".format(group_id)

    vk_photo_to_post_wall = photo_to_post_wall(post_owner_id, id_attachments )
    if vk_photo_to_post_wall == None:
        print("ОШИБКА Не смогли  hfpvtcnbnm gjcn на стенt Vk.   Все Остановили")
        return None
    return "Ok"


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



    answer_load_photo = load__photo_to_server_vk(name_file, comment_xkcd)
    if answer_load_photo  == None:
        print("Не смогли выгрузить Комикс в VK  ")
        remove_local_file(name_file)
        return

    remove_local_file(name_file)


if __name__ == '__main__':
    load_dotenv()
    client_id = os.getenv("CLIENT_ID")
    group_id = os.getenv("GROUP_ID")
    access_token = os.getenv("ACCESS_TOKEN")
    main()