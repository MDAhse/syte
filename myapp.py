# устанавливаю всякие приколы
from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import func
from flask_sqlalchemy import SQLAlchemy
import sqlite3

# список моих великих вопросов про жаб и ежей
list_of_questions = [
    ("Вы любите жаб?",),
    ("Вы любите ежей?",),
    ("Хотели бы Вы иметь дома жабу",),
    ("Хотели бы Вы иметь дома ежа?",),
    ("Кого вы любите больше (меньше не любите?)",),
    ("Ваше любимое животное?",),
    ("Какое идеальное имя для жабы?",),
    ("Какое идеальное имя для ежа?",),
    ("Ваши отзывы/вопросы/предложения",),
]


db = sqlite3.connect(
    r"/Users/dariamorozova/myproject/myproj/zhabiezhi.db"
)  # автоматически оно кидало базу данных в какой-то другой уголок компа, поэтому пришлось указать точный путь

cur = db.cursor()
cur.execute(
    """CREATE TABLE IF NOT EXISTS answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    q1 INTEGER,
    q2 INTEGER,
    q3 INTEGER,
    q4 INTEGER,
    q5 INTEGER,
    q6 TEXT,
    q7 TEXT,
    q8 TEXT,
    q9 TEXT)
    """
)

cur.execute(
    """CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT
    )"""
)

cur.execute(
    """CREATE TABLE IF NOT EXISTS  
    user ( 
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    gender TEXT,
    hometown TEXT,
    age INTEGER )"""
)

for smth in list_of_questions:
    a = smth
    cur.execute("""INSERT into questions (text) VALUES (?) """, a)
# будем удалять вопросы чтобы они не добавлялись при каждом запуске
cur.execute("""DELETE FROM questions WHERE id>9""")
db.commit()


app = Flask(__name__)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///zhabiezhi.db"
db1 = SQLAlchemy(app)


class User(db1.Model):
    __tablename__ = "user"
    id = db1.Column(db1.Integer, primary_key=True)
    gender = db1.Column(db1.Text)
    hometown = db1.Column(db1.Text)
    age = db1.Column(db1.Integer)


class Questions(db1.Model):
    __tablename__ = "questions"
    id = db1.Column(db1.Integer, primary_key=True)
    text = db1.Column(db1.Text)


class Answers(db1.Model):
    __tablename__ = "answers"
    id = db1.Column(db1.Integer, primary_key=True)
    q1 = db1.Column(db1.Integer)
    q2 = db1.Column(db1.Integer)
    q3 = db1.Column(db1.Integer)
    q4 = db1.Column(db1.Integer)
    q5 = db1.Column(db1.Integer)
    q6 = db1.Column(db1.Text)
    q7 = db1.Column(db1.Text)
    q8 = db1.Column(db1.Text)
    q9 = db1.Column(db1.Text)


# запишем приветственный текст
@app.route("/")
def base():
    with open("text.txt", "r", encoding="utf-8") as f:
        content = f.read().split("\n")
    return render_template("base.html", content=content)


@app.route("/questions")
def question_page():
    questions = Questions.query.all()[:-5]
    return render_template("questions.html", questions=questions)


@app.route("/process", methods=["get"])
def answer_process():
    # если нет ответов, то отсылаем решать анкету
    if not request.args:
        return redirect(url_for("question_page"))

    # достаем параметры
    gender = request.args.get("gender")
    hometown = request.args.get("hometown")
    age = request.args.get("age")

    # создаем профиль пользователя
    user = User(age=age, gender=gender, hometown=hometown)
    # добавляем в базу
    db1.session.add(user)
    # сохраняемся
    db1.session.commit()
    # получаем юзера с айди (автоинкремент)
    db1.session.refresh(user)

    # получаем два ответа
    q1 = request.args.get("q1")
    q2 = request.args.get("q2")
    q3 = request.args.get("q3")
    q4 = request.args.get("q4")
    q5 = request.args.get("q5")
    q6 = request.args.get("q6")
    q7 = request.args.get("q7")
    q8 = request.args.get("q8")
    q9 = request.args.get("q9")

    # привязываем к пользователю (см. модели в проекте)
    answer = Answers(
        id=user.id, q1=q1, q2=q2, q3=q3, q4=q4, q5=q5, q6=q6, q7=q7, q8=q9, q9=q9
    )
    # добавляем ответ в базу
    db1.session.add(answer)
    # сохраняемся
    db1.session.commit()

    return "Спасибо! Можете посмотреть статистику ответов в разделе статистика."


@app.route("/stats")
def stats():
    all_info = {}
    age_stats = db1.session.query(
        func.avg(User.age), func.min(User.age), func.max(User.age)
    ).one()
    all_info["age_average"] = age_stats[0]
    all_info["age_min"] = age_stats[1]
    all_info["age_max"] = age_stats[2]
    all_info["total_count"] = User.query.count()
    all_info["q1_mean"] = db1.session.query(func.avg(Answers.q1)).one()[0]
    all_info["q2_mean"] = db1.session.query(func.avg(Answers.q2)).one()[0]
    all_info["q3_mean"] = db1.session.query(func.avg(Answers.q3)).one()[0]
    all_info["q4_mean"] = db1.session.query(func.avg(Answers.q4)).one()[0]
    all_info["q5_mean"] = db1.session.query(func.avg(Answers.q4)).one()[0]

    # здесь посмотрим на то, к чему больше склонны люди: кого любить, кого не любить, кого заводить
    if round(all_info["q1_mean"], 0) == 1:
        content1 = "скорее да"
    elif round(all_info["q1_mean"], 0) == 2:
        content1 = "скорее нет"
    if round(all_info["q2_mean"], 0) == 1:
        content2 = "скорее да"
    elif round(all_info["q2_mean"], 0) == 2:
        content2 = "скорее нет"
    if round(all_info["q3_mean"], 0) == 1:
        content3 = "скорее да"
    elif round(all_info["q3_mean"], 0) == 2:
        content3 = "скорее нет"
    if round(all_info["q4_mean"], 0) == 1:
        content4 = "скорее да"
    elif round(all_info["q4_mean"], 0) == 2:
        content4 = "скорее нет"
    if round(all_info["q5_mean"], 0) == 1:
        content5 = "ЕЖИ"
    elif round(all_info["q5_mean"], 0) == 2:
        content5 = "ЖАБЫ"
    return render_template(
        "results.html",
        all_info=all_info,
        content1=content1,
        content2=content2,
        content3=content3,
        content4=content4,
        content5=content5,
    )


if __name__ == "__main__":
    app.run()

cur.close()
