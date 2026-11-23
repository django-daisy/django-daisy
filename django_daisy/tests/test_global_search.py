from unittest.mock import patch

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import RequestFactory, TestCase
from django.urls import reverse

from django_daisy.admin import DaisyAdminSite
from django_daisy.global_search import search


class SearchUserAdmin(admin.ModelAdmin):
    search_fields = ('username',)

    def get_queryset(self, request):
        return super().get_queryset(request).exclude(username='hidden-user')

    def has_view_permission(self, request, obj=None):
        return super().has_view_permission(request, obj) and (obj is None or obj.username != 'denied-user')

    def get_search_results(self, request, queryset, search_term):
        if search_term == 'custom-term':
            return queryset.filter(username='visible-user'), False
        return super().get_search_results(request, queryset, search_term)


class GlobalSearchTests(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.staff = self.User.objects.create_user(username='staff', is_staff=True)
        self.staff.user_permissions.add(Permission.objects.get(codename='view_user'))
        self.User.objects.create_user(username='visible-user')
        self.User.objects.create_user(username='hidden-user')
        self.User.objects.create_user(username='denied-user')
        self.site = DaisyAdminSite(name='admin')
        self.site.register(self.User, SearchUserAdmin)

    def request(self, term):
        request = RequestFactory().get('/admin/global-search/', {'q': term})
        request.user = self.staff
        return request

    def test_pages_are_searchable_but_records_require_opt_in(self):
        self.assertTrue(any(r['group'] == 'Pages' for r in search(self.site, self.request('users'), {})))
        self.assertFalse(any(r['label'] == 'visible-user' for r in search(self.site, self.request('visible'), {})))
        result = search(self.site, self.request('visible'), {'models': ['auth.user']})
        self.assertEqual([r['label'] for r in result], ['visible-user'])
        self.assertIn('/change/', result[0]['url'])

    def test_query_and_object_permissions_and_custom_search_are_respected(self):
        config = {'models': ['auth.user']}
        result = search(self.site, self.request('user'), config)
        labels = [r['label'] for r in result]
        self.assertIn('visible-user', labels)
        self.assertNotIn('hidden-user', labels)
        self.assertNotIn('denied-user', labels)
        self.assertEqual(search(self.site, self.request('custom-term'), config)[0]['label'], 'visible-user')

    def test_no_access_and_short_terms(self):
        self.staff.user_permissions.clear()
        self.staff = self.User.objects.get(pk=self.staff.pk)
        self.assertEqual(search(self.site, self.request('user'), {'models': ['auth.user']}), [])
        self.assertEqual(search(self.site, self.request('u'), {'models': ['auth.user']}), [])

    def test_add_action_requires_add_permission(self):
        self.assertFalse(any(r['group'] == 'Actions' for r in search(self.site, self.request('user'), {})))
        self.staff.user_permissions.add(Permission.objects.get(codename='add_user'))
        self.staff = self.User.objects.get(pk=self.staff.pk)
        self.assertTrue(any(r['group'] == 'Actions' for r in search(self.site, self.request('user'), {})))

    def test_result_limit(self):
        self.User.objects.create_user(username='another-user')
        records = [r for r in search(self.site, self.request('user'), {
            'models': ['auth.user'], 'limit_per_model': 1,
        }) if r['label'] in ('visible-user', 'another-user')]
        self.assertEqual(len(records), 1)

    def test_authenticated_endpoint_and_switch(self):
        url = reverse('admin:global_search')
        self.assertEqual(self.client.get(url).status_code, 302)
        self.client.force_login(self.staff)
        response = self.client.get(url, {'q': 'users'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('no-store', response['Cache-Control'])
        self.assertEqual(self.client.post(url).status_code, 405)
        with patch('django_daisy.admin.DAISY_SETTINGS', {'GLOBAL_SEARCH': {'enabled': False}}):
            self.assertEqual(self.client.get(url).status_code, 404)

    def test_navigation_renders_search_for_staff(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse('admin:index'))
        self.assertContains(response, 'id="global-search-input"')
        self.assertContains(response, 'id="global-search-dropdown"')
        self.assertContains(response, reverse('admin:global_search'))
