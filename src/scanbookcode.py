from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.ext.webapp import template
import datetime
import os


class ScanData(db.Model):
    owner = db.UserProperty()
    scancode = db.StringProperty(multiline=False)
    date = db.DateTimeProperty(auto_now=True)


class MainPage(webapp.RequestHandler):
    def get(self):
        fpath = os.path.join(os.path.dirname(__file__), 'views', 'index.html')
        html = template.render(fpath, {})
        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write(html)


class addPage(webapp.RequestHandler):
    def get(self, scan_code):
        user = users.get_current_user()
        if user:
            scandata = ScanData()
            scandata.owner = user
            scandata.scancode = scan_code
            scandata.put()
            self.redirect('http://group-aff.appspot.com/amaraku?isbn=' + scan_code)
        else:
            self.redirect(users.create_login_url(self, self.request.uri))



class delPage(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            scanDatas = ScanData.gql("WHERE owner = :owner ORDER BY date", owner = user)
            db.delete(scanDatas)
            fpath = os.path.join(os.path.dirname(__file__), 'views', 'delete.html')
            html = template.render(fpath, {})
            self.response.headers['Content-Type'] = 'text/html'
            self.response.out.write(html)
        else:
            self.redirect(users.create_login_url(self, self.request.uri))



class viewPage(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            scanDatas = ScanData.gql("WHERE owner = :owner ORDER BY date", owner = user)
            self.response.headers['Content-Type'] = 'text/plain'
            for scandata in scanDatas:
                self.response.out.write(scandata.scancode + '\n')
        else:
            self.redirect(users.create_login_url(self, self.request.uri))

class clearPage(webapp.RequestHandler):
    def get(self):
        scanDatas = ScanData.gql("WHERE date < :limitDate", limitDate = datetime.datetime.today() + datetime.timedelta(days = -90))
        db.delete(scanDatas)
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Cleared.')

class errPage(webapp.RequestHandler):
    def get(self, param):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Invalid parameter(s): ' + param)


application = webapp.WSGIApplication([('/', MainPage),
                                      ('/a/(.*)', addPage),
                                      ('/d', delPage),
                                      ('/v', viewPage),
                                      ('/clear', clearPage),
                                      ('/(.*)', errPage)],
                                      debug=True)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
