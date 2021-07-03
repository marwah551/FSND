#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

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
from sqlalchemy import literal


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234567@localhost:5432/fyyur'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate=Migrate(app,db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres=db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    looking_for_talent=db.Column(db.Boolean)
    seeking_description=db.Column(db.String(500))
    shows = db.relationship('Show',backref='venue',lazy=True, cascade="save-update, merge, delete")

 



    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    looking_for_venues=db.Column(db.Boolean)
    seeking_description=db.Column(db.String(500))
    shows = db.relationship('Show',backref='artist',lazy=True, cascade="save-update, merge, delete")
    

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
  __tablename__='Show'

  id=db.Column(db.Integer, primary_key=True)
  start_time=db.Column(db.DateTime(timezone=True))
  venue_id=db.Column(db.Integer,db.ForeignKey('Venue.id') ,nullable=False)
  artist_id=db.Column(db.Integer,db.ForeignKey('Artist.id') ,nullable=False)
  

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  all_places = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state).all()
  data = []
  for place in all_places:
      venues = Venue.query.filter_by(state = place.state).filter_by(city = place.city).all()
      venue_data = []
      data.append({
          'city': place.city,
          'state': place.state,
          'venues': venue_data
      })
      for venue in venues:
          venue_data.append({
              'id': venue.id,
              'name': venue.name 
              })
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_word = request.form.get('search_term', '')
  res = db.session.query(Venue).filter(Venue.name.ilike(f'%{search_word}%')).all()
  data = []
  for r in res:
    data.append({
      "id": r.id,
      "name": r.name
    })
  
  response = { "count": len(res), "data": data }

  return render_template('pages/search_venues.html', results = response, search_term = request.form.get('search_term', ''))

   
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id 

  #resourse https://flask-sqlalchemy.palletsprojects.com/en/2.x/queries/

 all_venue = Venue.query.filter_by(id=venue_id).first_or_404()

 data = {
        'id': venue.id,
        'name': venue.name,
        'genres': venue.genres,
        'address': venue.address,
        'city': venue.city,
        'state': venue.state,
        'phone': venue.phone,
        'image_link': venue.image_link,
        'facebook_link': venue.facebook_link,
        'website_link': venue.website_link,
        'looking_for_talent': venue.seeking_talent,
        'seeking_description': venue.seeking_description,
        }
 
   
 
 return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)


 

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
 #resourse is here https://stackoverflow.com/questions/42554368/python-flask-inserting-data-from-form
   
  new_venue = Venue(
  name= request.form['name'],
  city= request.form['city'],
  address= request.form['address'],
  genres= request.form['genres'],
  phone=request.form['phone'],
  facebook_link=request.form['facebook_link'],
  website_link=request.form['website_link'],
  image_link=request.form['image_link']
)
  try:
    db.session.add(new_venue)
    db.session.commit()
   # on successful db insert, flash success
    flash('Venue ' + new_venue.name + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.

  except:
   db.session.rollback() 
   flash('An error occurred. Venue ' + new_venue.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  deleted_venue = Venue.query.get(Venue.venue_id)
  
  try:
    db.session.delete(deleted_venue)
    db.session.commit()
    flash('Venue was successfully deleted!')
  except:
    db.session.rollback()
    flash('please try again. Venue could not be deleted.')
  finally:
    db.session.close()
  
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  
  data = db.session.query(Artist).all()

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  all_artist = Artist.query.filter_by(id=artist_id).first_or_404()

  data = {
        "id" : artist.id,
        "name" : artist.name,
        "genres" : artist.genres,
        "address" : artist.address,
        "city" : artist.city,
        "state" : artist.state,
        "phone" : artist.phone,
        "image_link" : artist.image_link,
        "facebook_link" : artist.facebook_link,
        "website_link" : artist.website_link,
        "looking_for_talent" : artist.seeking_talent,
        "seeking_description" : artist.seeking_description
        }
 
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  getArtistId=Artist.session.get(artist.id)

  data={
  'id':artist.id,
  'name':artist.name,
  'city':astist.city,
  'address':artist.address,
  'genres':astist.genres,
  'phone':artist.phone,
  'facebook_link':artist.facebook_link,
  'website_link':artist.website_link,
  'image_link':artist.image_link
  }

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  editArtist=Artist.session.get(artist.id)
  edit_artisr= Artist(
  name= request.form['name'],
  city= request.form['city'],
  address= request.form['address'],
  genres= request.form['genres'],
  phone=request.form['phone'],
  facebook_link=request.form['facebook_link'],
  website_link=request.form['website_link'],
  image_link=request.form['image_link']
)

  db.session.commit()
  db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  getVenuetId=Venue.session.get(venue.id)
  data={
  'id':venue.id,
  'name':venue.name,
  'city':venue.city,
  'address':venue.address,
  'genres':venue.genres,
  'phone':venue.phone,
  'facebook_link':venue.facebook_link,
  'website_link':venue.website_link,
  'image_link':venue.image_link
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  editVenuet=Venue.session.get(Venue.id)
  edit_venue= Venue(
  name= request.form['name'],
  city= request.form['city'],
  address= request.form['address'],
  genres= request.form['genres'],
  phone=request.form['phone'],
  facebook_link=request.form['facebook_link'],
  website_link=request.form['website_link'],
  image_link=request.form['image_link']
 )
  db.session.commit()
  db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  
 

  new_artist = Artist(

    name= request.form['name'],
    city= request.form['city'],
    genres= request.form['genres'],
    phone=request.form['phone'],
    facebook_link=request.form['facebook_link'],
    website_link=request.form['website_link'],
    image_link=request.form['image_link']
 
  )
        
   
  try:
      db.session.add(new_artist)
      db.session.commit()
    # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')

  except:
      db.session.rollback()
    # TODO: on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

  finally:
        db.session.close()

  
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  displayshows = db.session.query(Show).join(Artist).join(Venue).all()

  data=[]

  for show in displayshows:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name, 
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
 
  error = False
  new_show = Show(
    artist_id = request.form['artist_id'],
    venue_id = request.form['venue_id'],
    start_time = request.form['start_time']
    )
 
 
  try:
    db.session.add(new_show)
    db.session.commit()

  except: 
    error = True
    db.session.rollback()
  finally: 
    db.session.close()
  if error: 
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Show could not be listed.')
  else: 
    # on successful db insert, flash success
    flash('Show was successfully listed!')

  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')


    

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
