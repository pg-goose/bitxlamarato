from django.contrib.auth.views import LoginView

class RedirectUserView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        user = self.request.user
        if user.is_superuser:
            return '/admin/'
        else:
            return '/alertas/'

class AdminOutbreaksView(LoginRequiredMixin, TemplateView):
    template_name = 'admin_outbreaks.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['outbreaks'] = Outbreak.objects.all()
        return context