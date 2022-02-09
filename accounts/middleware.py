from django.http.response import HttpResponse
from django.utils.deprecation import MiddlewareMixin
from django.urls import resolve, reverse
from django.http import HttpResponseRedirect
from django.conf import settings
from . import views
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken


class LoginRequiredMiddleware(MiddlewareMixin):
    
    """
    Middleware that requires a user to be authenticated to view any page other
    than LOGIN_URL. Exemptions to this requirement can optionally be specified
    in settings by setting a tuple of routes to ignore
    """

    def process_request(self, request):
        assert hasattr(request, 'user'), """
        The Login Required middleware needs to be after AuthenticationMiddleware.
        Also make sure to include the template context_processor:
        'django.contrib.auth.context_processors.auth'."""   

        # current_route_name = resolve(request.path_info).url_name
        # print(current_route_name)
        
        # admin_urls = ['home','profile','attendance','filter_attendance','files','add_files','assets','add_asset',
        #             'leave_tracker','apply_leave','leave','self_travel_request','add_self_travel_request','delete_travel_request',
        #             'self_travel_expense','compensatory_request','add_compensatory_request','employees','add_employee','update_employee',
        #             'delete_employee','snippets','reporting','roles','add_roles','update_role','delete_role'
                    
        #         ]

        # if request.user.is_authenticated:
        #     if not current_route_name in admin_urls:
        #         return HttpResponse('not authorized..')

        # if not request.user.is_authenticated:
            
        #     if not current_route_name in settings.AUTH_EXEMPT_ROUTES:
        #         return HttpResponseRedirect(reverse(settings.AUTH_LOGIN_ROUTE))

        user_id = request.user.id            
        is_allowed_user = True
        # token = request.auth
        token = request.auth
        # print(token)
        try:
            is_blackListed = BlacklistedToken.objects.get(user=user_id, tk=token)
            if is_blackListed:
                is_allowed_user = False
        except BlacklistedToken.DoesNotExist:
            is_allowed_user = True
        return is_allowed_user


    # def process_view(self, request, view_func, view_args, view_kwargs):
    #     # Get the view name as a string
    #     view_name = '.'.join((view_func.__module__, view_func.__name__))

    #     current_route_name = resolve(request.path_info).url_name
    #     # print(current_route_name)
    #     # If the view name is in our exclusion list, exit early
    #     exclusion_set = 'organinzation_files'
    #     if current_route_name == 'organinzation_files':
    #         return HttpResponse('not authorized..')