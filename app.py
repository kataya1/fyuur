# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import datetime
# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object("config")
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
Migrate(app, db)
# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#


class Venue(db.Model):
	__tablename__ = "Venue"

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String)
	city = db.Column(db.String(120))
	state = db.Column(db.String(120))
	address = db.Column(db.String(120))
	phone = db.Column(db.String(120))
	image_link = db.Column(db.String(500))
	facebook_link = db.Column(db.String(120))

	# TODO: implement any missing fields, as a database migration using Flask-Migrate
	def __repr__(self):
		return f"<Venue {self.id} {self.name} {self.city} {self.state} {self.address} {self.phone} {self.genres}>"

class Artist(db.Model):
	__tablename__ = "Artist"

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String)
	city = db.Column(db.String(120))
	state = db.Column(db.String(120))
	phone = db.Column(db.String(120))
	# genres = db.Column(db.String(120))
	image_link = db.Column(db.String(500))
	facebook_link = db.Column(db.String(120))

	# TODO: implement any missing fields, as a database migration using Flask-Migrate
	# it seems that this line is unnessesary as it's not detected in migration
	venues = db.relationship("Venue", secondary='show', backref="artists")

	def __repr__(self):
		return f"<Artist {self.id} {self.name} {self.city} {self.state} {self.phone} {self.genres}>"


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
	__tablename__ = "show"

	id = db.Column(db.Integer, primary_key=True)
	start_time = db.Column(db.DateTime, nullable=False)
	artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"), nullable=False)
	venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"), nullable=False)
	artist = db.relationship('Artist', backref="show")
	venue = db.relationship('Venue', backref="show")

	def __repr__(self):
		return f'<Show {self.id} {self.start_time} artist id: {self.artist_id} venue id:{self.venue_id}>'

# Association tables
artist_genre = db.Table(
	"artist_genre",
	db.Column("artist_id", db.Integer, db.ForeignKey("Artist.id"), primary_key=True),
	db.Column("genre_id", db.Integer, db.ForeignKey("genre.id"), primary_key=True),
)

venue_genre = db.Table(
	"venue_genre",
	db.Column("venue_id", db.Integer, db.ForeignKey("Venue.id"), primary_key=True),
	db.Column("genre_id", db.Integer, db.ForeignKey("genre.id"), primary_key=True),
)

# genre table. 1NF wouldnot allow multi argument per column of each row
class Genre(db.Model):
	__tablename__ = "genre"

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String, nullable=False)
	# decided that genre is parent table, as Artist.genres makes more meaning
	artists = db.relationship(
		"Artist", secondary=artist_genre, backref=db.backref("genres", lazy=True), cascade='all'
	)
	venues = db.relationship(
		"Venue", secondary=venue_genre, backref=db.backref("genres", lazy=True), cascade='all'
	)
	def __repr__(self):
		return f'<Genre {self.id}, {self.name} >'

""" # inserting initial values into the genre table by detecting event after creation of table
@db.event.listens_for(Genre.__table__, 'after_create')
def insert_initial_values(*args, **kwargs):
	try:
		db.session.add(Genre(name="Alternative"))
		db.session.add(Genre(name="Blues"))
		db.session.add(Genre(name="Classical"))
		db.session.add(Genre(name="Country"))
		db.session.add(Genre(name="Electronic"))
		db.session.add(Genre(name="Folk"))
		db.session.add(Genre(name="Funk"))
		db.session.add(Genre(name="Hip-Hop"))
		db.session.add(Genre(name="Heavy Metal"))
		db.session.add(Genre(name="Instrumental"))
		db.session.add(Genre(name="Jazz"))
		db.session.add(Genre(name="Musical Theatre"))
		db.session.add(Genre(name="Pop"))
		db.session.add(Genre(name="Punk"))
		db.session.add(Genre(name="R&B"))
		db.session.add(Genre(name="Reggae"))
		db.session.add(Genre(name="Rock n Roll"))
		db.session.add(Genre(name="Soul"))
		db.session.add(Genre(name="Other"))
		db.session.commit()
	except Exception as e:
		print(".\n.\nerror\n\n")
	finally:
		db.session.close()
# **update** can't get it to work will implement it using migation file """

	
# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format="medium"):
	date = dateutil.parser.parse(value)
	if format == "full":
		format = "EEEE MMMM, d, y 'at' h:mma"
	elif format == "medium":
		format = "EE MM, dd, y h:mma"
	return babel.dates.format_datetime(date, format)

