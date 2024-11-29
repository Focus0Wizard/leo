from flask import Flask, request, jsonify, Response, render_template, redirect, url_for, session, request
from flask_pymongo import PyMongo
from bson import json_util
from bson.objectid import ObjectId

app = Flask(__name__)
app.config['MONGO_URI'] = "mongodb+srv://jhonnramirez:admin123@clusterpjbd.1goyjmu.mongodb.net/DBStore?retryWrites=true&w=majority&appName=ClusterPjBD"
mongo = PyMongo(app, uri=app.config['MONGO_URI'])

app.secret_key = '123' 

@app.route('/')
def index():
    instruments = mongo.db.Instruments.find()
    return render_template('index.html', instruments=instruments)

@app.route('/pago_exitoso')
def pago_exitoso():
    return render_template('pago_exitoso.html')

@app.route('/viewProducts')
def viewProducts():
    instruments = mongo.db.Instruments.find()
    return render_template('viewProducts.html', instruments=instruments)


""" Clients """
@app.route('/Clients', methods=['POST'])
def create_client():
    try:
        # Receiving data
        username = request.json['username']
        email = request.json['email']
        address = request.json['address']
        credit_card = request.json['credit_card']
        
        if username and email and address and credit_card:
            id = mongo.db.Clients.insert_one(
            {
                'username': username, 
                'email': email, 
                'address': address, 
                'credit_card': credit_card
            })
            response = {
                'id': str(id),
                'username': username,
                'email': email,
                'address': address,
                'credit_card': credit_card
            }
            return response
        else:
            return not_found() 
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/Clients', methods=['GET'])
def get_clients():
    try:
        clients = mongo.db.Clients.find()
        response = json_util.dumps(clients)
        return Response(response, mimetype="application/json")
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/Clients/<id>', methods=['GET'])
def get_client(id): 
    try:
        user = mongo.db.Clients.find_one({'_id': ObjectId(id)})
        response = json_util.dumps(user) 
        return Response(response, mimetype='application/json')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/Clients/<id>', methods=['DELETE'])
def delete_client(id):
    try:    
        mongo.db.Clients.delete_one({'_id': ObjectId(id)})
        response = jsonify({'message': 'User ' + id + 'was deleted successfully'})
        return response 
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/Clients/<id>', methods=['PUT'])
def update_client(id):
    try:
        username = request.json['username']
        email = request.json['email']
        
        if username and email:
            mongo.db.Clients.update_one({'_id': ObjectId(id)}, {'$set': {
                'username': username,
                'email': email
            }})
            response = jsonify({'message': ' User ' + id + ' was updated successfully '})
            return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500

""" Categories """
@app.route('/Category', methods=['POST'])
def create_category():
    try:
        name = request.json['name']
        description = request.json['description']

        if name and description:
            id = mongo.db.Category.insert_one(
                {'name': name, 'description': description}
            )
            response = {
                'id': str(id),
                'name': name,
                'description': description
            }
            return response
        else:
            return not_found()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/Category', methods=['GET'])
def get_categories():
    try:
        categories = mongo.db.Category.find()
        response = json_util.dumps(categories)
        return Response(response, mimetype="application/json")
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/Category/<id>', methods=['GET'])
def get_category(id):
    try:
        category = mongo.db.Category.find_one({'_id': ObjectId(id)})
        response = json_util.dumps(category)
        return Response(response, mimetype='application/json')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/Category/<id>', methods=['DELETE'])
def delete_category(id):
    try:
        mongo.db.Category.delete_one({'_id': ObjectId(id)})
        response = jsonify({'message': 'Category ' + id + ' was deleted successfully'})
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/Category/<id>', methods=['PUT'])
def update_category(id):
    try:
        name = request.json['name']
        description = request.json['description']
        if name and description:
            mongo.db.Category.update_one({'_id': ObjectId(id)}, {'$set':
                {
                    'name': name,
                    'description': description
                }
            })
        response = jsonify({'message': 'Category ' + id + ' was updated successfully '})
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500


