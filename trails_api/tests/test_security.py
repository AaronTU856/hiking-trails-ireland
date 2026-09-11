from importlib import reload
from unittest.mock import patch

from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from django.test import TestCase, RequestFactory, override_settings
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from trails_api.models import Trail, Town, TrailDescriptionSuggestion


@override_settings(ROOT_URLCONF='webmapping_project.urls')
class SecurityTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user('contributor', password='test-password-123')
        self.staff = User.objects.create_user('moderator', password='test-password-123', is_staff=True, is_superuser=True)
        self.trail = Trail.objects.create(
            trail_name='Published trail', county='Wicklow', distance_km=5, elevation_gain_m=100,
            start_point=Point(-6.1, 53.2, srid=4326),
            description='Original published description', status='verified',
        )
        self.town = Town.objects.create(name='Sample town', location=Point(-6.1, 53.2, srid=4326))
        self.detail = f'/api/trails/{self.trail.pk}/'
        self.suggest = self.detail + 'suggest_description/'
        self.town_url = f'/advanced-js-mapping/api/town/edit/{self.town.pk}/'

    def test_public_browsing_remains_available(self):
        for url in ['/api/trails/', self.detail]:
            self.assertEqual(self.client.get(url, secure=True).status_code, 200)

    def test_anonymous_and_regular_users_cannot_mutate_catalogue(self):
        for user in [None, self.user]:
            self.client.force_authenticate(user=user)
            for method in ['put', 'patch', 'delete']:
                response = getattr(self.client, method)(self.detail, {'description': 'Changed text'}, format='json', secure=True)
                self.assertIn(response.status_code, [401, 403])
            response = self.client.post('/api/trails/', {}, format='json', secure=True)
            self.assertIn(response.status_code, [401, 403])
        self.trail.refresh_from_db()
        self.assertEqual(self.trail.description, 'Original published description')

    def test_staff_can_update_and_delete_trails(self):
        self.client.force_authenticate(user=self.staff)
        self.assertEqual(self.client.patch(self.detail, {'description': 'Reviewed update'}, format='json', secure=True).status_code, 200)
        self.assertEqual(self.client.delete(self.detail, secure=True).status_code, 204)

    def test_removed_import_url_cannot_delete_towns(self):
        for method in ['get', 'post']:
            self.assertEqual(getattr(self.client, method)('/api/trails/load-towns/', secure=True).status_code, 404)
        self.assertTrue(Town.objects.filter(pk=self.town.pk).exists())

    def test_anonymous_suggestions_are_rejected(self):
        response = self.client.patch(self.suggest, {'description': 'Untrusted suggestion'}, format='json', secure=True)
        self.assertIn(response.status_code, [401, 403])
        self.assertFalse(TrailDescriptionSuggestion.objects.exists())

    def test_jwt_suggestion_is_private_until_approved(self):
        token = str(RefreshToken.for_user(self.user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.patch(self.suggest, {'description': 'A new contributed description'}, format='json', secure=True)
        self.assertEqual(response.status_code, 200)
        suggestion = TrailDescriptionSuggestion.objects.get()
        self.assertEqual(suggestion.submitted_by, self.user)
        self.assertEqual(suggestion.status, 'pending')
        self.trail.refresh_from_db()
        self.assertEqual(self.trail.description, 'Original published description')
        self.assertEqual(self.trail.status, 'verified')
        self.client.credentials()
        self.assertEqual(self.client.get(self.detail, secure=True).data['description'], self.trail.description)

    def test_invalid_description_does_not_create_suggestion(self):
        self.client.force_authenticate(user=self.user)
        for value in [None, 123, 'short', ' ' * 20, 'x' * 10001]:
            self.assertEqual(self.client.patch(self.suggest, {'description': value}, format='json', secure=True).status_code, 400)
        self.assertFalse(TrailDescriptionSuggestion.objects.exists())

    def test_approval_publishes_once_and_rejection_preserves_published_text(self):
        model_admin = admin.site._registry[TrailDescriptionSuggestion]
        request = RequestFactory().post('/admin/')
        request.user = self.staff
        suggestion = TrailDescriptionSuggestion.objects.create(trail=self.trail, submitted_by=self.user, description='Approved suggestion')
        queryset = TrailDescriptionSuggestion.objects.filter(pk=suggestion.pk)
        model_admin.approve(request, queryset)
        self.trail.refresh_from_db()
        self.assertEqual(self.trail.description, suggestion.description)
        Trail.objects.filter(pk=self.trail.pk).update(description='Subsequent staff correction')
        model_admin.approve(request, queryset)
        self.trail.refresh_from_db()
        self.assertEqual(self.trail.description, 'Subsequent staff correction')
        rejected = TrailDescriptionSuggestion.objects.create(trail=self.trail, submitted_by=self.user, description='Rejected suggestion')
        model_admin.reject(request, TrailDescriptionSuggestion.objects.filter(pk=rejected.pk))
        rejected.refresh_from_db()
        self.assertEqual(rejected.status, 'rejected')
        self.trail.refresh_from_db()
        self.assertEqual(self.trail.description, 'Subsequent staff correction')

    def test_regular_account_cannot_manage_towns(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(self.town_url, secure=True).status_code, 403)
        self.assertEqual(self.client.put(self.town_url, {'name': 'Changed'}, format='json', secure=True).status_code, 403)
        self.assertEqual(self.client.delete(self.town_url, secure=True).status_code, 403)
        self.assertEqual(self.client.get('/advanced-js-mapping/towns/', secure=True).status_code, 403)

    def test_staff_town_edit_requires_csrf(self):
        client = APIClient(enforce_csrf_checks=True)
        client.force_login(self.staff)
        self.assertEqual(client.put(self.town_url, {'name': 'Changed'}, format='json', secure=True).status_code, 403)
        self.assertEqual(client.delete(self.town_url, secure=True).status_code, 403)
        csrf_token = 'a' * 32
        client.cookies['csrftoken'] = csrf_token
        response = client.put(self.town_url, {'name': 'Reviewed town'}, format='json', secure=True, HTTP_X_CSRFTOKEN=csrf_token, HTTP_ORIGIN='https://testserver')
        self.assertEqual(response.status_code, 200)
        self.town.refresh_from_db()
        self.assertEqual(self.town.name, 'Reviewed town')

    def test_importing_urls_does_not_create_admin_or_start_thread(self):
        import webmapping_project.urls
        with patch('threading.Thread') as thread, patch.object(User.objects, 'create_superuser') as create:
            reload(webmapping_project.urls)
        thread.assert_not_called()
        create.assert_not_called()

    def test_staff_town_page_and_listing_load(self):
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get('/advanced-js-mapping/towns/', secure=True).status_code, 200)
        response = self.client.get('/advanced-js-mapping/towns/?format=json', secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['towns'][0]['name'], self.town.name)

    def test_alternative_trail_creation_route_rejects_regular_users(self):
        self.client.force_login(self.user)
        response = self.client.post('/advanced-js-mapping/api/trails/', {}, format='json', secure=True)
        self.assertEqual(response.status_code, 403)


from django.test import SimpleTestCase
from django.template import engines
from django.utils.html import escapejs


class CartoConfigurationTests(SimpleTestCase):
    def test_browser_sends_origin_for_restricted_carto_tiles(self):
        response = self.client.get('/auth/login/', secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Referrer-Policy'], 'strict-origin-when-cross-origin')

    @override_settings(CARTO_BASEMAP_API_KEY='test-key</script>"&')
    def test_key_is_escaped_and_available_before_child_map_scripts(self):
        template = engines['django'].from_string(
            '{% extends "base.html" %}{% block extra_js %}<script id="map-initializer"></script>{% endblock %}'
        )
        html = template.render({}, request=RequestFactory().get('/'))
        self.assertIn(str(escapejs('test-key</script>"&')), html)
        self.assertNotIn('test-key</script>', html)
        self.assertLess(html.index('window.STAY_TREK_CONFIG'), html.index('id="map-initializer"'))

    @override_settings(CARTO_BASEMAP_API_KEY='')
    def test_missing_local_key_does_not_break_template_rendering(self):
        template = engines['django'].get_template('base.html')
        html = template.render({}, request=RequestFactory().get('/'))
        self.assertIn('cartoBasemapApiKey: ""', html)
