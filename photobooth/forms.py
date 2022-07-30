from flask_wtf import FlaskForm
import wtforms as f


class MainForm(FlaskForm):
    surname = f.StringField(
        'Prénom',
        validators=[
            f.validators.input_required(message='Ce champ est requis'),
            f.validators.Length(min=3, max=100, message='La valeur doit être comprise entre 3 et 100 caractères')
        ])
    name = f.StringField(
        'Nom',
        validators=[
            f.validators.input_required(message='Ce champ est requis'),
            f.validators.Length(min=3, max=100, message='La valeur doit être comprise entre 3 et 100 caractères')
        ])

    email = f.StringField(
        'Adresse e-mail',
        validators=[
            f.validators.input_required(message='Ce champ est requis'),
            f.validators.email(message="Ceci n'est pas une adresse email valide")]
    )

    id_pic = f.IntegerField(
        'Numéro de la photo',
        validators=[
            f.validators.input_required(message='Ce champ est requis'),
            f.validators.number_range(min=0)
        ]
    )

    note = f.StringField('Note')

    gdpr = f.BooleanField(
        'J\'accepte de recevoir, par mail, ma photo.',
        validators=[f.validators.input_required('ce choix est nécessaire')]
    )

    add_to_newsletter = f.BooleanField(
        "Je m'inscris à l'infolettre de l'association Anne-Marie Nihoul (facultatif)",
    )

    submit_button = f.SubmitField("S'inscrire")


class LoginForm(FlaskForm):
    login = f.StringField('Login', validators=[f.validators.InputRequired()])
    password = f.PasswordField('Mot de passe', validators=[f.validators.InputRequired()])
    next = f.HiddenField(default='')

    login_button = f.SubmitField('Login')
