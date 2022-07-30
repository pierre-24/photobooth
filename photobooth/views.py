import flask
from flask.views import View
from flask import Blueprint

from photobooth import settings, forms, models, db

bp = Blueprint('main', __name__, url_prefix='/')


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


class IndexView(FormView):
    template_name = 'index.html'
    form_class = forms.MainForm

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


bp.add_url_rule('/', view_func=IndexView.as_view(name='index'))
