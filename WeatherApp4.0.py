import json
import logging
import random
import tkinter as tk
import requests
import PIL.Image
import PIL.ImageTk
import geocoder
from tkinter import *

# Laden der Config und setzen des API-Keys
with open('config/config.json', 'r') as f:
    config = json.load(f)

api_key = config['API_KEY']

# Anlegen der Loggerdatei
logging.basicConfig(filename='log/weather_app.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s', datefmt='%d.%m.%y %H:%M:%S')


# Ruft die Location des Users ab und gibt Breitengrad(Latitude) und Längengrad(Longitude) zurück
def get_user_location():
    try:
        response = requests.get('https://ipinfo.io')
        data = response.json()
        city = data.get('city', 'Unknown')
        return city
    except Exception as e:
        print(f"Error retrieving location: {e}")
        return "Unknown"


# globale Variable um Wetter-Bild zu vergleichen um identische Bilder auf beiden Frames zu vermeiden
global left_weather_image_path

# Erstellt den Pfad des Bildes inkl. einer Zufallszahl von 1 bis 3
def get_weather_img(weather):
    img_format = ".jpg"  # png oder jpg
    img_path = "img/"
    allowed_weather = ["Clear", "Rain", "Snow", "Thunderstorm", "Clouds"]
    random_int_as_string = str(random.randint(1, 3))
    if weather in allowed_weather:
        return img_path + weather.lower() + random_int_as_string + img_format
    else:
        return img_path + "default" + img_format


# Erstellen einer allgemeinen Fehlermeldung, die die Fehlermeldung direkt vom Server holt
def display_error_message(error_code, error_message):
    error_message = f" {error_code}: {error_message} \n\n Error collecting data.\n Please check spelling \n or choose larger city."
    result_label_right.config(text=error_message)
    img = PIL.Image.open("img/default.jpg")
    img = img.resize((200, 200), PIL.Image.LANCZOS)  # Zahlen entsprechend der gewünschten Größe anpassen
    weather_image_label_right.img = PIL.ImageTk.PhotoImage(img)
    weather_image_label_right['image'] = weather_image_label_right.img
    weather_image_label_right.image = img
    city_entry.delete(0, "end")
    city_entry.insert(0, "Enter city")
    city_entry.bind("<Button-1>", temp_text)
    logging.error(error_message + "Requested City: " + city_entry.get())


# Selektiert und formatiert die Daten aus dem JSON und gibt ein Python Dictionary zurück
def select_data(data):
    return_dict = {
        "weather": data["weather"][0]["main"],
        "weather_img": get_weather_img(data["weather"][0]["main"]),
        "temperature": int(data["main"]["temp"]),
        "humidity": data["main"]["humidity"],
        "feels_like_temp": int(data["main"]["feels_like"]),
        "wind_speed": data["wind"]["speed"],
        "temp_min": int(data["main"]["temp_min"]),
        "temp_max": int(data["main"]["temp_max"])
    }
    return return_dict


def show_widget(widget):
    widget.pack()


def hide_widget(widget):
    widget.pack_forget()


def temp_text(e):
    if city_entry.get() == "Enter city":
        city_entry.delete(0, "end")
        city_entry.config(fg="#000000")


def reset():
    result_label_right.config(text="")
    city_entry.delete(0, "end")
    weather_image_label_right.config(image=None)
    weather_image_label_right.image = None
    hide_widget(weather_image_label_right)
    hide_widget(result_label_right)
    city_entry.insert(0, "Enter city")
    city_entry.bind("<Button-1>", temp_text)


# Abruf der Daten von API
def get_weather_data(city):
    base_url = "https://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}q={city},&appid={api_key}&units=metric"
    response = requests.get(complete_url)
    data = response.json()
    if data["cod"] != 200:
        display_error_message(data["cod"], data["message"])
    else:
        return select_data(data)


# Setzt die Inhalte, die dann von tkinter im UI angezeigt werden
def display_weather_right():
    city_name_right = city_entry.get()
    data = get_weather_data(city_name_right)

    # Globale Variable wird eingebunden. While-Schleife verhindert, dass identische Bilder angezeigt werden
    global left_weather_image_path
    while left_weather_image_path == data['weather_img']:
        data['weather_img'] = get_weather_img(data['weather'])

    # Bild laden, Größe anpassen und setzen
    img = PIL.Image.open(data['weather_img'])
    img = img.resize((200, 200), PIL.Image.LANCZOS)  # Zahlen entsprechend der gewünschten Größe anpassen
    weather_image_label_right.img = PIL.ImageTk.PhotoImage(img)
    show_widget(weather_image_label_right)
    show_widget(result_label_right)
    city_entry.delete(0, "end")
    city_entry.insert(0, "Enter city")
    city_entry.bind("<Button-1>", temp_text)

    # Wetterdaten loggen
    logging.info(
        f"Weather for {city_name_right}: {data['weather']}, Temperature: {data['temperature']:.2f}°C, Feels Like: {data['feels_like_temp']:.2f}°C, Humidity: {data['humidity']:.2f}°C,"
        f"Min Temperature: {data['temp_min']:.2f}°C, Max Temperature: {data['temp_max']:.2f}°C, Wind Speed: {data['wind_speed']} m/s")

    # Text für das Wetterlabel
    result_label_right.config(
        text=f"Current weather for: \n{city_name_right}: \n{data['weather']}\nTemperature: {data['temperature']}°C\nMin Temperature: {data['temp_min']}°C\nMax Temperature: {data['temp_max']}°C\nHumidity: {data['humidity']}%\nFeels like: {data['feels_like_temp']}°C\n"
             f"Wind speed: {data['wind_speed']} km/h\n")

    weather_image_label_right['image'] = weather_image_label_right.img
    weather_image_label_right.image = img


