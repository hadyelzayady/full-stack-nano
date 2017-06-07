from __future__ import print_function # In python 2.7
import sys
from flask import Flask, render_template, request, redirect, url_for, flash,jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

app = Flask(__name__)

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()
# main page
@app.route('/')
@app.route('/restaurants/')
def restaurants():
    allRestaurants=session.query(Restaurant).order_by(Restaurant.name)
    return render_template('restaurants.html',restaurants=allRestaurants)

@app.route('/restaurants/<int:restaurant_id>/edit',methods=['POST','GET'])
def editRestaurant(restaurant_id):
    if request.method == 'POST':
        newName=request.form['name']
        if newName =='':
            flash('no change happended')
            return render_template('editRestaurant.html',restaurant=session.query(Restaurant).filter_by(id=restaurant_id).one())
        else:
            restaurant=session.query(Restaurant).filter_by(id=restaurant_id).first()
            flash('name changed from:%s to %s' %(restaurant.name,newName))
            restaurant.name=newName
            session.commit()
            return redirect('restaurants') 

    else:# get request
        restaurant=session.query(Restaurant).filter_by(id=restaurant_id).one()
        return render_template('editRestaurant.html',restaurant=session.query(Restaurant).filter_by(id=restaurant_id).one())
  
def deleteRestaurantItems(restaurant_id):
    items=session.query(MenuItem).filter_by(restaurant_id=restaurant_id)
    for item in items:
        session.delete(item)
    session.commit()
    return   

@app.route('/restaurants/<int:restaurant_id>/delete',methods=['GET','POST'])
def deleteRestaurant(restaurant_id):
    restaurant=session.query(Restaurant).filter_by(id=restaurant_id).first()
    if request.method=='POST':
        restaurant=session.query(Restaurant).filter_by(id=restaurant_id).first()
        flash('%s deleted' % restaurant.name)
        session.delete(restaurant)
        #delete restaurant items
        deleteRestaurantItems(restaurant.id)            
        #
        session.commit()
        return redirect(url_for('restaurants'))
    else :#get request
        if restaurant=='':
            flash('not exist')
            return redirect(url_for('restaurants'))
        return render_template('deleteRestaurant.html',restaurant=restaurant)

@app.route('/restaurants/multiple-delete',methods=['POST'])
def deleteMultipleRestaurants():
    restaurants=request.form.getlist('restaurant_id')
    for restaurant_id in restaurants:
        session.delete(session.query(Restaurant).filter_by(id=restaurant_id).one())
        deleteRestaurantItems(restaurant_id)
    session.commit()
    return redirect(url_for('restaurants'))

@app.route('/restaurants/delete-All',methods=['POST'])
def deleteAllRestaurants():
    restaurants=session.query(Restaurant).all()
    for restaurant in restaurants:
        session.delete(restaurant)
        deleteRestaurantItems(restaurant_id=restaurant.id)
    session.commit()
    return redirect(url_for('restaurants'))

@app.route('/restaurants/new',methods=['POST','GET'])
def newRestaurant():
    if request.method == 'POST':
        name=request.form['name']
        if name =='':
            flash('empty name !')
            return redirect(url_for('newRestaurant'))
        else:
            flash('new restaruant added:%s' % name)
            restaurant=Restaurant(name=name)
            session.add(restaurant)
            session.commit()
            return redirect(url_for('restaurants'))
    else:# get request
        return render_template('addRestaurant.html')


tableheaders=['Appetizer','Entree','Dessert','Beverage']
@app.route('/restaurants/<int:restaurant_id>/')
@app.route('/restaurants/<int:restaurant_id>/menu/<string:hilightFlag>')
@app.route('/restaurants/<int:restaurant_id>/menu/')
def restaurantMenu(restaurant_id,hilightFlag="None"):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id)
    return render_template(
        'menu.html',hilightFlag=hilightFlag ,restaurant=restaurant, items=items, restaurant_id=restaurant_id,tableheaders=tableheaders)


@app.route('/restaurants/<int:restaurant_id>/new', methods=['GET', 'POST'])
def newMenuItem(restaurant_id):

    if request.method == 'POST':
        form=request.form
        if form['name']=='' or form['price'] =='' or form['course']=='' :
            flash('Error , fill the name , price ,course fields')
            return render_template('newmenuitem.html', restaurant=session.query(Restaurant).filter_by(id=restaurant_id).one())
    	Price="$"
    	Price+=request.form['price']
        newItem = MenuItem(name=request.form['name'], description=request.form[
                           'description'], price=Price, course=request.form['course'], restaurant_id=restaurant_id)
        session.add(newItem)
        session.commit()
        flash("new menu item created!")
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    else:
        return render_template('newmenuitem.html', restaurant=session.query(Restaurant).filter_by(id=restaurant_id).one())


@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit',
           methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
    editedItem=session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
    	editedItem.name=request.form['name']
    	editedItem.price=request.form['price']
    	editedItem.description=request.form['description']
    	editedItem.course=request.form['course']
        session.commit()
        flash("Menu Item has been edited")
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    else:
        return render_template(
            'editmenuitem.html', restaurant_id=restaurant_id, item=editedItem)


# DELETE MENU ITEM SOLUTION
@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete',
           methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
    itemToDelete = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash("Menu Item has been deleted")
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    else:
        return render_template('deletemenuitem.html',restaurant_id=restaurant_id, item=itemToDelete)

@app.route('/restaurants/search-item',methods=['POST'])
def searchItem():
    searchfor=request.form['search']
    searchfor="%"+searchfor+"%"
    items=session.query(MenuItem).filter(MenuItem.name.like(searchfor))
    restaurants=[]
    for i in items:
        restaurants.append(session.query(Restaurant).filter_by(id=i.restaurant_id).one())
    return render_template('search-result.html',items=items,restaurants=restaurants,size=len(restaurants))

#Json requests
@app.route('/restaurants/JSON')
def restaurantsJSON():
    restaurants=session.query(Restaurant).order_by(Restaurant.name).all()
    return jsonify(restaurants=[restaurant.serialize for restaurant in restaurants])
@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON/')
@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/JSON/')
def menuItemJson(restaurant_id,menu_id):
    item = session.query(MenuItem).filter_by(id=menu_id).one()
    return jsonify(menuItem=[item.serialize])


@app.route('/restaurants/<int:restaurant_id>/menu/JSON/')
@app.route('/restaurants/<int:restaurant_id>/JSON/')
def restaurantmenuJson(restaurant_id):
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id)
    return jsonify(menuItems=[i.serialize for i in items])
## end json requests

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