def show_response_format(show_list):
	""" {
	"artist_id": 4,
	"artist_name": "Guns N Petals",
	"artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
	"start_time": "2019-05-21T21:30:00.000Z",
	} """
	return [{
	"artist_id": s.artist_id,
	"artist_name": s.artist.name,
	"artist_image_link": s.artist.image_link,
	"start_time": str(s.start_time),
	} for s in show_list]
	
def show_times(entity):
	'retun two arrays. pastshows[], upcomingshows[]'
	past_shows = []
	up_coming_shows = []
	for s in entity.show:
		if s.start_time >= datetime.datetime.now():
			up_coming_shows.append(s)
		else:
			past_shows.append(s)
	
	return (past_shows, up_coming_shows)

app.jinja_env.filters["datetime"] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route("/")
def index():
	return render_template("pages/home.html")


#  Venues
#  ----------------------------------------------------------------

# done
@app.route("/venues")
def venues():
	# TODO: replace with real venues data.
	#       num_shows should be aggregated based on number of upcoming shows per venue.
	try:
		v = db.session.query(Venue).order_by(Venue.state, db.func.lower(Venue.city)).all()
		# data = [{"city": venue.city, "state": venue.state } for i, venue in enumerate(v)]
		
		if v:
			data, venues = [], []
			s, c = v[0].state, v[0].city
			for venue in v:
				if venue.state != s or venue.city != c:
					data.append({"city": c, "state": s, "venues": venues})
					s, c = venue.state, venue.city
					venues = []
				_, up_coming = show_times(venue)
				print(up_coming)
				venues.append({"id": venue.id, "name": venue.name, "num_upcoming_shows": len(up_coming) })	
	except Exception as e:
		print(e)

	
	
	""" data = [
		{
			"city": "San Francisco",
			"state": "CA",
			"venues": [
				{"id": 1, "name": "The Musical Hop", "num_upcoming_shows": 0,},
				{
					"id": 3,
					"name": "Park Square Live Music & Coffee",
					"num_upcoming_shows": 1,
				},
			],
		},
		{
			"city": "New York",
			"state": "NY",
			"venues": [
				{"id": 2, "name": "The Dueling Pianos Bar", "num_upcoming_shows": 0,}
			],
		},
	] """
	return render_template("pages/venues.html", areas=data)

# done
@app.route("/venues/search", methods=["POST"])
def search_venues():
	# TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
	# seach for Hop should return "The Musical Hop".
	# search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
	search = f"%{request.form.get('search_term')}%"
	venues = db.session.query(Venue).filter(Venue.name.ilike(search)).all()
	response = {
		"count": len(venues),
		"data": [{"id": v.id, "name": v.name, "num_upcoming_shows": len(show_times(v)[1]),} for v in venues],
	}
	""" response = {
		"count": 1,
		"data": [{"id": 2, "name": "The Dueling Pianos Bar", "num_upcoming_shows": 0,}],
	} """
	return render_template(
		"pages/search_venues.html",
		results=response,
		search_term=request.form.get("search_term", ""),
	)


