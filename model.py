import logging

from google.appengine.api import users
from google.appengine.ext import db

class User(db.Model):
    # Just store email address, because GAFYD seems to be buggy (omits domain in stored email or something...)
    email = db.StringProperty()
    following = db.StringListProperty()
    enabled = db.BooleanProperty(default=True)
    tags = db.StringListProperty()
    tags_following = db.StringListProperty()
    
    def pretty_name(self):
        return self.email.split('@')[0]

class UserProfile(db.Model):
    user = db.ReferenceProperty(User)
    append_snippets = db.BooleanProperty(default=False)


class Snippet(db.Model):
    user = db.ReferenceProperty(User)
    text = db.TextProperty()
    date = db.DateProperty()
    
def compute_following(current_user, users):
    """Return set of email addresses being followed by this user."""
    email_set = set(current_user.following)
    tag_set = set(current_user.tags_following)
    following = set()
    for u in users:
        if ((u.email in email_set) or
            (len(tag_set.intersection(u.tags)) > 0)):
            following.add(u.email)
    return following            
    
def user_from_email(email):
    return User.all().filter("email =", email).fetch(1)[0]
    

def create_or_replace_snippet(user, text, date):
    """this name no longer makes sense..."""
    current_profile = UserProfile.all().filter("user =", user).fetch(1)[0]
    snippet = Snippet(text=text, user=user, date=date)

    if current_profile.append_snippets:
        for current in Snippet.all().filter("date =", date).filter("user =", user).fetch(10):
            snippet = current
            snippet.text = snippet.text + "\r\n" + text
            continue
    else:
        # Delete existing (yeah, yeah, should be a transaction)
        for existing in Snippet.all().filter("date =", date).filter("user =", user).fetch(10):
            existing.delete()
    
    snippet.put()
       