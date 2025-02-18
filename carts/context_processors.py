from .models import Cart, CartItem
from carts.views import _cart_id


def counter(request):
    cart_count = 0
    # si on est dans l'administration, on ne modifie rien
    if "admin" in request.path:
        return {}
    # on peut aussi utiliser ce code:
    # if request.user.is_admin or is_staff or is_superuser
    else:
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart)
            for cart_item in cart_items:
                cart_count += cart_item.quantity
        except Cart.DoesNotExist:
            cart_count = 0
    return dict(cart_count=cart_count)
