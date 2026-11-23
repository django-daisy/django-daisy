"""Permission-aware search across the models registered on a Daisy admin site."""
from django.contrib.admin.utils import quote
from django.urls import NoReverseMatch, reverse
from django.utils.translation import gettext as _


def search(site, request, config):
    term = request.GET.get('q', '').strip()[:200]
    if len(term) < 2:
        return []
    needle = term.casefold()
    enabled_models = {label.lower() for label in config.get('models', [])}
    limit = max(1, min(int(config.get('limit_per_model', 5)), 20))
    results = []
    for app in site.get_app_list(request):
        for item in app['models']:
            model = next((model for model in site._registry
                          if model._meta.app_label == app['app_label']
                          and model._meta.object_name == item['object_name']), None)
            if model is None:
                continue
            model_admin = site._registry[model]
            label = str(item['name'])
            app_name = str(app['name'])
            model_matches = needle in label.casefold() or needle in app_name.casefold()
            if model_matches and item.get('admin_url'):
                results.append({'group': str(_('Pages')), 'label': label,
                                'description': app_name, 'url': item['admin_url']})
            action = str(_('Add %(name)s') % {'name': model._meta.verbose_name})
            if item.get('add_url') and (needle in action.casefold() or model_matches):
                results.append({'group': str(_('Actions')), 'label': action,
                                'description': app_name, 'url': item['add_url']})
            if (model._meta.label_lower not in enabled_models
                    or not item.get('admin_url')
                    or not model_admin.has_view_or_change_permission(request)
                    or not model_admin.get_search_fields(request)):
                continue
            queryset = model_admin.get_queryset(request)
            queryset, may_have_duplicates = model_admin.get_search_results(request, queryset, term)
            if may_have_duplicates:
                queryset = queryset.distinct()
            # Bound work even when object-level permissions exclude some matches.
            for obj in queryset[:limit * 10]:
                if not model_admin.has_view_or_change_permission(request, obj):
                    continue
                try:
                    url = reverse('%s:%s_%s_change' % (site.name, model._meta.app_label,
                                                        model._meta.model_name),
                                  args=[quote(obj.pk)], current_app=site.name)
                except NoReverseMatch:
                    continue
                results.append({'group': label, 'label': str(obj),
                                'description': app_name, 'url': url})
                limit -= 1
                if not limit:
                    break
            limit = max(1, min(int(config.get('limit_per_model', 5)), 20))
    # Keep each result category together while preserving the site's model order.
    groups = {}
    for result in results:
        groups.setdefault(result['group'], []).append(result)
    return [result for group in groups.values() for result in group]
