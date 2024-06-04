Проект YaMDb собирает отзывы пользователей на различные произведения. Произведения делятся на категории, такие как «Книги», «Фильмы», «Музыка».
Пользователи оставляют к произведениям текстовые отзывы и ставят произведению оценку; из пользовательских оценок формируется усреднённая оценка произведения.
Чтобы клонировать репозиторий воспользейтесь командой в терминале (команды описаны для Windows):
git clone https://github.com/ElenaZalomlenkova/api_final_yatube.git
Для перехода в проект:
cd api_final_yatube
Cоздать и активировать виртуальное окружение:
python -m venv venv
source venv/Scripts/activate
Установить зависимости из файла requirements.txt:
python -m pip install --upgrade pip 
pip install -r requirements.txt
Выполнить миграции:
python manage.py migrate
Запуск проекта:
python3 manage.py runserver
