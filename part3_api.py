@app.get("/api/companies/{company_id}/alerts/low-stock")
def get_low_stock_alerts(company_id: int, db: Session):
    alerts = []
    recent_days = 30
    cutoff_date = datetime.utcnow() - timedelta(days=recent_days)

    # Fetch inventory items for the company (per warehouse)
    inventory_items = (
        db.query(Inventory, Product, Warehouse)
        .join(Product, Inventory.product_id == Product.id)
        .join(Warehouse, Inventory.warehouse_id == Warehouse.id)
        .filter(Product.company_id == company_id)
        .all()
    )

    for inventory, product, warehouse in inventory_items:

        # Low stock check per warehouse
        if inventory.quantity >= product.min_count:
            continue

        # Recent sales activity check
        recent_sale = (
            db.query(InventoryLog)
            .filter(
                InventoryLog.inventory_id == inventory.id,
                InventoryLog.change_amount < 0,
                InventoryLog.created_at >= cutoff_date
            )
            .first()
        )

        if not recent_sale:
            continue  # Skip items with no recent sales

        # Calculate approximate days until stockout
        avg_daily_usage = abs(recent_sale.change_amount) / recent_days
        days_until_stockout = (
            int(inventory.quantity / avg_daily_usage)
            if avg_daily_usage > 0 else None
        )

        # 4. Fetch supplier details (if available)
        supplier = (
            db.query(Supplier)
            .join(ProductSupplier)
            .filter(ProductSupplier.product_id == product.id)
            .first()
        )

        alerts.append({
            "product_id": product.id,
            "product_name": product.name,
            "sku": product.sku,
            "warehouse_id": warehouse.id,
            "warehouse_name": warehouse.name,
            "current_stock": inventory.quantity,
            "threshold": product.min_count,
            "days_until_stockout": days_until_stockout,
            "supplier": {
                "id": supplier.id if supplier else None,
                "name": supplier.name if supplier else None,
                "contact_email": supplier.email if supplier else None
            }
        })

    return {
        "alerts": alerts,
        "total_alerts": len(alerts)
    }
