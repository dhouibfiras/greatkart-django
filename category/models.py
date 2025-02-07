from django.db import models
from django.urls import reverse


class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.CharField(max_length=255, blank=True)
    cat_image = models.ImageField(upload_to="photos/categories", blank=True)
    # upload: dans quel dossier l'image va etre stockée

    class Meta:
        # Pour corriger l'ajout automatique de S au nom du model dans l'administration, car Django ajoute automatiquement un s à la fin du nom du modele "Categorys" et c'est une mauvaise orthographe
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    # fonction qui retourne l'url de categorie
    def get_url(self):
        return reverse("products_by_category", args=[self.slug])

    def __str__(self):
        return self.category_name