def display_weather_left():
    city_name_left = get_user_location()
    data = get_weather_data(city_name_left)

    # Globale Variable wird eingebunden und der Wetterpfad des linken Frames darin gespeichert
    global left_weather_image_path
    left_weather_image_path = data['weather_img']

    # Bild laden, Größe anpassen und setzen
    img = PIL.Image.open(data['weather_img'])
    img = img.resize((200, 200), PIL.Image.LANCZOS)  # Zahlen entsprechend der gewünschten Größe anpassen
    weather_image_label_left.img = PIL.ImageTk.PhotoImage(img)
    show_widget(weather_image_label_left)
    show_widget(result_label_left)


    # Wetterdaten loggen
    logging.info(
        f"Weather for {city_name_left}: {data['weather']}, Temperature: {data['temperature']:.2f}°C, Feels Like: {data['feels_like_temp']:.2f}°C, Humidity: {data['humidity']:.2f}°C,"
        f"Min Temperature: {data['temp_min']:.2f}°C, Max Temperature: {data['temp_max']:.2f}°C, Wind Speed: {data['wind_speed']} m/s")

    # Text für das Wetterlabel
    result_label_left.config(
        text=f"Current weather for: \n{city_name_left}: \n{data['weather']}\nTemperature: {data['temperature']}°C\nMin. Temperature: {data['temp_min']}°C\nMax. Temperature: {data['temp_max']}°C\nHumidity: {data['humidity']}%\nFeels like: {data['feels_like_temp']}°C\n"
             f"Wind speed: {data['wind_speed']} km/h\n")

    weather_image_label_left['image'] = weather_image_label_left.img
    weather_image_label_left.image = img


# GUI erstellen
root = tk.Tk()
root.title("Delta Boson - Weather App")
root.configure(bg="#cce0ea")

#root.wm_attributes("-transparentcolor","black")
#background_image = tk.PhotoImage(file="img/backgroundWeatherApp.png")
#background_label = tk.Label(root, image=background_image, bg="black")
#background_label.place(relwidth=1, relheight=1)

mon_x = root.winfo_screenwidth() / 2 - 350
mon_y = root.winfo_screenheight() / 2 - 400
root.geometry("700x800+%d+%d" % (mon_x, mon_y))  # groesse des Fensters + Position immer center. Verkürzter code
root.resizable(width=False, height=False)  # macht die groesse des Fensters fest. True macht es veraenderbar

# Aufteilung des Fensters in zwei Spalten
top_frame = Frame(root, bg="#cce0ea", height=100)
top_frame.pack(side=tk.TOP, fill=tk.X, pady=30, padx=25)

left_frame = Frame(root, bg="#cce0ea", width=150)
left_frame.pack(side=tk.LEFT, fill=tk.BOTH, pady=0, padx=50)

right_frame = Frame(root, bg="#cce0ea", width=150)
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, pady=0, padx=50)

### Erstellung der tkinter Elemente des rechten Frames ###
# Erstellung des leeren Labels für die rechte Spalte
empty_label_right = tk.Label(right_frame, bg="#cce0ea")  # leeres label aus optischen Gründen
empty_label_right.pack(pady=10)

# Erstellung des Stadt-Labels für die rechte Spalte
city_label_right = tk.Label(right_frame, text="Requested location:", font=("Helvetica", 16), bg="#cce0ea")
city_label_right.pack(pady=5)

# Eingabefeld für die Stadt
city_entry = tk.Entry(top_frame, font=("Helvetica", 20), bg="#ccd1dd", fg="#000000")
city_entry.insert(0, "Enter city")
city_entry.bind("<FocusIn>", temp_text)
clicked = city_entry.bind('<Return>', temp_text)
city_entry.pack(pady=20)

# Button, um das Wetter abzurufen
get_weather_button = Button(top_frame, text="Go!", bg="#ccd1dd", font=("Helvetica", 16), fg="black",
                            command=display_weather_right)
get_weather_button.bind("<Return>")
get_weather_button.pack()

# Bild-Label
weather_image_label_right = tk.Label(right_frame, bg="#cce0ea")
weather_image_label_right.pack(pady=20)

# Label, um das Wetter anzuzeigen
result_label_right = tk.Label(right_frame, text="", font=("Helvetica", 16), bg="#cce0ea", fg="#7c818b")  # 8c919b
result_label_right.pack(pady=10)

### Erstellung der tkinter Elemente des linken Frames ###
# Erstellung des leeren Labels für die linke Spalte
empty_label_left = tk.Label(left_frame, bg="#cce0ea")  # leeres label aus optischen Gründen
empty_label_left.pack(pady=10)

# Erstellung des Stadt-Labels für die linke Spalte
city_label_left = tk.Label(left_frame, text="Your location:", font=("Helvetica", 16), bg="#cce0ea")
city_label_left.pack(pady=5)


# Bild-Label
weather_image_label_left = tk.Label(left_frame, bg="#cce0ea")
weather_image_label_left.pack(pady=20)

# Label, um das Wetter anzuzeigen
result_label_left = tk.Label(left_frame, text="", font=("Helvetica", 16), bg="#cce0ea", fg="#7c818b")  # 8c919b
result_label_left.pack(pady=10)

display_weather_left()

root.mainloop()
