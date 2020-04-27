"""
Поиск файла для NovatorWeb
Программа работает в режиме мультипоточности. 
Задается корневой каталог, в котором каждой найденной папке/файлу
присваивается свой поток для обработки.

На i7-8550u 1.8Ghz, SSD время исполнения занимает 7.7-12с. (8.4 среднее)

Использование:

cmd: python search.py -name %filename% -all(опционально)

-name: имя файла для поиска. Использование расширения обязательно, если требуется конкретный файл.

-all: поиск всех файлов с заданным именем, независимо от его расширения.

"""

import os
from time import time, sleep
from multiprocessing import Pool, cpu_count
import argparse


def search_for_file(start_dir, name, all_ext=None):
	"""
	Главная функция, отвечающая за поиск файла

	Параметры
	___________

	start_dir : str
		Путь для поиска

	name : str
		Имя файла
	___________

	"""
	try:
		# если имя содержится в начальном каталоге, то сразу возвращаем его
		if all_ext:
			if name.split(".")[0] == start_dir[3:].split(".")[0]:
				return [f"Путь к файлу: {start_dir}. Полное имя файла: {os.path.basename(start_dir)}"]
		else:
			if name == start_dir[3:]:
				return [f"Путь к файлу: {start_dir}. Полное имя файла: {os.path.basename(start_dir)}"]

		matched = []
		# проходимся по каталогу в поисках файла
		for root, _, files in os.walk(start_dir): 
			# для каждого элемента в списке делаем проверки
			for element in files:
				# если найденный файл соответсвует, добавляем в список
				if all_ext:
					if name.split(".")[0] == element.split(".")[0]:
						matched += [f"Путь к файлу: {root}. Полное имя файла: {element}"]
				else:
					if name == element:
						matched += [f"Путь к файлу: {root}. Полное имя файла: {element}"]
		return matched
	except KeyboardInterrupt:
		return


def set_thread_param(filename, all_ext=None):
	"""
	Установка аргументов для потока

	Параметры
	___________

	filename : str
		Название файла для поиска

	___________

	"""
	thread_params = []
	start_dir = "C:\\"
	thread_params = []
	max_dirs = cpu_count() * 2

	# находим файлы + папки в корневом каталоге
	for path in os.listdir(start_dir):
		full_path = os.path.join(start_dir, path)
		thread_params.append(tuple([full_path, filename, all_ext]))

	# Если кол-во ядер на процессоре позволяет, проходимся по подпапкам.
	while thread_params and len(thread_params) < max_dirs:
		new_dir = thread_params[0][0]
		for path in os.listdir(new_dir):
			full_path = os.path.join(new_dir, path)
			thread_params.append(tuple([full_path, filename, all_ext]))

	return thread_params


def pooling(function, thread_params):
	"""
	Функция, раздающая потокам функции и агрументы

	Параметры
	___________

	function : str
		Функция для потока

	thread_params : str
		Параметры для потока - начальный каталог для поиска, имя для поиска
	___________
	"""
	with Pool(cpu_count()) as pool:
		try:
			return_object = pool.starmap_async(function, thread_params)
			res = return_object.get(9999) # забираем информацию из объекта с таймаутом для функции
		except KeyboardInterrupt:
			print('KeyboardInterrupt, terminating search')
			return
	return res


def main():
	""" 
	Главная функция, отвечающая за ввод/вывод данных
	"""
	argparser = argparse.ArgumentParser(add_help=True)
	argparser.add_argument("-name", type=str, help="Filename to search")
	argparser.add_argument("-all", action="store_true", help="Use if you want to find all\
							files regardless of the file extension")
	args = argparser.parse_args()
	file_name = args.name
	all_ext = args.all
	total_matches = 0
	# если юзер ввел имя без расширения по дефолту ищем все файлы
	if len(file_name.split(".")) < 2:
		all_ext = True
	start_time = time() # для статистики
	result = []
	# Собираем со всех потоков данные в список
	result = pooling(search_for_file, set_thread_param(file_name, all_ext))
	stop_time = time()

	# Выводим все пути к найденным файлам + счёт
	for match in result: 
		if match is not None and len(match) > 0:
			for root in match:
				print(root)
				total_matches += 1

	print(f"По запросу {file_name} было найдено {total_matches} файла(ов)")
	print(f"Поиск занял {stop_time - start_time} секунд(ы)")
	input("Нажмите ENTER, чтобы выйти")


if __name__ == '__main__':
	main()
