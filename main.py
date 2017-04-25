import webapp2
import os
import jinja2

from google.appengine.ext import db

#Jinja template init
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

#Handler helper class
class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

#Post db object constructor
class Post(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

    def get_permalink(self):
        return "/blog/" + str(self.key().id_or_name())

#Front page handler
class Index(Handler):
    def get(self):
        self.render('blog.html')

#New post handler
class NewPost(Handler):
    def get(self):
        self.render('newpost.html')

    def post(self):
        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            p = Post(subject = subject, content = content)
            p.put()
            link = str(p.key().id())
            self.redirect('/blog/' + link)
        else:
            error = "subject and content, please!"
            self.render("newpost.html", subject=subject, content=content, error=error)

#Post view handler
class ViewPostHandler(Handler):
    def get(self, id):
        p = Post.get_by_id(int(id))

        if not p:
            error = "Post does not exist!"
            self.render("postview.html", error=error)
        else:
            self.render("postview.html", subject=p.subject, content=p.content, created=p.created)

#Blog handler
class Blog(Handler):
    def get(self):
        display_posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC LIMIT 5")
        self.render('blog.html', display_posts = display_posts)

app = webapp2.WSGIApplication([
    ('/', Blog),
    ('/blog', Blog),
    ('/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
