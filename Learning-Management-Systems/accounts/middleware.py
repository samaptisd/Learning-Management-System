from django.utils.deprecation import MiddlewareMixin
from django.utils.timezone import now
from .models import UserActivityLog

class UserActivityLogMiddleware(MiddlewareMixin):
    """ Middleware to track the duration of user activity on each page """

    def process_request(self, request):
        """ Log the new page visit and update previous page visit's end_time & duration """
        if request.user.is_authenticated:
            current_url = request.build_absolute_uri()
            
            # Get the last page visit that has no end_time
            last_log = UserActivityLog.objects.filter(
                user=request.user, 
                end_time__isnull=True
            ).order_by('-start_time').first()

            # If user is visiting a new page, update the last log's end_time and duration
            if last_log and last_log.url != current_url:
                last_log.end_time = now()
                last_log.duration = last_log.end_time - last_log.start_time
                last_log.save()

            # Create a new log entry for the new page visit
            UserActivityLog.objects.create(
                user=request.user,
                action=f"Visited {request.path}",
                url=current_url,
                method=request.method,
                start_time=now(),
            )

    def process_response(self, request, response):
        """ Ensure the last request gets updated when the user leaves the site """
        if request.user.is_authenticated:
            try:
                # Get the last log entry for the current page
                last_log = UserActivityLog.objects.filter(
                    user=request.user,
                    url=request.build_absolute_uri(),
                    end_time__isnull=True
                ).order_by('-start_time').first()

                if last_log:
                    last_log.end_time = now()
                    last_log.duration = last_log.end_time - last_log.start_time
                    last_log.save()
            except Exception as e:
                print(f"Error updating user activity log: {e}")

        return response
