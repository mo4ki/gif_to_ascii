
# gif to ascii
Скрипт, что преобразует **GIF** в **ASCII** анимацию. 
## Важное уточнение:
- На 81ой строке можно выбрать **FPS** для вашей анимации. Я оставил 22.
- Большая часть кода тут была сгенерирована через ИИ. 
- Большую часть кода я тут не понимаю
- Выкладываю для таких же бедолаг, как и я, что не смогли найти простого рабочего скрипта для генерации json файла с кадрами

Просто анимация в консоль
```
python main.py ./gifs/giphy.gif
```

Сохранение кадров в json
```
python main.py ./gifs/giphy.gif --save Sss.json
```
