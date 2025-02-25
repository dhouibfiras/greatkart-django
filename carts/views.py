from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from .models import Cart, CartItem
from store.models import Product, Variation
from django.core.exceptions import ObjectDoesNotExist


def _cart_id(request):  # underscore au début pour rendre la fonction privée
    # pour récupérer session_key (dans cookies)
    actual_session = request.session.session_key
    if not actual_session:  # si pas de session, créer une
        actual_session = request.session.create()
    return actual_session


def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    product_variations = []
    if request.method == "POST":
        # Pour chaque élément envoyé dans la requete POST (color, size ou d'autres)
        for item in request.POST:  # expemple pour color
            key = item  # key = color
            value = request.POST[key]  # value = blue (request.POST[color])
            # ajouter une instance de Variation avec les infos du produit
            try:
                variation = Variation.objects.get(
                    product=product,  # Jean
                    variation_category__iexact=key,  # variation_category = color
                    variation_value__iexact=value,  # variation_value = blue
                )
                # __iexact va ignorer si miniscule ou majuscule
                # pour chaque item de la requete POST il ya une variation (color, size ou d'autres)
                # remplir une liste avec toutes les variations du produit (variation color, variation size...)
                product_variations.append(variation)
            except:
                pass

    # récupérer la session actuelle en utilisant le cart_id récupéré grace à la fonction _cart_id, sinon crée une nouvelle session
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))

    # Vérifier si CartItem existe déjà (si le produit est déjà dans le panier)
    is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
    if is_cart_item_exists:
        # récupérer tous les cartitems du meme produit (mais avec différentes variations)
        cart_items = CartItem.objects.filter(product=product, cart=cart)
        existing_variations_list = []
        ids = []
        # pour chaque cart_item des cart_items du meme produit
        for cart_item in cart_items:
            # récupère les variations du produit (exp color=blue, size=M)
            existing_variations = cart_item.variations.all()
            # liste des variations du meme produit exp (color=blue, size=M), color=red, size=L)
            existing_variations_list.append(list(existing_variations))
            # liste des ids de chaque cart_item du meme produit
            ids.append(cart_item.id)

        # si les variations du produit à ajouter existent déjà dans le panier
        if product_variations in existing_variations_list:
            # augmenter la quantité du produit
            index = existing_variations_list.index(product_variations)
            cart_item_id = ids[index]
            item = CartItem.objects.get(product=product, id=cart_item_id)
            item.quantity += 1
            item.save()
        # sinon créer un nouveau cartitem
        else:
            item = CartItem.objects.create(product=product, quantity=1, cart=cart)
            # vérifier si la liste product_variations n'est pas vide
            if len(product_variations) > 0:
                item.variations.clear()
                item.variations.add(*product_variations)
                # * pour etre sur d'ajouter touts les product_variations
            item.save()
    # si le produit n'est pas déjà dans le panier, créer un nouveau cartitem
    else:
        cart_item = CartItem.objects.create(product=product, quantity=1, cart=cart)
        if len(product_variations) > 0:
            cart_item.variations.clear()
            cart_item.variations.add(*product_variations)
        cart_item.save()
    return redirect("cart")


def remove_cart(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect("cart")


def remove_cart_item(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect("cart")


def cart(request, total=0, quantity=0, tax=0, grand_total=0, cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            # valeur de tout le panier
            total += cart_item.product.price * cart_item.quantity
            # quantité de touts les articles du panier
            quantity += cart_item.quantity
        tax = (2 * total) / 100  # 2 % de taxe
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass
    context = {
        "total": total,
        "quantity": quantity,
        "cart_items": cart_items,
        "tax": tax,
        "grand_total": grand_total,
    }
    return render(request, "store/cart.html", context)
