
import os
import string
import random
from calculator import Calculator
from flask import Flask, render_template, request, send_file, flash, session, redirect
from texts import Russian, English


app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(12).hex()
calc = Calculator()


@app.route("/", methods=["POST", "GET"])
def index():
    remove_old_files()
    if len(session) == 0:
        session["texts"] = Russian
        session["language"] = "ru"
        save_data(session)
        session["OUT_FILE"] = Russian["default_filename"]

    if request.method == "POST":
        calc.set_args(request.form.get("i"),
                      request.form.get("dsh"),
                      request.form.get("Rout"),
                      request.form.get("D"),
                      request.form.get("RESOLUTION"),
                      request.form.get("BASE_WHEEL_SHAPE"),
                      request.form.get("ECCENTRIC"),
                      request.form.get("SEPARATOR"),
                      request.form.get("BALLS"),
                      request.form.get("OUT_DIAMETER"))

        calc.generate()
        send_error()
        save_data(session)
        session["OUT_FILE"] = request.form.get("OUT_FILE")  # имя файла, которое задал пользователь

    return render_template("hello.html",
                           i=session.get("i"),
                           dsh=session.get("dsh"),
                           Rout=session.get("Rout"),
                           D=session.get("D"),
                           RESOLUTION=session.get("RESOLUTION"),
                           BASE_WHEEL_SHAPE=session.get("BASE_WHEEL_SHAPE"),
                           ECCENTRIC=session.get("ECCENTRIC"),
                           SEPARATOR=session.get("SEPARATOR"),
                           BALLS=session.get("BALLS"),
                           OUT_DIAMETER=session.get("OUT_DIAMETER"),
                           OUT_FILE=session.get("OUT_FILE"),
                           parameters_string=session.get("parameters_string"),
                           texts=session.get("texts"),
                           language=session.get("language"))


@app.route("/license")
def license():
    return render_template("license.html")


@app.route("/about")
def about():
    return render_template("about.html", texts=session.get("texts"))


@app.route("/download_dxf")
def download_dxf():
    if not calc.generated:
        flash(session["texts"]["no_generated_error"], category="error")
        return redirect("/")
    if calc.get_error("ru"):    # любой язык можно передать, просто чекаем наличие ошибки
        return redirect("/")
    server_filename = "".join(random.choices(string.ascii_lowercase, k=10))  # я подумал, что если на сайте будет одновременно несколько пользователей, и они будут создавать файлы с одинаковым (дефолтным) именем, то это приведёт к ошибкам, поэтому каждый файл имеет рандомное название на сервере. Поэтому я задаю рандомное название каждомау файлу. Однако при скачивании ему всё равно присваивается имя, которое написал пользователь.
    OUT_FILE = session["OUT_FILE"] + session["texts"]["end_filename_dxf"]
    calc.save_dxf(server_filename)   # передаём имя файла БЕЗ расширения
    return send_file(server_filename + ".dxf", download_name=OUT_FILE + ".dxf", as_attachment=True)


@app.route("/download_txt")
def download_txt():
    if not calc.generated:
        flash(session["texts"]["no_generated_error"], category="error")
        return redirect("/")
    if calc.get_error("ru"):  # любой язык можно передать, просто чекаем наличие ошибки
        return redirect("/")
    server_filename = "".join(random.choices(string.ascii_lowercase, k=10))  # я подумал, что если на сайте будет одновременно несколько пользователей, и они будут создавать файлы с одинаковым (дефолтным) именем, то это приведёт к ошибкам, поэтому каждый файл имеет рандомное название на сервере. Поэтому я задаю рандомное название каждомау файлу. Однако при скачивании ему всё равно присваивается имя, которое написал пользователь.
    OUT_FILE = session["OUT_FILE"] + session["texts"]["end_filename_txt"]
    calc.save_txt(server_filename, session["language"])  # передаём имя файла БЕЗ расширения
    return send_file(server_filename + ".txt", download_name=OUT_FILE + ".txt", as_attachment=True)


@app.route("/ru_btn")
def ru_btn():
    session["texts"] = Russian
    session["language"] = "ru"
    session["OUT_FILE"] = Russian["default_filename"]
    return redirect("/")


@app.route("/en_btn")
def en_btn():
    session["texts"] = English
    session["language"] = "en"
    session["OUT_FILE"] = English["default_filename"]
    return redirect("/")


def save_data(session):
    session["i"] = str(calc.i)
    session["dsh"] = str(calc.dsh)
    session["Rout"] = str(calc.Rout)
    session["D"] = str(calc.D)
    session["RESOLUTION"] = str(calc.RESOLUTION)
    session["BASE_WHEEL_SHAPE"] = bool(calc.BASE_WHEEL_SHAPE)
    session["ECCENTRIC"] = bool(calc.ECCENTRIC)
    session["SEPARATOR"] = bool(calc.SEPARATOR)
    session["BALLS"] = bool(calc.BALLS)
    session["OUT_DIAMETER"] = bool(calc.OUT_DIAMETER)
    session["parameters_string"] = calc.get_parameters_string(session["language"])


def send_error():
    error = calc.get_error(session["language"])
    if error:
        flash(error, category="error")
    else:
        flash(session["texts"]["no_errors_message"], category="success")


def remove_old_files():
    for file in os.listdir():
        if file[-4:] in (".dxf", ".txt"):
            os.remove(file)


# для запуска кода на локальном сервере (обычном компьютере), раскомментрируйте следующие строки:
if __name__ == "__main__":
    app.run(debug=True)
