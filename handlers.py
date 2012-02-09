import logging

# Google App Engine imports
from google.appengine.ext import db

# Webapp2 imports
import webapp2
from webapp2_extras import sessions

class BaseHandler(webapp2.RequestHandler):
  """Enables session management"""
  def dispatch(self):
    self.session_store = sessions.get_store(request = self.request)
    
    try:
      webapp2.RequestHandler.dispatch(self)
    finally:
      logging.info(self.session)
      self.session_store.save_sessions(self.response)

  @webapp2.cached_property
  def session(self):
    return self.session_store.get_session()

  @property
  def flash(self):
    flashes = self.session.get_flashes()
    if flashes:
      return flashes[0]
    
  @flash.setter
  def flash(self, value):
    self.session.add_flash(value)

class UserHandler(BaseHandler):
  """Handler facilitating a currently logged in user (i.e. a DJ) and their programs, etc.
  """
  def set_session_user(self, dj):
    """Takes a Dj model, and stores values into the session"""
    self.session['dj'] = {
        'key' : str(dj.key()),
        'fullname' : dj.p_fullname,
        'lowername' : dj.p_lowername,
        'email' : dj.p_email,
        }

  @user.getter
  def get_user(self):
    return self.dj_key

  @user.setter
  def set_user(self, dj):
    self.set_session_user(dj)
  
  def set_session_program(self, pgm):
    """Takes a Program model, and stores values to the session"""
    self.session['program'] = {
        'key' : str(pgm.key()),
        'slug' : pgm.p_slug,
        'title' : pgm.p_title,
        }

  @program.getter
  def get_program(self):
    return self.program_key

  @program.setter
  def set_program(self, pgm):
    self.set_session_program(pgm)

  def session_logout(self):
    """Logs the dj out, deleting program and dj keys in the session"""
    for key in ('dj', 'program'):
      if key in self.session:
        del self.session[key]

  def session_has_login(self):
    return self.session.has_key('dj')

  def session_has_program(self):
    return self.session.has_key('program')

  @property
  def dj_key(self):
    key = self.session.get('dj').get('key')
    if key is not None:
      return db.Key(key)
    return None

  @property
  def program_key(self):
    key = self.session.get('program').get('key')
    if key is not None:
      return db.Key(key)
    return None
