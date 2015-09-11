from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem
import re

class webserverHandler(BaseHTTPRequestHandler):
    engine = create_engine('sqlite:///restaurantmenu.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind = engine)

    def do_GET(self):
        try:
            if self.path.endswith("/hello"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output = "<html><body>Hello!"

                output += """<form method='POST' enctype='multipart/form-data' action='/hello'>
                <h2>What would you like me to say?</h2><input name='message' type='text'>
                <input type='submit' value='Submit'></form>"""

                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/restaurants"):   
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = "<html><body>"
                output += "<a href='/restaurants/new'>Make a new restaurant</a><br><br>"

                session = self.DBSession()
                restaurants = session.query(Restaurant).all()
                for restaurant in restaurants:
                    output += restaurant.name+"<br>"
                    output += "<a href='restaurants/"+str(restaurant.id)+"/edit'>Edit</a>&nbsp"
                    output += "<a href='restaurants/"+str(restaurant.id)+"/delete'>Delete</a><br><br>"

                output +="</body></html>"
                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/restaurants/new"):   
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = "<html><body>"
                output += "<h2>Make a new restaurant</h2>"
                output += "<form method='POST' enctype='multipart/form-data' action=''>"
                output += "<input name='newrestaurant' type='text'>"
                output += "<input type='submit' value='Create'></form>"
                
                output +="</body></html>"
                self.wfile.write(output)
                print output
                return


            if self.path.endswith("/edit"): 
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = "<html><body>"
                i = self.path.split('/')[2]
                session = self.DBSession()
                restaurant = session.query(Restaurant).filter_by(id = i).one()
                
                output += "<form method='POST' enctype='multipart/form-data' action=''>"
                output += "<h2> %s </h2><input name='rename' type='text'>" % restaurant.name
                output += "<input type='submit' value='Rename'></form>"

                output +="</body></html>"
                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/delete"): 
                i = self.path.split('/')[2]                
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                session = self.DBSession()
                restaurant = session.query(Restaurant).filter_by(id = i).one()
                
                output = "<html><body>"  
                output += "<form method='POST' enctype='multipart/form-data' action=''>"
                output += "<h2> Are you sure you want to delete %s?</h2>" % restaurant.name
                output += "<input type='submit' value='Delete'></form>"

                output +="</body></html>"
                self.wfile.write(output)
                print output
                return

        except:
            self.send_error(404, "File Not Found %s" % self.path)

    def do_POST(self):
        if self.path.endswith("/edit"):
            try:
                i = self.path.split('/')[2]                
                self.send_response(301)
                self.send_header('Location', '/restaurants')
                self.end_headers()

                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    newname = fields.get('rename')

                session = self.DBSession()
                restaurant = session.query(Restaurant).filter_by(id = i).one()
                restaurant.name = newname[0]
                session.add(restaurant)
                session.commit()

                restaurant = session.query(Restaurant).filter_by(id = i).one()
                
                output = "<html><body>"
                output += "<form method='POST' enctype='multipart/form-data' action=''>"
                output += "<h2> %s </h2><input name='rename' type='text'>" % restaurant.name
                output += "<input type='submit' value='Rename'></form>"

                output +="</body></html>"

                self.wfile.write(output)
                print output

            except:
                pass

        if self.path.endswith("/delete"):
            try:
                i = self.path.split('/')[2]                
                self.send_response(301)
                self.send_header('Location', '/restaurants')
                self.end_headers()

                session = self.DBSession()
                restaurant = session.query(Restaurant).filter_by(id = i).one()
                session.delete(restaurant)
                session.commit()

            except:
                pass 

        if self.path.endswith("/restaurants/new"):
            try:
                self.send_response(301)
                '''self.send_header('Location', '/restaurants')'''
                self.end_headers()

                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    newrestaurant = fields.get('newrestaurant')

                session = self.DBSession()
                restaurant = Restaurant(name = newrestaurant[0])
                session.add(restaurant)
                session.commit()

                restaurant = session.query(Restaurant).filter_by(name = newrestaurant[0]).one()

                output = "<html><body>"
                output += restaurant.name+str(restaurant.id)
                output +="</body></html>"

                self.wfile.write(output)
                print output
                
            except:
                pass

def main():
    try:
        port = 8080
        server = HTTPServer(('',port), webserverHandler)
        print "Web server running on port %s" % port
        server.serve_forever()

    except KeyboardInterrupt:
        print "^C entered, stopping web server..."
        server.socket.close()

if __name__ == '__main__':
    main()
