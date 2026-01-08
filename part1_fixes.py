@app.route('/api/products', methods=['POST'])
def create_product():
    data = request.get_json() #added get_json here as this method provides explicit validation

    if not data:
        return {"error": "Invalid JSON"}, 400

    #Here I assumed that all fields are given in future we can make it flexible as all the requirements might not be present
    required = ['name', 'sku', 'price', 'warehouse_id', 'initial_quantity']
    for field in required:
        if field not in data:
            return {"error": f"{field} is required"}, 400

    #such errors can happen by mistake
    if data['price'] < 0 or data['initial_quantity'] < 0:
        return {"error": "Price and Quantity cannot be negative"}, 400

    try:
        #Here I assumed that SKU is unique and we added constraints for that in db
        if Product.query.filter_by(sku=data['sku']).first():
            return {"error": "SKU already exists"}, 409

        # In product removed warehouse_id
        product = Product(
            name=data['name'],
            sku=data['sku'],
            price=Decimal(str(data['price'])) # Fix floating point issues
        )
        db.session.add(product)

        #Here flush is used as we needed information created but we must not commit
        db.session.flush()

        #Inventory is created here they both are linked by taking id from product this was missing before
        inventory = Inventory(
            product_id=product.id,
            warehouse_id=data['warehouse_id'],
            quantity=data['initial_quantity']
        )
        db.session.add(inventory)

        #Here we made only one commit to preserve atomicity
        db.session.commit()
        return {"message": "Product created", "product_id": product.id}, 201

    except Exception as e:
        db.session.rollback() #added rollback mechanism
        return {"error": str(e)}, 500 #strictly mentioned error for easy debugging
