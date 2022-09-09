import requests
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired, URL, Length
#import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


'''class add_form(FlaskForm):
    title = StringField(label="TITTLE",
                        validators=[DataRequired(), Length(max=25, min=3, message="Enter the correct title")])
    year = IntegerField(label="YEAR", validators=[DataRequired()])
    description = StringField(label="DESCRIPTION", validators=[DataRequired(), Length(max=100, min=15, message="Enter the description (lrngthshoud mr greate than 15)")])
    rating = IntegerField(label="RATING", validators=[DataRequired()])
    ranking = IntegerField(label="RANKING", validators=[DataRequired()])
    review = StringField(label="REVIEW", validators=[DataRequired(), Length(max=100, min=3, message="Enter the review")])
    img_url = StringField(label="IMG URL", validators=[DataRequired(), URL()])
    submit = SubmitField(label="Submit")'''


class Rate_(FlaskForm):
    rating = IntegerField(label="RATING (out off 10)", validators=[DataRequired()])
    review = StringField(label="REVIEW",
                         validators=[DataRequired(), Length(max=100, min=3, message="Enter the review")])
    submit = SubmitField(label="Submit")

#database creation if exist do nothing
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), nullable=False)
db.create_all()


@app.route("/",methods=["GET", "POST"])
def home():
    #fetch data from database table
    all_movies = Movie.query.order_by(Movie.rating).all()
    for i in range(len(all_movies)):
        # This line gives each movie a new ranking reversed from their order in all_movies
        all_movies[i].ranking = len(all_movies) - i
    all_movies = Movie.query.order_by(Movie.ranking).all()
    db.session.commit()
    return render_template("index.html", movies=all_movies)



'''@app.route("/add,", methods=["GET", "POST"])
def add():
    form = add_form()
    return render_template("add.html", form=form)
'''

@app.route("/edit", methods=["GET", "POST"])
def update():
    form = Rate_()
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    if form.validate_on_submit():
        movie.rating = float(form.rating.data)
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", movie=movie, form=form)





@app.route("/delete", methods=["GET", "POST"])
def delete():
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for('home'))


class FindMovieForm(FlaskForm):
    title = StringField(label="TITTLE",validators=[DataRequired(), Length(max=25, min=3, message="Enter the correct title")])
    submit = SubmitField(label="Submit")


@app.route("/add", methods=["GET", "POST"])
def add_movie():
    #form = FindMovieForm()
    #create like this also
    #url="https://api.themoviedb.org/3/search/movie?api_key=<<api key>>&language=en-US&query=<<movie title>>&page=1&include_adult=false
    #api key and url
    MOVIE_DB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
    MOVIE_DB_API_KEY="8b6cbe8a792dbdca39649d8a9f50246d"
    form = FindMovieForm()

    if form.validate_on_submit():
        movie_title = form.title.data
        response = requests.get(MOVIE_DB_SEARCH_URL, params={"api_key": MOVIE_DB_API_KEY, "query": movie_title})
        data = response.json()["results"]
        return render_template("select.html", options=data)
    return render_template("add.html", form=form)




@app.route("/sucess",methods=["GET","POST"])
def add_item():
    movie_id_api = request.args.get("id")
    MOVIE_DB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"
    MOVIE_DB_INFO_URL = "https://api.themoviedb.org/3/movie"
    movie_api_url = f"{MOVIE_DB_INFO_URL}/{movie_id_api}"
    MOVIE_DB_API_KEY = "8b6cbe8a792dbdca39649d8a9f50246d"
    reponse=requests.get(url=movie_api_url,params={"api_key": MOVIE_DB_API_KEY})
    data=reponse.json()

    new_entry=Movie(title=data["title"],year=data["release_date"].split("-")[0],img_url=f"{MOVIE_DB_IMAGE_URL}{data['poster_path']}",description=data["overview"] )
    db.session.add(new_entry)
    db.session.commit()
    return redirect(url_for("update",id=new_entry.id))


if __name__ == '__main__':
    app.run(debug=True,port=1245)
