"""Data for the admin dashboard. Projects may override the site hooks."""
from datetime import timedelta

from django.core.exceptions import FieldDoesNotExist
from django.db.models import BooleanField, Count, DateField, DateTimeField, Q
from django.db.models.functions import TruncDate
from django.urls import NoReverseMatch, reverse
from django.utils import timezone
from django.utils.formats import date_format
from django.utils.translation import gettext_lazy as _



def get_user_overview(site, request, config, start, today):
    """Use the registered user admin's permission and scoped queryset."""
    from django.contrib.auth import get_user_model

    model = get_user_model()
    model_admin = site._registry.get(model)
    if not model_admin or not model_admin.has_view_or_change_permission(request):
        return [], None
    if not config.get('show_user_stats', True) and not config.get('show_user_chart', True):
        return [], None
    users = model_admin.get_queryset(request)

    def field(name):
        try:
            return model._meta.get_field(name)
        except FieldDoesNotExist:
            return None

    stats = []
    if config.get('show_user_stats', True):
        aggregates = {'total': Count('pk', distinct=True)}
        if isinstance(field('is_active'), BooleanField):
            aggregates['active'] = Count('pk', filter=Q(is_active=True), distinct=True)
        if isinstance(field('is_staff'), BooleanField):
            aggregates['staff'] = Count('pk', filter=Q(is_staff=True), distinct=True)
        totals = users.aggregate(**aggregates)
        stats.append({'label': _('Total users'), 'value': totals['total'], 'icon': 'fa-solid fa-users'})
        if 'active' in totals:
            stats.append({'label': _('Active users'), 'value': totals['active'], 'icon': 'fa-solid fa-user-check'})
        if 'staff' in totals:
            stats.append({'label': _('Staff accounts'), 'value': totals['staff'], 'icon': 'fa-solid fa-user-shield'})

    joined_field = config.get('user_date_field', 'date_joined')
    date_field = field(joined_field)
    chart = None
    if config.get('show_user_chart', True) and isinstance(date_field, DateField) and date_field.concrete:
        if isinstance(date_field, DateTimeField):
            lookup = joined_field + '__date'
            day_expression = TruncDate(joined_field)
        else:
            from django.db.models import F
            lookup = joined_field
            day_expression = F(joined_field)
        rows = (users.filter(**{lookup + '__gte': start, lookup + '__lte': today})
                .annotate(dashboard_day=day_expression).values('dashboard_day')
                .annotate(total=Count('pk', distinct=True)))
        counts = {row['dashboard_day']: row['total'] for row in rows}
        points = []
        for offset in range((today - start).days + 1):
            day = start + timedelta(days=offset)
            points.append({'label': date_format(day, 'SHORT_DATE_FORMAT'), 'count': counts.get(day, 0)})
        chart = {'points': points, 'max': max(counts.values(), default=0) or 1}
    return stats, chart


def build_dashboard(site, request, app_list):
    from django.contrib.admin.models import ADDITION, CHANGE, DELETION, LogEntry

    config = site.get_dashboard_config(request)
    days = max(1, min(int(config.get('activity_days', 7)), 31))
    limit = max(0, int(config.get('history_limit', 10)))
    # Match Django's recent actions: non-superusers see only their own entries.
    logs = site.get_log_entries(request)
    if not request.user.is_superuser:
        logs = logs.filter(user=request.user)
    now = timezone.now()
    today = timezone.localtime(now).date() if timezone.is_aware(now) else now.date()
    start = today - timedelta(days=days - 1)
    recent = logs.filter(action_time__date__gte=start, action_time__date__lte=today)
    counts = {}
    for row in recent.annotate(day=TruncDate('action_time')).values('day', 'action_flag').annotate(total=Count('pk')):
        counts.setdefault(row['day'], {})[row['action_flag']] = row['total']
    maximum = max((sum(day.values()) for day in counts.values()), default=0)
    chart = []
    for offset in range(days):
        day = start + timedelta(days=offset)
        values = counts.get(day, {})
        additions = values.get(ADDITION, 0)
        changes = values.get(CHANGE, 0)
        deletions = values.get(DELETION, 0)
        count = additions + changes + deletions
        chart.append({
            'label': date_format(day, 'SHORT_DATE_FORMAT'), 'count': count,
            'additions': additions, 'changes': changes, 'deletions': deletions,
        })
    totals = {row['action_flag']: row['total'] for row in recent.values('action_flag').annotate(total=Count('pk'))}
    stats = [
        {'label': _('Activity'), 'value': sum(totals.values()), 'icon': 'fa-solid fa-chart-line'},
        {'label': _('Additions'), 'value': totals.get(ADDITION, 0), 'icon': 'fa-solid fa-plus'},
        {'label': _('Changes'), 'value': totals.get(CHANGE, 0), 'icon': 'fa-solid fa-pen'},
        {'label': _('Deletions'), 'value': totals.get(DELETION, 0), 'icon': 'fa-solid fa-trash'},
    ]
    user_stats, user_chart = get_user_overview(site, request, config, start, today)
    if user_stats:
        stats = (user_stats + stats)[:4]
    actions = []
    for app in app_list:
        for model in app['models']:
            if model.get('add_url'):
                actions.append({'label': _('Add %(name)s') % {'name': model['name']}, 'url': model['add_url'], 'icon': 'fa-solid fa-plus'})
    history = []
    for entry in logs[:limit]:
        url = None
        model = entry.content_type.model_class() if entry.content_type else None
        model_admin = site._registry.get(model)
        if model_admin and not entry.is_deletion() and model_admin.has_view_or_change_permission(request):
            try:
                url = reverse(f'{site.name}:{model._meta.app_label}_{model._meta.model_name}_change', args=[entry.object_id])
            except NoReverseMatch:
                pass
        history.append({'entry': entry, 'url': url})
    log_url = None
    log_admin = site._registry.get(LogEntry)
    if request.user.is_superuser and log_admin and log_admin.has_view_permission(request):
        try:
            log_url = reverse(f'{site.name}:admin_logentry_changelist')
        except NoReverseMatch:
            pass
    return {
        'config': config,
        'days': days,
        'stats': site.get_dashboard_stats(request, stats),
        'actions': site.get_dashboard_actions(request, actions[:6]),
        'chart': chart,
        'user_chart': user_chart,
        'chart_max': maximum or 1,
        'history': history,
        'log_url': log_url,
    }
