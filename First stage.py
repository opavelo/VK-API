from pprint import pprint
import requests
import json
import cv2
import time

class YaUploader:
    def __init__(self, id_vk, token_yd, token_vk):
        self.id_vk = id_vk
        self.token_yd = token_yd
        self.token_vk = token_vk
        self.photo_id = []
        self.photo_url = []
        self.photo_likes = []
        self.photo_date = []
        self.photos_to_upload = []
        self.yd_file_list = []
        self.file_path = ''
        self.photo_counter = 0

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token_yd)
        }

    def vk_linklikes_loader(self):   #функция заполнения словаря {photo_id : [date, likes, url]}
        url = 'https://api.vk.com/method/photos.get'
        params = {'user_id': self.id_vk,
                  'access_token': self.token_vk,
                  'v': '5.130',
                  'extended': 1,
                  'album_id' : 'wall'       #wall, saved, profile
                  }
        response = requests.get(url, params=params)
        #print(response.json())
        if response.status_code == 200:
            print('Запрос на получение фотографий прошел успешно')
            # Запускаем функцию обработки json файла для извлечения информации
            self.photo_counter = len(response.json()['response']['items'])
            for i in range(self.photo_counter):  # почему-то максимум 50 фото в json()
                self.photo_id.append(response.json()['response']['items'][i]['id'])
                self.photo_url.append(response.json()['response']['items'][i]['sizes'][-1]['url'])
                self.photo_date.append(response.json()['response']['items'][i]['date'])
                self.photo_likes.append(response.json()['response']['items'][i]['likes']['count'] + \
                        response.json()['response']['items'][i]['likes']['user_likes'])
        else:
            print('Ошибка:', response)
        #pprint(self.photo_date)

    def upload_to_yddisk_from_url(self, file_path, photo_url):
        upload_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        headers = self.get_headers()
        params = {'path': file_path,
                  'url': photo_url ,
                  'overwrite': 'false'
                   }
        response = requests.post(upload_url, headers=headers, params=params)
        response.raise_for_status()
        #print(response.json())
        time.sleep(1)
        if response.status_code == 202:
            print(f'Загрузка фото {file_path} выполнено успешно')

    # функция проверки совпадений в названиях списка на загрузку и в названиях файлов на Яндекс Диске
    def preparing_to_upload(self, requested_quantity):    # кол-во фото для загрузки
        yd.yd_folder_create()       # Создаем папку с id пользователем, если она еще не создана
        yd.checking_avaliability()  # Создаем словарь с именами загруженных на Яндекс Диск файлов
        for i in range(requested_quantity):
            if requested_quantity <= self.photo_counter:    # проверка на доступное кол-во фото
                self.photos_to_upload.append(self.photo_likes[i])  # вспомогательный список фото для загрузки для дальнейшей проверки на совпадения
            else:
                print('В альбоме Вконтакте меньше фото, чем запрошено загрузить на яндекс-диск')
                break
        #print(self.photos_to_upload)
        for count_i, i in enumerate(self.photos_to_upload):
            for count_j, j in enumerate(self.photos_to_upload):
                if i==j:
                    if count_j != count_i:
                        self.photos_to_upload[count_i] = str(self.photos_to_upload[count_i]) + '_' + str(self.photo_date[count_i])
                           #проверяем что на Яндекс диске уже что-то загружено
        #print(self.photos_to_upload)
        #print(self.yd_file_list)
        for count_i, i in enumerate(self.photos_to_upload):
            #print(i)
            for count_k, k in enumerate(self.yd_file_list):
                #print(k)
                if str(i)==str(k):
                    self.photos_to_upload[count_i] = str(self.photos_to_upload[count_i]) + '_' + str(self.photo_date[count_i])
            yd.upload_to_yddisk_from_url(f'{self.file_path}/{self.photos_to_upload[count_i]}', self.photo_url[count_i])
        #print(self.photos_to_upload)

    # создание папки и списка файлов внутри
    def yd_folder_create(self):
        self.file_path = 'VK/' + str(self.id_vk)   #создаем папку с фотографиями, название = id пользователя
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = self.get_headers()
        params = {
            'path': self.file_path
        }
        response = requests.put(url, headers=headers, params=params)
        if response.status_code == 201:
            print(f'Папка {self.file_path} создана')
        elif response.status_code == 409:
            print(f'Папка {self.file_path} уже была создана')
            # Если папка уже создана получаем имена файлов из этой папки
        else:
            print('Ошибка', response)

    # Проверка что записано на яндекс диске
    def checking_avaliability(self):
        upload_url = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = self.get_headers()
        params = {'path': self.file_path}
        response = requests.get(upload_url, headers=headers, params=params)
        for i in range(0, len(response.json()['_embedded']['items'])):
            self.yd_file_list.append(response.json()['_embedded']['items'][i]['name'])
        print(f'Список файлов в папке {self.file_path}', self.yd_file_list)

yd = YaUploader('1126679', 'токен яндекс диск', 'токен ВК')

yd.vk_linklikes_loader()

yd.preparing_to_upload(5)       # аргумент = кол-во фото для загрузки

#1126679 мой id
#4262878 ромин
#552934290 Афанасич