""" Instruments """
@app.route('/Instrument', methods=['POST'])
def create_instrument():
    try:
        # Receiving data
        name = request.json['name']
        brand = request.json['brand']
        price = request.json['price']
        category_id = request.json['category_id']
        stock = request.json['stock']
        description = request.json['description']

        category_id = ObjectId(category_id)
        
        if name and brand and price and category_id and stock and description:
            id = mongo.db.Instrument.insert_one(
                {'name': name, 'brand': brand, 'price': price, 'category_id': category_id, 'stock': stock, 'description': description}
            )
            response = {
                'id': str(id),
                'name': name,
                'brand': brand,
                'price': price,
                'category_id': str(category_id),
                'stock': stock,
                'description': description
            }
            return response
        else:
            return not_found()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/Instrument', methods=['GET'])
def get_Instruments():
    try:
        instruments = mongo.db.Instrument.aggregate(
            [
                {
                    '$lookup':{
                        'from': 'Category',
                        'localField': 'category_id',
                        'foreignField': '_id',
                        'as': 'category'
                    }
                },
                {
                    '$unwind': '$category'
                }
            ]
        )
        response = json_util.dumps(instruments)
        return Response(response, mimetype="application/json")
    except Exception as e:
        return jsonify({'error': str(e)}), 500   

@app.route('/Instrument/<id>', methods=['GET'])
def get_instrument(id):
    try:
        instrument = mongo.db.Instrument.aggregate(
        [
                {
                    '$match': {'_id': ObjectId(id)}
                },
                {
                    '$lookup': {
                        'from': 'Category',
                        'localField': 'category_id',
                        'foreignField': '_id',
                        'as': 'category'
                    }
                },
                {
                    '$unwind': {
                        'path': '$category',
                        'preserveNullAndEmptyArrays': True
                    }
                }
            ]
        )
        instrument = list(instrument)  # Convert cursor to list
        if instrument:
            response = json_util.dumps(instrument[0])
        else:
            response = jsonify({'error': 'Instrument not found'}), 404
        return Response(response, mimetype="application/json")
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/Instrument/<id>', methods=['DELETE'])
def delete_instrument(id):
    try:    
        mongo.db.Instrument.delete_one({'_id': ObjectId(id)})
        response = jsonify({'message': 'Instrument ' + id + 'was deleted successfully'})
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/Instrument/<id>', methods=['PUT'])
def update_instrument(id):
    try:
        name = request.json['name']
        brand = request.json['brand']
        price = request.json['price']
        category_id = request.json['category_id']
        stock = request.json['stock']
        description = request.json['description']

        category_id = ObjectId(category_id)

        if name and brand and price and category_id and stock and description:
            mongo.db.Instruments.update_one({'_id': ObjectId(id)}, {'$set':
                {
                    'name': name,
                    'brand': brand,
                    'price': price,
                    'category_id': category_id,
                    'stock': stock,
                    'description': description
                }
            })
        response = jsonify({'message': ' Instrument ' + id + ' was updated successfully '})
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500

""" Items """
@app.route('/Items', methods=['POST'])
def create_item():
    try:
        # Receiving data
        instrument_id = request.json['instrument_id']
        quantity = request.json['quantity']
        price = request.json['price']
        client_id = request.json['client_id']

        instrument_id = ObjectId(instrument_id)
        client_id = ObjectId(client_id)

        if instrument_id and quantity and price and client_id:
            id = mongo.db.Items.insert_one(
                {'instrument_id': instrument_id, 'quantity': quantity, 'price': price, 'client_id': client_id}
            )
            response = {
                'id': str(id),
                'instrument_id': str(instrument_id),
                'quantity': quantity,
                'price': price,
                'client_id': str(client_id)
            }
            return jsonify(response)
        else:
            return not_found()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/Items', methods=['GET'])
