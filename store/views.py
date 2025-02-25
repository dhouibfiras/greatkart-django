from django.shortcuts import render, get_object_or_404, HttpResponse
from store.models import Product
from carts.models import CartItem
from carts.views import _cart_id
from category.models import Category
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q


def store(request, category_slug=None):
    categories = None
    products = None

    if category_slug != None:  # si un filtre categorie est choisi
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
        paginator = Paginator(products, 1)
        page = request.GET.get("page")  # capturer le numero de la page en cours
        paged_products = paginator.get_page(page)
        product_count = products.count()
    else:  # si aucun filtre de categorie n'est choisi
        products = Product.objects.all().filter(is_available=True).order_by("id")
        paginator = Paginator(products, 3)
        page = request.GET.get("page")  # capturer le numero de la page en cours
        paged_products = paginator.get_page(page)
        product_count = products.count()

    context = {
        "products": paged_products,
        "product_count": product_count,
    }
    return render(request, "store/store.html", context)


def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(
            category__slug=category_slug, slug=product_slug
        )
        in_cart = CartItem.objects.filter(
            cart__cart_id=_cart_id(request), product=single_product
        ).exists()  # Si la variable existe, retourne True, sinon False

    except Exception as e:
        raise e

    context = {"single_product": single_product, "in_cart": in_cart}
    return render(request, "store/product_detail.html", context)


def search(request):
    if "keyword" in request.GET:  # keyword est le nom du champ search dans le template
        keyword = request.GET.get("keyword")
        if keyword:  # si keyword n'est pas blank
            products = Product.objects.order_by("created_date").filter(
                Q(description__icontains=keyword) | Q(product_name__icontains=keyword)
            )
            # Q pour chercher dans la description et le titre, | pour operateur or
            # icontains va chercher dans la description et le titre du produit
            product_count = products.count()
            context = {"products": products, "product_count": product_count}
        else:  # si keyword est vide
            context = {}
    return render(request, "store/store.html", context)
