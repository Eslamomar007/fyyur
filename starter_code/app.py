#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm

from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app,db)
# TODO: connect to a local postgresql database
#done

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_description= db.Column(db.String(500))
    shows = db.relationship('Show',backref='venue_shows',lazy =True)
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    shows = db.relationship('Show', backref='artist_shows', lazy=True)
    

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
class Show(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
  start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)



# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

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
  #done
  data = []
  s = db.session.query(Venue.city, Venue.state).group_by(Venue.city,Venue.state).all()
  for i in s:
      venues = db.session.query(Venue).filter(Venue.city==i.city, Venue.state==i.state)
      data += [{'city': i.city,
                'state': i.state,
                'venues':venues
                }]
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  key = request.form['search_term']
  
  
  response={
      "count": db.session.query(Venue).filter(Venue.name.ilike('%'+key+'%')).count(),
    "data": db.session.query(Venue).filter(Venue.name.ilike('%'+key+'%')).all()
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venues = Venue.query.get(venue_id)

  data = {
      "id": venues.id,
      "name": venues.name,
      "genres": db.session.query(Venue.genres).filter(Venue.id == venue_id).all(),
      "city": venues.city,
      "state": venues.state,
      "phone": venues.phone,
      "facebook_link": venues.facebook_link,
      "seeking_venue": venues.seeking_talent,
      "seeking_description": venues.seeking_description,
      "image_link": venues.image_link,
      "past_shows": [],
      "upcoming_shows": [],
      "past_shows_count":  db.session.query(Show).filter(Show.venue_id == venue_id, Show.start_time <= datetime.today()).count(),
      "upcoming_shows_count":  db.session.query(Show).filter(Show.venue_id == venue_id, Show.start_time >= datetime.today()).count(),
  }
  pastshows = db.session.query(Show).filter(
      Show.venue_id == venue_id, Show.start_time <= datetime.today()).all()
  upshows = db.session.query(Show).filter(
      Show.venue_id == venue_id, Show.start_time >= datetime.today()).all()

  for item in pastshows:
    artist = db.session.query(Artist).filter(
        Artist.id == item.artist_id).first()
    data['past_shows'].append({'artist_image_link': artist.image_link, 'artist_name': artist.name,
                               'artist_id': artist.id, 'start_time': str(item.start_time)})

  for item in upshows:
    artist = db.session.query(Artist).filter(
        Artist.id == item.artist_id).first()
    data['upcoming_shows'].append({'artist_image_link': artist.image_link, 'artist_name': artist.name,
                               'artist_id': artist.id, 'start_time': str(item.start_time)})


  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET','POST'])
def create_venue_form():
  form = VenueForm()

  if request.method=='POST':
    try:
      name=form.name.data
      venue = Venue(name=form.name.data, city=form.city.data, state=form.state.data, facebook_link=form.facebook_link.data,
                    genres=form.genres.data, address=form.address.data, phone=form.phone.data)
      db.session.add(venue)
      db.session.commit()
      flash('Venue ' + name + ' was successfully listed!')

    except:
      flash('An error occurred. Venue ' +
            form.name.data + ' could not be listed.')        
      db.session.rollback()
      print(sys.exc_info())
    finally:
      return redirect(url_for('create_venue_form'))
      db.session.close()


  return render_template('forms/new_venue.html', form=form)
'''
@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
    print(form.name.data, form.city.data, form.state.data, form.facebook_link.data,
          form.genres.data, form.address.data, form.phone.data)
    venue = Venue(name=form.name.data, city=form.city.data, state=form.state.data, facebook_link=form.facebook_link.data,
                  genres=form.genres.data, address=form.address.data, phone=form.phone.data)
    db.session.add(venue)
    db.session.commit()

  except:
    print('asiwqq')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    return redirect(url_for('create_venue_form'))

  # on successful db insert, flash success
  flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')
  '''

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):

  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    Venue.query.filter(Venue.id == venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  #done
  artists = Artist.query.all()
  data=artists
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  key = request.form['search_term']
  response={
      "count": db.session.query(Venue).filter(Venue.name.ilike('%'+key+'%')).count(),
    "data": db.session.query(Venue).filter(Venue.name.ilike('%'+key+'%')).all()
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  artist = Artist.query.get(artist_id)
  
  data={
        "id": artist.id,
        "name": artist.name,
        "genres": db.session.query(Artist.genres).filter(Artist.id == artist_id).all(),
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_talent,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows":[],
        "upcoming_shows": [],    
      "past_shows_count":  db.session.query(Show).filter(Show.artist_id == artist_id, Show.start_time <= datetime.today()).count(),
      "upcoming_shows_count":  db.session.query(Show).filter(Show.artist_id == artist_id, Show.start_time >= datetime.today()).count(),
    }
  pastshows = db.session.query(Show).filter(
      Show.artist_id == artist_id, Show.start_time <= datetime.today()).all()
  upshows = db.session.query(Show).filter(
      Show.artist_id == artist_id, Show.start_time >= datetime.today()).all()

  for item in pastshows:
    venue = db.session.query(Venue).filter(Venue.id == item.venue_id).first()
    data['past_shows'].append({'venue_image_link': venue.image_link, 'venue_name': venue.name,'venue_id':venue.id, 'start_time': str(item.start_time)})
  
  for item in upshows:
    venue = db.session.query(Venue).filter(Venue.id == item.venue_id).first()
    data['upcoming_shows'].append({'venue_image_link': venue.image_link, 'venue_name':venue.name , 'venue_id':venue.id, 'start_time': str(item.start_time)})



  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET','POST'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  if request.method == 'POST':
      try:
        name = form.name.data
        artist.name = name
        artist.city = form.city.data
        artist.state = form.state.data
        artist.phone = form.phone.data
        artist.genres = form.genres.data
        artist.facebook_link = form.facebook_link.data
        db.session.commit()
        flash('artist ' + name + ' was successfully edited!')
        print(Artist.query.get(artist_id).city)

      except:
        flash('An error occurred. artist ' +
              form.name.data + ' could not be edited.')
        db.session.rollback()
        print(sys.exc_info())
      finally:
        db.session.close()
        return redirect('/artists/'+str(artist_id)+'/edit')

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)
'''
@app.route('/artists/<int:artist_id>/edit', methods=['POST','GET'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))
'''

@app.route('/venues/<int:venue_id>/edit', methods=['GET','POST'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  if request.method == 'POST':
      try:
        name=form.name.data
        venue.name = name
        venue.city = form.city.data
        venue.state = form.state.data
        venue.phone = form.phone.data
        venue.genres = form.genres.data
        venue.facebook_link = form.facebook_link.data
        db.session.commit()
        flash('Venue ' + name + ' was successfully edited!')
 
      except:
        flash('An error occurred. Venue ' +
              form.name.data + ' could not be edited.')
        db.session.rollback()
        print(sys.exc_info())
      finally:
        db.session.close()
        return redirect('/venues/'+str(venue_id)+'/edit')
                
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

'''
@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------
'''

@app.route('/artists/create', methods=['GET','POST'])
def create_artist_form():
  form = ArtistForm()
  if request.method=='POST':
    try:
      name = form.name.data
      artist = Artist(name=form.name.data, city=form.city.data, state=form.state.data, facebook_link=form.facebook_link.data,
                      genres=form.genres.data, phone=form.phone.data)
      db.session.add(artist)
      db.session.commit()
      flash('Artist ' + name + ' was successfully listed!')

    except:
      db.session.rollback()
      flash('An error occurred. Artist ' +
            form.name.data + ' could not be listed.')
      print(sys.exc_info())
    finally:
      db.session.close()
      return redirect(url_for('create_artist_form'))


  return render_template('forms/new_artist.html', form=form)

'''
@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
    artist = Artist(nam=form.name.data, city=form.city.data, state=form.state.data, facebook_link=form.facebook_link.data,
                  genres=form.genres.data, address=form.address.data, phone=form.phone.data)
    db.session.add(veartistnue)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')      
    print(sys.exc_info())
  finally:
    db.session.close()
    return redirect(url_for('create_artist_form'))

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g.,       flash('An error occurred. Artist ' + data.name + ' could not be listed.')      print(sys.exc_info())

  return render_template('pages/home.html')

'''
#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data=[]
  shows = Show.query.all()
  for show in shows:
    venue = Venue.query.get(show.venue_id)
    artist = Artist.query.get(show.artist_id)
    data += [{"venue_id": venue.id,
              "venue_name": venue.name,
              "artist_id": artist.id,
              "artist_name": artist.name,
              "artist_image_link": artist.image_link,
              "start_time": str(show.start_time)}]
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create', methods=['POST','GET'])
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  if request.method == 'POST':
      id1 = Artist.query.get_or_404(int(form.artist_id.data))
      id2 = Venue.query.get_or_404(int(form.venue_id.data))
      try:
        show = Show(artist_id=form.artist_id.data,
                    venue_id=form.venue_id.data, start_time=form.start_time.data)
        db.session.add(show)
        db.session.commit()
        flash('Show  was successfully listed!')

      except:
        flash('An error occurred. Show ' +
              form.name.data + ' could not be listed.') 
        db.session.rollback()
        print(sys.exc_info())

      finally:
        db.session.close()
        return redirect(url_for('create_shows'))    

  return render_template('forms/new_show.html', form=form)

'''
@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')
'''
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