def get_items():
    try:
        items = mongo.db.Items.aggregate(
            [
                {
                    '$lookup': {
                        'from': 'Instrument',  # Nombre de la colección
                        'localField': 'instrument_id',
                        'foreignField': '_id',
                        'as': 'instrument'
                    }
                },
                {
                    '$unwind': '$instrument'
                },
                {
                    '$lookup': {
                        'from': 'Clients',  # Nombre de la colección
                        'localField': 'client_id',
                        'foreignField': '_id',
                        'as': 'client'
                    }
                },
                {
                    '$unwind': '$client'
                } 
            ]
        )
        items
        response = json_util.dumps(items)
        return Response(response, mimetype="application/json")
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/Items/<id>', methods=['GET'])
def get_item(id):
    try:
        item = mongo.db.Items.aggregate(
            [
                {
                    '$match': {'_id': ObjectId(id)}
                },
                {
                    '$lookup': {
                        'from': 'Instrument',  # Nombre de la colección
                        'localField': 'instrument_id',
                        'foreignField': '_id',
                        'as': 'instrument'
                    }
                },
                {
                    '$unwind': '$instrument'
                },
                {
                    '$lookup': {
                        'from': 'Clients',  # Nombre de la colección
                        'localField': 'client_id',
                        'foreignField': '_id',
                        'as': 'client'
                    }
                },
                {
                    '$unwind': '$client'
                }
            ]
        )
        item = list(item)  # Convert cursor to list
        if item:
            response = json_util.dumps(item[0])
        else:
            response = jsonify({'error': 'Item not found'}), 404
        return Response(response, mimetype="application/json")
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/Items/<id>', methods=['DELETE'])
def delete_item(id):
    try:    
        mongo.db.Items.delete_one({'_id': ObjectId(id)})
        response = jsonify({'message': 'Item ' + id + ' was deleted successfully'})
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/Items/<id>', methods=['PUT'])
def update_item(id):
    try:
        instrument_id = request.json['instrument_id']
        quantity = request.json['quantity']
        price = request.json['price']
        client_id = request.json['client_id']

        instrument_id = ObjectId(instrument_id)
        client_id = ObjectId(client_id)

        if instrument_id and quantity and price and client_id:
            mongo.db.Items.update_one({'_id': ObjectId(id)}, {'$set':
                {
                    'instrument_id': instrument_id,
                    'quantity': quantity,
                    'price': price,
                    'client_id': client_id
                }
            })
        response = jsonify({'message': 'Item ' + id + ' was updated successfully'})
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500


#Cart#
@app.route('/add_to_cart/<instrument_id>', methods=['POST'])
def add_to_cart(instrument_id):
    instrumento = mongo.db.Instruments.find_one({"_id": ObjectId(instrument_id)})
    cart_items = {
        'id': str(instrumento['_id']),
        'name': instrumento['name'],
        'price': float(instrumento['price']),
        'image': instrumento['image']
    }

    if 'carts' not in session:
        session['carts'] = []

    session['carts'].append(cart_items)
    session.modified = True
    return redirect(url_for('view_cart'))

@app.route('/cart')
def view_cart():
    cart = session.get('carts', [])
    total = sum(item['price'] for item in cart)
    print(f"Total final: {total}")  # Depuración
    return render_template('cart.html', cart=cart, total=total)

@app.route('/remove_from_cart/<instrument_id>', methods=['POST'])
def remove_from_cart(instrument_id):
    cart = session.get('carts', [])
    cart = [item for item in cart if item['id'] != instrument_id]
    session['carts'] = cart
    session.modified = True
    return redirect(url_for('view_cart'))

@app.errorhandler(404)
def not_found(error = None):
    response = jsonify({
        'message': 'Resource Not Found: ' + request.url,
        'status': 404
    })
    response.status_code = 404
    return response

if __name__=="__main__":
    app.run(debug=True)