#done
@app.route("/venues/<int:venue_id>")
def show_venue(venue_id):
	# shows the venue page with the given venue_id
	# TODO: replace with real venue data from the venues table, using venue_id
	try:
		v = Venue.query.get(venue_id)
		past_shows, upcoming_shows = show_times(v)
		if v:
			data = {
				"id": venue_id,
				"name": v.name,
				"genres": [g.name for g in v.genres],
				"address": v.address,
				"city": v.city,
				"state": v.state,
				"phone": v.phone,
				"website": "",
				"facebook_link": v.facebook_link,
				"seeking_talent": "",
				"seeking_description": "",
				"image_link": v.image_link,
				"past_shows": show_response_format(past_shows),
				"upcoming_shows": show_response_format(upcoming_shows),
				"past_shows_count": len(past_shows),
				"upcoming_shows_count": len(upcoming_shows),
			}
		else:
			data = {"name": "no venue with that id"}
	except Exception as e:
		print(e)
	""" data1 = {
		"id": 1,
		"name": "The Musical Hop",
		"genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
		"address": "1015 Folsom Street",
		"city": "San Francisco",
		"state": "CA",
		"phone": "123-123-1234",
		"website": "https://www.themusicalhop.com",
		"facebook_link": "https://www.facebook.com/TheMusicalHop",
		"seeking_talent": True,
		"seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
		"image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
		"past_shows": [
			{
				"artist_id": 4,
				"artist_name": "Guns N Petals",
				"artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
				"start_time": "2019-05-21T21:30:00.000Z",
			}
		],
		"upcoming_shows": [],
		"past_shows_count": 1,
		"upcoming_shows_count": 0,
	}
	data2 = {
		"id": 2,
		"name": "The Dueling Pianos Bar",
		"genres": ["Classical", "R&B", "Hip-Hop"],
		"address": "335 Delancey Street",
		"city": "New York",
		"state": "NY",
		"phone": "914-003-1132",
		"website": "https://www.theduelingpianos.com",
		"facebook_link": "https://www.facebook.com/theduelingpianos",
		"seeking_talent": False,
		"image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
		"past_shows": [],
		"upcoming_shows": [],
		"past_shows_count": 0,
		"upcoming_shows_count": 0,
	}
	data3 = {
		"id": 3,
		"name": "Park Square Live Music & Coffee",
		"genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
		"address": "34 Whiskey Moore Ave",
		"city": "San Francisco",
		"state": "CA",
		"phone": "415-000-1234",
		"website": "https://www.parksquarelivemusicandcoffee.com",
		"facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
		"seeking_talent": False,
		"image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
		"past_shows": [
			{
				"artist_id": 5,
				"artist_name": "Matt Quevedo",
				"artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
				"start_time": "2019-06-15T23:00:00.000Z",
			}
		],
		"upcoming_shows": [
			{
				"artist_id": 6,
				"artist_name": "The Wild Sax Band",
				"artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
				"start_time": "2035-04-01T20:00:00.000Z",
			},
			{
				"artist_id": 6,
				"artist_name": "The Wild Sax Band",
				"artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
				"start_time": "2035-04-08T20:00:00.000Z",
			},
			{
				"artist_id": 6,
				"artist_name": "The Wild Sax Band",
				"artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
				"start_time": "2035-04-15T20:00:00.000Z",
			},
		],
		"past_shows_count": 1,
		"upcoming_shows_count": 1,
	} """
	# data = list(filter(lambda d: d["id"] == venue_id, [data1, data2, data3]))[0]
	return render_template("pages/show_venue.html", venue=data)


#  Create Venue
#  ----------------------------------------------------------------

# done
@app.route("/venues/create", methods=["GET"])
def create_venue_form():
	form = VenueForm()
	return render_template("forms/new_venue.html", form=form)

