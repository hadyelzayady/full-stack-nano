from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi 
import cgitb
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Restaurant, Base, MenuItem

def addEntry(resName):
    newRestaurant=Restaurant(name=resName)
    session.add(newRestaurant)
    session.commit()
    return

def update(restaurantId,newName):
    restaurant=session.query(Restaurant).filter_by(id=restaurantId).one()
    if restaurantName != None:
        restaurant.name=newName
        session.commit()
    return

def deleteRestaurant(Id):
    rest=session.query(Restaurant).filter_by(id=Id).one()
    session.delete(rest)
    session.commit()
    return
class webserverHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('Content-type','text/html')
                self.end_headers()
                output=""
                restaurantsNames=session.query(Restaurant).order_by(Restaurant.name)
                output+="<html><body>"
                output+='''<h1 style="color:#FF0000;text-align:center;"><i><b>My Restaurants</i></b></h1>'''
                output+='''<h2>Add Restaurant</h2><button   onclick="location.href='restaurants/new'">add restaurant</button>'''
                for rest in restaurantsNames:
                    output+='''<p style="font-size:30p">%s</p>''' % rest.name
                    output+='''<a href="restaurants/%s/edit">Edit</a><br>''' % rest.id
                    output+='''<a href="restaurants/%s/delete">Delete</a><br><br>''' % rest.id
                output+="</body></html>"
                self.wfile.write(output)
                return
                
                #add restaurant
            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type','text/html')
                self.end_headers()
                output=open("addRestaurant.html",'r')
                self.wfile.write(output.read())
                return

                #edit restaurant 
            if self.path.endswith("edit"):
                self.send_response(200)
                self.send_header('Content-type','text/html')
                self.end_headers()
                Id = self.path.split('/')[2]
                try:
                    restaurant=session.query(Restaurant).filter_by(id=Id).one()
                    output=""
                    output+='''<html><body>'''
                    output+='''<form method="POST" action='/restaurants/%s/edit' enctype="multipart/form-data"><input type="text" name="restaurantName" placeholder="%s"><input type="submit" value="Edit"></form''' % (Id , restaurant.name)
                    self.wfile.write(output)
                    return 
                except:
                    output="<html><body><h1>Eorror ,id not found</h1><br><a href='/restaurants'>back to menu</a></body></html>"
                    self.wfile.write(output)

                #delete restaurant
            if self.path.endswith("delete"):
                self.send_response(200)
                self.send_header('Content-type','text/html')
                self.end_headers()
                Id = self.path.split('/')[2]
                restaurant=session.query(Restaurant).filter_by(id=Id).one()
                output=""
                output+='''<h1>Are you sure you want to delete %s ?</h1><br><form action="/restaurants/%s/delete"  enctype="multipart/form-data" method="POST"><input type="submit" value="Delete"></form>''' %(restaurant.name,Id)
                self.rfile.write(output)                
                return
        except IOError:
            self.send_error(404,"File Not Found %s" %  self.path)

    def do_POST(self):
        try:
            print self.path
            ctype, pdict = cgi.parse_header(
                self.headers.getheader('content-type')) 
            if ctype == 'multipart/form-data':
                fields = cgi.parse_multipart(self.rfile,pdict)
                restaurantName=fields.get('restaurantName')
                if self.path.endswith("edit"):
                    Id = self.path.split('/')[2]
                    update(Id,restaurantName[0])
                elif self.path.endswith("new"):
                    addEntry(restaurantName[0])
                elif self.path.endswith("delete"):
                    Id = self.path.split('/')[2]
                    deleteRestaurant(Id)
            self.send_response(301)
            self.send_header('Content-type', 'text/html')
            self.send_header('Location', '/restaurants')
            self.end_headers()
            return
        except:
            print "error"



def main():# configure the webserver
    try:
        port=8080
        server_address=('',port)
        server=HTTPServer(server_address,webserverHandler)
        print "Web server runnign on port %s" %port
        server.serve_forever()
    except KeyboardInterrupt:
        print "^C entered, stoping web server.."
        server.socket.close()

if __name__ =='__main__':
    print __name__
    engine = create_engine('sqlite:///restaurantmenu.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    main()
