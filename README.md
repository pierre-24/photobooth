# `photobooth`

Un truc en *quick and dirty* pour stocker les infos des gens afin d'ensuite leur envoyer leur photo.


```bash
# create virtualenv
python3 -m venv venv
source venv/bin/activate

# install dependencies
pip3 install --upgrade -r requirements.txt

# init
export FLASK_APP=photobooth
flask init
```

N'oubliez pas de créer un `settings_prod.py`

```python
from photobooth import settings

# config interne
settings.APP_CONFIG.update({
    
    # Clé secrète pour Flask
    'SECRET_KEY': '****',
    
    # Mot de passe d'administration
    'PASSWORD': '****',
    
    # Clé secrète reCAPTCHA (si utilisé)
    'RECAPTCHA_SECRET_KEY': '***'
})

# info pour pages
settings.WEBPAGE_INFO.update({
    # clé publique FontAwesome
    'fa_kit': '***',
    
    # clé publique recaptcha
    'recaptcha_public_key': '****'
})
```