# done
@app.route("/venues/create", methods=["POST"])
def create_venue_submission():
	# TODO: insert form data as a new Venue record in the db, instead
	# TODO: modify data to be the data object returned from db insertion
	try:
		data = request.form
		genres = data.getlist('genres')
		v = Venue( name= data['name'], city=data['city'], state=data['state'], address=data['address'], phone=data['phone'], facebook_link=data['facebook_link'])
		for genre in genres:
			g = Genre.query.filter_by(name=genre).first()
			g.venues.append(v)
		db.session.add(v)
		db.session.commit()
		# on successful db insert, flash success
		flash(f"Venue {data['name']}  was successfully listed!")
	except Exception as e:
		# TODO: on unsuccessful db insert, flash an error instead.
		db.session.rollback()
		flash(f'An error occurred. Venue {data["name"]} could not be listed. {e}')
	finally:
		db.session.close()
	# see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
	return render_template("pages/home.html")


@app.route("/venues/<venue_id>", methods=["DELETE"])
def delete_venue(venue_id):
	# TODO: Complete this endpoint for taking a venue_id, and using
	# SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

	# BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
	# clicking that button delete it from the db then redirect the user to the homepage
	return None


#  Artists
#  ----------------------------------------------------------------
# done
@app.route("/artists")
def artists():
	# TODO: replace with real data returned from querying the database
	try:
		data = db.session.query(Artist.id, Artist.name).order_by('id').all()
	except Exception as e:
		print(e)
	
	# data = [{"id": artist.id, "name": f"{artist.name}"} for artist in a]
	# print(data)
	""" data = [
		{"id": 4, "name": "Guns N Petals",},
		{"id": 5, "name": "Matt Quevedo",},
		{"id": 6, "name": "The Wild Sax Band",},] """
	return render_template("pages/artists.html", artists=data)

# done
@app.route("/artists/search", methods=["POST"])
def search_artists():
	# TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
	# seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
	# search for "band" should return "The Wild Sax Band".
	search = f"%{request.form.get('search_term')}%"
	artists = db.session.query(Artist).filter(Artist.name.ilike(search)).all()
	response = {
		"count": len(artists),
		"data": [{"id": a.id, "name": a.name, "num_upcoming_shows": 0,} for a in artists],
	}
	""" response = {
		"count": 1,
		"data": [{"id": 4, "name": "Guns N Petals", "num_upcoming_shows": 0,}],
	} """
	return render_template(
		"pages/search_artists.html",
		results=response,
		search_term=request.form.get("search_term", ""),
	)

