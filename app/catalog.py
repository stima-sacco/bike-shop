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
        "image": product.display_image,
        "is_spare": product.category == "spares",
    }


def product_gallery(product):
    images = []
    if product.display_image:
        images.append({"url": product.display_image, "alt": product.name})
    for extra in product.gallery_images.all():
        images.append({"url": extra.image.url, "alt": extra.caption or product.name})
    return images
