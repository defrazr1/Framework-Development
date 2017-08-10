from flask import Flask , render_template, request, redirect, url_for, flash, jsonify
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Restaurant, Base, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

'''
###API Endpoints###
'''
@app.route('/restaurants/JSON/')
def showRestaurantsJSON():
    restaurants = session.query(Restaurant).all()
    return jsonify(Restaurants=[r.serialize for r in restaurants])

@app.route('/restaurants/<int:restaurant_id>/menu/JSON/')
def showMenuJSON(restaurant_id):
    restaurantMenu = session.query(MenuItem).filter_by(restaurant_id = restaurant_id).all()
    return jsonify(MenuItems = [m.serialize for m in restaurantMenu])

@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON/')
def showItemJSON(restaurant_id, menu_id):
    item = session.query(MenuItem).filter_by(id = menu_id).one()
    return jsonify(MenuItem = [item.serialize])

'''
###Restaurant Routing and CRUD functinality###
'''
@app.route('/')
@app.route('/restaurants/')
def showRestaurants():
    restaurants = session.query(Restaurant).all()
    return render_template('restaurants.html', restaurants = restaurants)

@app.route('/restaurants/new/', methods = ['GET', 'POST'])
def newRestaurant():
    if request.method == 'POST':
        addRestaurant = Restaurant(name = request.form['name'])
        session.add(addRestaurant)
        session.commit()
        flash(("New restaurant, %s, created!") % (addRestaurant.name))
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('newRestaurant.html')

@app.route('/restaurants/<int:restaurant_id>/edit/', methods = ['GET', 'POST'])
def editRestaurant(restaurant_id):
    editedRestaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    editedRestaurantOld = editedRestaurant.name
    if request.method == 'POST':
        if request.form['name']:
            editedRestaurant.name = request.form['name']

        session.add(editedRestaurant)
        session.commit()
        flash(("%s has been renamed to %s") % (editedRestaurantOld, editedRestaurant.name))
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('editRestaurant.html', restaurant = editedRestaurant)

@app.route('/restaurants/<int:restaurant_id>/delete/', methods = ['GET', 'POST'])
def deleteRestaurant(restaurant_id):
    restaurantToDelete = session.query(Restaurant).filter_by(id = restaurant_id).one()
    if request.method == 'POST':
        session.delete(restaurantToDelete)
        session.commit()
        flash(("%s has been removed") % (restaurantToDelete.name))
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('deleteRestaurant.html', restaurant = restaurantToDelete)

'''
###Menu Routing and CRUD functinality###
'''
@app.route('/restaurants/<int:restaurant_id>/')
@app.route('/restaurants/<int:restaurant_id>/menu/')
def showMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    menuItems = session.query(MenuItem).filter_by(restaurant_id = restaurant_id).all()
    return render_template('menu.html', restaurant = restaurant, items = menuItems)

@app.route('/restaurants/<int:restaurant_id>/menu/new/', methods = ['GET', 'POST'])
def newMenuItem(restaurant_id):
    if request.method == 'POST':
        if request.form['name']:
            itemName = request.form['name']

        if request.form['description']:
            itemDescription = request.form['description']

        if request.form['price']:
            itemPrice = (("$%s") % (request.form['price']))

        newItem = MenuItem(
            name = itemName,
            price = itemPrice,
            description = itemDescription,
            restaurant_id = restaurant_id)

        session.add(newItem)
        session.commit()
        flash(("New menu item, %s, created!") % (newItem.name))
        return redirect(url_for('showMenu', restaurant_id = restaurant_id))
    else:
        return render_template('newMenuItem.html', restaurant_id = restaurant_id)

@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/edit/', methods = ['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
    editedItem = session.query(MenuItem).filter_by(id = menu_id).one()
    editedItemOldName = editedItem.name
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        session.add(editedItem)
        session.commit()
        flash(("%s has been renamed to %s") % (editedItemOldName, editedItem.name))
        return redirect(url_for('showMenu', restaurant_id = restaurant_id))
    else:
        return render_template('editMenuItem.html', restaurant_id = restaurant_id,
                                menu_id = menu_id, item = editedItem)

@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/delete/', methods = ['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
    itemToDelete = session.query(MenuItem).filter_by(id = menu_id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash(("%s has been DELETED!") % (itemToDelete.name))
        return redirect(url_for('showMenu', restaurant_id = restaurant_id))
    else:
        return render_template('deleteMenuItem.html',
                                restaurant_id = restaurant_id,
                                menu_id = menu_id,
                                item = itemToDelete)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
