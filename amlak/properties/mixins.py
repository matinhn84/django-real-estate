from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden


class UserOwnedObjectsMixin(LoginRequiredMixin):

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_superuser:
            return queryset
        return queryset.filter(user=self.request.user)



class LimitFieldsMixin:

    limited_fields = ['user', 'is_approved']

    def get_form_class(self):
 
        form_class = super().get_form_class()
        user = self.request.user

        if not user.is_superuser and self.limited_fields:
            class LimitedFieldsForm(form_class):
                class Meta(form_class.Meta):
                    fields = self.limited_fields

            return LimitedFieldsForm

        return form_class

    def dispatch(self, request, *args, **kwargs):
        """
        Additional permission checks (if needed).
        """
        if not request.user.is_authenticated:
            return HttpResponseForbidden("You are not authorized to access this page.")
        return super().dispatch(request, *args, **kwargs)
