from flask.views import View
from flask import Blueprint
import flask

import flask_login
from flask_login import login_required

from photobooth import settings, forms, models, db, limiter, User


class RenderTemplateView(View):
    methods = ['GET']
    template_name = None

    def get_context_data(self, *args, **kwargs):
        # webpage info
        ctx = {}
        ctx.update(**settings.WEBPAGE_INFO)

        return ctx

    def get(self, *args, **kwargs):
        """Handle GET: render template"""

        if not self.template_name:
            raise ValueError('template_name')

        context_data = self.get_context_data(*args, **kwargs)
        return flask.render_template(self.template_name, **context_data)

    def dispatch_request(self, *args, **kwargs):
        if flask.request.method == 'GET':
            return self.get(*args, **kwargs)
        else:
            flask.abort(403)


class FormView(RenderTemplateView):

    methods = ['GET', 'POST']
    form_class = None
    success_url = '/'
    failure_url = '/'
    modal_form = False

    DEBUG = False

    form_kwargs = {}

    def get_form_kwargs(self):
        return self.form_kwargs

    def get_form(self):
        """Return an instance of the form"""
        return self.form_class(**self.get_form_kwargs())

    def get_context_data(self, *args, **kwargs):
        """Insert form in context data"""

        context = super().get_context_data(*args, **kwargs)

        if 'form' not in context:
            context['form'] = kwargs.pop('form', self.get_form())

        return context

    def post(self, *args, **kwargs):
        """Handle POST: validate form."""

        self.url_args = args
        self.url_kwargs = kwargs
        if not self.form_class:
            raise ValueError('form_class')

        form = self.get_form()

        if form.validate_on_submit():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        """If the form is valid, go to the success url"""
        return flask.redirect(self.success_url)

    def form_invalid(self, form):
        """If the form is invalid, go back to the same page with an error"""

        if self.DEBUG:
            print('form is invalid ::')
            for i in form:
                if len(i.errors) != 0:
                    print('-', i, '→', i.errors, '(value is=', i.data, ')')

        if not self.modal_form:
            return self.get(form=form, *self.url_args, **self.url_kwargs)
        else:
            return flask.redirect(self.failure_url)

    def dispatch_request(self, *args, **kwargs):

        if flask.request.method == 'POST':
            return self.post(*args, **kwargs)
        elif flask.request.method == 'GET':
            return self.get(*args, **kwargs)
        else:
            flask.abort(403)


# -- MAIN
bp_main = Blueprint('main', __name__, url_prefix='/')


class IndexView(FormView):
    template_name = 'index.html'
    form_class = forms.MainForm
    decorators = [limiter.limit(settings.REQUEST_LIMIT)]

    def form_valid(self, form):
        print(form.name.data)

        req = models.Request.create(
            form.surname.data,
            form.name.data,
            form.email.data,
            form.id_pic.data,
            form.add_to_newsletter.data,
            form.note.data)

        db.session.add(req)
        db.session.commit()

        flask.flash("Merci, c'est noté !")
        return super().form_valid(form)


bp_main.add_url_rule('/', view_func=IndexView.as_view(name='index'))


# -- ADMIN
bp_admin = Blueprint('admin', __name__, url_prefix='/admin')


class LoginView(FormView):
    form_class = forms.LoginForm
    template_name = 'login.html'
    decorators = [limiter.limit(settings.LOGIN_LIMIT)]

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        ctx['next'] = flask.request.args.get('next', '')
        return ctx

    def dispatch_request(self, *args, **kwargs):

        if flask_login.current_user.is_authenticated:
            flask.flash('Vous êtes déjà connecté', category='error')
            return flask.redirect(flask.request.args.get('next', flask.url_for('visitor.index')))

        return super().dispatch_request(*args, **kwargs)

    def form_valid(self, form):

        if form.login.data != settings.APP_CONFIG['USERNAME'] or form.password.data != settings.APP_CONFIG['PASSWORD']:
            flask.flash('Utilisateur ou mot de passe incorrect', 'error')
            return self.form_invalid(form)

        flask_login.login_user(User(form.login.data))

        next = form.next.data
        self.success_url = flask.url_for('admin.index') if next == '' else next
        return super().form_valid(form)


bp_admin.add_url_rule('/login.html', view_func=LoginView.as_view(name='login'))


@login_required
@bp_admin.route('/logout', endpoint='logout')
def logout():
    flask_login.logout_user()
    flask.flash('Vous êtes déconnecté.')
    return flask.redirect(flask.url_for('main.index'))


# -- Index
class AdminBaseMixin:
    decorators = [login_required]


class AdminIndexView(AdminBaseMixin, RenderTemplateView):
    template_name = 'admin.html'
    decorators = [login_required]

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)

        req = models.Request.query

        ctx['num_requests'] = req.count()
        ctx['num_newsletters'] = req.filter(models.Request.add_to_newsletter.is_(True)).count()
        ctx['requests'] = req.order_by(models.Request.id.desc()).all()

        return ctx


bp_admin.add_url_rule('/index.html', view_func=AdminIndexView.as_view(name='index'))
