def product_to_dict(product):
    return {
        "id": product.slug,
        "slug": product.slug,
        "name": product.name,
        "category": product.category,
        "type": product.type,
        "description": product.description,
        "details": product.details,
        "specifications": product.specifications,
        "compatibility": getattr(product, "compatibility", ""),
        "price": product.price,
        "rating": product.rating,
        "tag": product.tag,
        "image_class": product.image_class,
        "image": product.image_url,
        "is_spare": product.category == "spares",
    }
