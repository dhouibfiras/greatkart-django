from category.models import Category


def menu_links(request):
    links = Category.objects.all()
    return dict(links=links)  # variable links disponible dsns touts les Templates
