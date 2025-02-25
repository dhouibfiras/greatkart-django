from django import forms
from .models import Account


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "Enter Password", "class": "form-control"}
        )
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "Confirm Password", "class": "form-control"}
        )
    )

    class Meta:
        model = Account
        fields = [
            "first_name",
            "last_name",
            "phone_number",
            "email",
            "password",
        ]

    # on ne peut pas ajouter class css ou placeholder pour nos fields dans le template car ils sont en {{}} et non plus en html
    # donc on doit le faire depuis le modèle
    # au lieu de le faire pour chaque field comme pour password ou confirm_password, on surcharge la fonction __init__ pour l'automatiser
    # password et confirm_password ne sont pas des fields du modèle Account mais ont été ajoutés au formulaire, il faut donc ajouter leurs attrs en dehors de la fonction __init__
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        # Définir les placeholder
        self.fields["first_name"].widget.attrs["placeholder"] = "Enter First Name"
        self.fields["last_name"].widget.attrs["placeholder"] = "Enter  Phone Number"
        self.fields["email"].widget.attrs["placeholder"] = "Enter Email"
        # Définir la class css
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"
            # form-control était la class css de l'input de Bootsrap que nous avons remplacé par nos fields

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Passwords does not match!")
