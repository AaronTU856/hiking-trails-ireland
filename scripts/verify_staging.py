"""Exercise release workflows only against the isolated staging database.

Run through manage.py shell after staging migrations. Never targets production.
"""
import json
import secrets
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from django.test import Client
from trails_api.models import Trail, Town, TrailDescriptionSuggestion

expected_host = '/cloudsql/long-octane-477515-k6:europe-west1:stay-trek-security-staging'
assert settings.DATABASES['default']['HOST'] == expected_host, 'Refusing non-staging database'
assert settings.DATABASES['default']['NAME'] == 'stay_and_trek', 'Unexpected database'
print('Staging database identity verified; trails:', Trail.objects.count())
suffix = secrets.token_hex(6)
password = secrets.token_urlsafe(32)
member = staff = trail = town = None
try:
    member = User.objects.create_user('release-member-' + suffix, password=password)
    staff = User.objects.create_superuser('release-staff-' + suffix, password=password)
    trail = Trail.objects.create(trail_name='Release check ' + suffix, county='Wicklow', distance_km=5,
                                 elevation_gain_m=100, start_point=Point(-6.1, 53.2, srid=4326),
                                 description='Original published description', status='verified')
    town = Town.objects.create(name='Release town ' + suffix, location=Point(-6.1, 53.2, srid=4326))
    public = Client(HTTP_HOST='stay-and-trek.com')
    detail = f'/api/trails/{trail.pk}/'
    assert public.get('/auth/login/', secure=True).status_code == 200
    assert public.get(detail, secure=True).status_code == 200
    assert public.patch(detail, data=json.dumps({'description': 'Forbidden change'}), content_type='application/json', secure=True).status_code in (401, 403)
    response = public.post('/api/token/', data=json.dumps({'username': member.username, 'password': password}), content_type='application/json', secure=True)
    assert response.status_code == 200, 'Mobile token login failed'
    token = response.json()['access']
    response = public.patch(detail + 'suggest_description/', data=json.dumps({'description': 'A reviewed mobile contribution'}), content_type='application/json', secure=True, HTTP_AUTHORIZATION='Bearer ' + token)
    assert response.status_code == 200, 'Mobile submission failed'
    trail.refresh_from_db()
    assert trail.description == 'Original published description'
    suggestion = TrailDescriptionSuggestion.objects.get(trail=trail)
    admin_client = Client(enforce_csrf_checks=True, HTTP_HOST='stay-and-trek.com')
    login_page = admin_client.get('/auth/login/', secure=True)
    csrf = admin_client.cookies['csrftoken'].value
    response = admin_client.post('/auth/login/', {'username': staff.username, 'password': password, 'csrfmiddlewaretoken': csrf}, secure=True, HTTP_ORIGIN='https://stay-and-trek.com')
    assert response.status_code == 302, 'Staff web login failed'
    csrf = admin_client.cookies['csrftoken'].value
    assert admin_client.get('/advanced-js-mapping/towns/', secure=True).status_code == 200
    town_url = f'/advanced-js-mapping/api/town/edit/{town.pk}/'
    assert admin_client.put(town_url, data=json.dumps({'name': 'Reviewed town'}), content_type='application/json', secure=True).status_code == 403
    response = admin_client.put(town_url, data=json.dumps({'name': 'Reviewed town'}), content_type='application/json', secure=True, HTTP_X_CSRFTOKEN=csrf, HTTP_ORIGIN='https://stay-and-trek.com')
    assert response.status_code == 200, 'Staff town edit failed'
    response = admin_client.post('/admin/trails_api/traildescriptionsuggestion/', {'action': 'approve', '_selected_action': str(suggestion.pk), 'csrfmiddlewaretoken': csrf}, secure=True, HTTP_ORIGIN='https://stay-and-trek.com')
    assert response.status_code == 302, 'Admin approval failed'
    trail.refresh_from_db()
    suggestion.refresh_from_db()
    assert trail.description == 'A reviewed mobile contribution' and suggestion.status == 'approved'
    print('PASS: public reads; anonymous write rejection; mobile JWT login/submission; staff web login; town CSRF/edit; admin moderation.')
finally:
    if trail: Trail.objects.filter(pk=trail.pk).delete()
    if town: Town.objects.filter(pk=town.pk).delete()
    for user in [member, staff]:
        if user: User.objects.filter(pk=user.pk).delete()
    print('Disposable staging fixtures cleaned up.')
