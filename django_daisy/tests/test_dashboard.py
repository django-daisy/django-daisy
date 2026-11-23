from datetime import timedelta

from django.contrib import admin
from django.contrib.admin.models import ADDITION, CHANGE, LogEntry
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import RequestFactory, TestCase
from django.utils import timezone, translation

from django_daisy.admin import DaisyAdminSite
from django_daisy.dashboard import build_dashboard


class DashboardTests(TestCase):
    def setUp(self):
        self.site = DaisyAdminSite(name='test_admin')
        self.user = get_user_model().objects.create_user(username='dashboard-user', is_staff=True)
        self.other = get_user_model().objects.create_user(username='other', is_staff=True)
        self.request = RequestFactory().get('/admin/')
        self.request.user = self.user
        self.content_type = ContentType.objects.get_for_model(get_user_model())

    def log(self, user, flag):
        return LogEntry.objects.create(user=user, content_type=self.content_type, object_id='1', object_repr='Example', action_flag=flag)

    def test_staff_activity_is_scoped_to_current_user(self):
        self.log(self.user, ADDITION)
        self.log(self.other, CHANGE)
        dashboard = build_dashboard(self.site, self.request, [])
        self.assertEqual(dashboard['stats'][0]['value'], 1)
        self.assertEqual(sum(point['count'] for point in dashboard['chart']), 1)
        self.assertEqual(sum(point['additions'] for point in dashboard['chart']), 1)
        self.assertEqual(sum(point['changes'] for point in dashboard['chart']), 0)
        self.assertEqual(len(dashboard['history']), 1)
        self.assertIsNone(dashboard['log_url'])

    def test_superuser_sees_all_and_old_activity_is_outside_chart(self):
        self.user.is_superuser = True
        self.log(self.user, ADDITION)
        old = self.log(self.other, CHANGE)
        LogEntry.objects.filter(pk=old.pk).update(action_time=timezone.now() - timedelta(days=20))
        dashboard = build_dashboard(self.site, self.request, [])
        self.assertEqual(dashboard['stats'][0]['value'], 1)
        self.assertEqual(len(dashboard['history']), 2)

    def test_default_actions_follow_available_add_urls(self):
        apps = [{'models': [{'name': 'Allowed', 'add_url': '/add/'}, {'name': 'Denied', 'add_url': None}]}]
        dashboard = build_dashboard(self.site, self.request, apps)
        self.assertEqual([action['label'] for action in dashboard['actions']], ['Add Allowed'])

    def test_index_renders_and_translations_are_available(self):
        self.client.force_login(self.user)
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No recent activity yet.')
        with translation.override('fa'):
            self.assertEqual(translation.gettext('Overview'), 'نمای کلی')
            self.assertEqual(translation.gettext('No recent activity yet.'), 'هنوز فعالیت اخیری ثبت نشده است.')

    def test_user_metrics_respect_permissions_and_admin_queryset(self):
        class ScopedUserAdmin(admin.ModelAdmin):
            def get_queryset(self, request):
                return super().get_queryset(request).filter(pk=self_site.user.pk)

        self_site = self
        self.site.register(get_user_model(), ScopedUserAdmin)
        dashboard = build_dashboard(self.site, self.request, [])
        self.assertIsNone(dashboard['user_chart'])
        self.user.user_permissions.add(Permission.objects.get(content_type=self.content_type, codename='view_user'))
        # Django caches permissions on the user instance.
        self.request.user = get_user_model().objects.get(pk=self.user.pk)
        dashboard = build_dashboard(self.site, self.request, [])
        self.assertEqual([item['value'] for item in dashboard['stats'][:3]], [1, 1, 1])
        self.assertEqual(sum(point['count'] for point in dashboard['user_chart']['points']), 1)

    def test_user_chart_can_be_disabled_or_use_missing_date_field(self):
        self.user.is_superuser = True
        self.site.register(get_user_model(), admin.ModelAdmin)
        self.site.get_dashboard_config = lambda request: {'user_date_field': 'not_a_field'}
        dashboard = build_dashboard(self.site, self.request, [])
        self.assertEqual(dashboard['stats'][0]['value'], 2)
        self.assertIsNone(dashboard['user_chart'])
        self.site.get_dashboard_config = lambda request: {'show_user_stats': False, 'show_user_chart': False}
        dashboard = build_dashboard(self.site, self.request, [])
        self.assertEqual(str(dashboard['stats'][0]['label']), 'Activity')
        self.assertIsNone(dashboard['user_chart'])

    def test_superuser_index_renders_user_chart(self):
        self.user.is_superuser = True
        self.user.save()
        self.client.force_login(self.user)
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Total users')
        self.assertContains(response, 'Daily user registrations')
