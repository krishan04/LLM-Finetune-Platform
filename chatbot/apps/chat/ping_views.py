from django.http import JsonResponse
from django.db import connection


def ping(request):
    """
    Lightweight health check endpoint.
    - UptimeRobot hits this every 10 minutes to prevent Render spin-down.
    - Also runs a cheap DB query so Supabase stays active.
    - Returns 200 with basic status info.
    """
    db_ok = False
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_ok = True
    except Exception:
        pass

    status = "ok" if db_ok else "degraded"
    return JsonResponse({"status": status, "db": db_ok}, status=200)