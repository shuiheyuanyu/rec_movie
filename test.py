from flask_main import *
from flask_main import Movies

movie_id = 32
movies = Movies.query.filter(Movies.id == movie_id).first()
movie_hai =movies.url
print(movie_hai)