# done
@app.route("/artists/<int:artist_id>")
def show_artist(artist_id):
	# shows the venue page with the given venue_id
	# TODO: replace with real venue data from the venues table, using venue_id
	try:
		a = Artist.query.get(artist_id)
		if a:
			data = {
				"id": a.id,
				"name": a.name,
				"genres": [g.name for g in a.genres],
				"city": a.city,
				"state": a.state,
				"phone": a.phone,
				"website": "",
				"facebook_link": a.facebook_link,
				"seeking_venue": "",
				"seeking_description": "",
				"image_link": a.image_link,
				"past_shows": "",
				"upcoming_shows": [],
				"past_shows_count": 0,
				"upcoming_shows_count": 0,
			}
		else:
			data = {"name": "no venue with that id"}
	except Exception as e:
		print(e)
	""" data1 = {
		"id": 4,
		"name": "Guns N Petals",
		"genres": ["Rock n Roll"],
		"city": "San Francisco",
		"state": "CA",
		"phone": "326-123-5000",
		"website": "https://www.gunsnpetalsband.com",
		"facebook_link": "https://www.facebook.com/GunsNPetals",
		"seeking_venue": True,
		"seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
		"image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
		"past_shows": [
			{
				"venue_id": 1,
				"venue_name": "The Musical Hop",
				"venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
				"start_time": "2019-05-21T21:30:00.000Z",
			}
		],
		"upcoming_shows": [],
		"past_shows_count": 1,
		"upcoming_shows_count": 0,
	}
	data2 = {
		"id": 5,
		"name": "Matt Quevedo",
		"genres": ["Jazz"],
		"city": "New York",
		"state": "NY",
		"phone": "300-400-5000",
		"facebook_link": "https://www.facebook.com/mattquevedo923251523",
		"seeking_venue": False,
		"image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
		"past_shows": [
			{
				"venue_id": 3,
				"venue_name": "Park Square Live Music & Coffee",
				"venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
				"start_time": "2019-06-15T23:00:00.000Z",
			}
		],
		"upcoming_shows": [],
		"past_shows_count": 1,
		"upcoming_shows_count": 0,
	}
	data3 = {
		"id": 6,
		"name": "The Wild Sax Band",
		"genres": ["Jazz", "Classical"],
		"city": "San Francisco",
		"state": "CA",
		"phone": "432-325-5432",
		"seeking_venue": False,
		"image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
		"past_shows": [],
		"upcoming_shows": [
			{
				"venue_id": 3,
				"venue_name": "Park Square Live Music & Coffee",
				"venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
				"start_time": "2035-04-01T20:00:00.000Z",
			},
			{
				"venue_id": 3,
				"venue_name": "Park Square Live Music & Coffee",
				"venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
				"start_time": "2035-04-08T20:00:00.000Z",
			},
			{
				"venue_id": 3,
				"venue_name": "Park Square Live Music & Coffee",
				"venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
				"start_time": "2035-04-15T20:00:00.000Z",
			},
		],
		"past_shows_count": 0,
		"upcoming_shows_count": 3,
	} 
	data = list(filter(lambda d: d["id"] == artist_id, [data1, data2, data3]))[0]"""
	return render_template("pages/show_artist.html", artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route("/artists/<int:artist_id>/edit", methods=["GET"])
def edit_artist(artist_id):
	form = ArtistForm()
	artist = {
		"id": 4,
		"name": "Guns N Petals",
		"genres": ["Rock n Roll"],
		"city": "San Francisco",
		"state": "CA",
		"phone": "326-123-5000",
		"website": "https://www.gunsnpetalsband.com",
		"facebook_link": "https://www.facebook.com/GunsNPetals",
		"seeking_venue": True,
		"seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
		"image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
	}
	# TODO: populate form with fields from artist with ID <artist_id>
	return render_template("forms/edit_artist.html", form=form, artist=artist)


@app.route("/artists/<int:artist_id>/edit", methods=["POST"])
def edit_artist_submission(artist_id):
	# TODO: take values from the form submitted, and update existing
	# artist record with ID <artist_id> using the new attributes

	return redirect(url_for("show_artist", artist_id=artist_id))


@app.route("/venues/<int:venue_id>/edit", methods=["GET"])
def edit_venue(venue_id):
	form = VenueForm()
	venue = {
		"id": 1,
		"name": "The Musical Hop",
		"genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
		"address": "1015 Folsom Street",
		"city": "San Francisco",
		"state": "CA",
		"phone": "123-123-1234",
		"website": "https://www.themusicalhop.com",
		"facebook_link": "https://www.facebook.com/TheMusicalHop",
		"seeking_talent": True,
		"seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
		"image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
	}
	# TODO: populate form with values from venue with ID <venue_id>
	return render_template("forms/edit_venue.html", form=form, venue=venue)


@app.route("/venues/<int:venue_id>/edit", methods=["POST"])
def edit_venue_submission(venue_id):
	# TODO: take values from the form submitted, and update existing
	# venue record with ID <venue_id> using the new attributes
	return redirect(url_for("show_venue", venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------


@app.route("/artists/create", methods=["GET"])
def create_artist_form():
	form = ArtistForm()
	return render_template("forms/new_artist.html", form=form)


@app.route("/artists/create", methods=["POST"])
def create_artist_submission():
	# called upon submitting the new artist listing form
	try:
		data = request.form
		print(data)
		genres = data.getlist('genres')
		a = Artist(name=data['name'], city=data['city'], state=data['state'], phone=data['phone'], facebook_link=data['facebook_link'])
		for genre in genres:
			g = Genre.query.filter_by(name=genre).first()
			g.artists.append(a)	
		db.session.add(a)
		# db.session.rollback()
		db.session.commit()
		print(a)
		# on successful db insert, flash success
		flash(f"Artist {data['name']} was successfully listed!")
	except Exception as e:
		# TODO: on unsuccessful db insert, flash an error instead.
		db.session.rollback()
		flash(f'An error occurred. Artist {data["name"]} could not be listed. {e}')
		print(e)
	finally:
		db.session.close()
	# see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
	return render_template("pages/home.html")


#  Shows
#  ----------------------------------------------------------------


@app.route("/shows")
def shows():
	# displays list of shows at /shows
	# TODO: replace with real venues data.
	#       num_shows should be aggregated based on number of upcoming shows per venue.
	shows = Show.query.all()
	data = [{"venue_id": s.id ,"venue_name": s.venue.name, "artist_id": s.artist_id, "artist_name": s.artist.name ,"artist_imag": "", "start_time": str(s.start_time)} for s in shows]
	""" data = [
		{
			"venue_id": 1,
			"venue_name": "The Musical Hop",
			"artist_id": 4,
			"artist_name": "Guns N Petals",
			"artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
			"start_time": "2019-05-21T21:30:00.000Z",
		},
		{
			"venue_id": 3,
			"venue_name": "Park Square Live Music & Coffee",
			"artist_id": 5,
			"artist_name": "Matt Quevedo",
			"artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
			"start_time": "2019-06-15T23:00:00.000Z",
		},
		{
			"venue_id": 3,
			"venue_name": "Park Square Live Music & Coffee",
			"artist_id": 6,
			"artist_name": "The Wild Sax Band",
			"artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
			"start_time": "2035-04-01T20:00:00.000Z",
		},
		{
			"venue_id": 3,
			"venue_name": "Park Square Live Music & Coffee",
			"artist_id": 6,
			"artist_name": "The Wild Sax Band",
			"artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
			"start_time": "2035-04-08T20:00:00.000Z",
		},
		{
			"venue_id": 3,
			"venue_name": "Park Square Live Music & Coffee",
			"artist_id": 6,
			"artist_name": "The Wild Sax Band",
			"artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
			"start_time": "2035-04-15T20:00:00.000Z",
		},
	] """
	return render_template("pages/shows.html", shows=data)


@app.route("/shows/create")
def create_shows():
	# renders form. do not touch.
	form = ShowForm()
	return render_template("forms/new_show.html", form=form)


@app.route("/shows/create", methods=["POST"])
def create_show_submission():
	# called to create new shows in the db, upon submitting new show listing form
	# TODO: insert form data as a new Show record in the db, instead
	try:
		data = request.form
		a = Artist.query.get(data['artist_id'])
		v = Venue.query.get(data['venue_id'])
		if a and v:
			s = Show(artist=a, venue=v, start_time=data['start_time'])
			db.session.add(s)
		else:
			raise Exception("Either the venue or the artist doesn't exist")
		db.session.commit()
		# on successful db insert, flash success
		flash("Show was successfully listed!")
	# TODO: on unsuccessful db insert, flash an error instead.
	except Exception as e:
		db.session.rollback()
		print(e)
		flash(f'An error occurred. Show could not be listed. {e}')
	finally:
		db.session.close()
	# see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
	return render_template("pages/home.html")


@app.errorhandler(404)
def not_found_error(error):
	return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(error):
	return render_template("errors/500.html"), 500


if not app.debug:
	file_handler = FileHandler("error.log")
	file_handler.setFormatter(
		Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
	)
	app.logger.setLevel(logging.INFO)
	file_handler.setLevel(logging.INFO)
	app.logger.addHandler(file_handler)
	app.logger.info("errors")

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == "__main__":
	app.run()

# Or specify port manually:
"""
if __name__ == '__main__':
		port = int(os.environ.get('PORT', 5000))
		app.run(host='0.0.0.0', port=port)
"""
