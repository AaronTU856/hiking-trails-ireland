# Security hardening rollout

These changes are on `security/post-fyp-hardening`. They have not been deployed.

## Behaviour changes

- Public catalogue reads remain available. Creating, editing, and deleting trails
  requires an active staff account. Town edits require staff login and CSRF.
- Mobile/API Bearer JWTs are accepted alongside session and legacy token auth.
- Signed-in users submit descriptions into a separate review table. Published
  descriptions remain unchanged until an administrator approves a suggestion.
- The description suggestion admin offers approve/reject actions. Approval
  requires both suggestion-change and trail-change permissions.
- The public `load-towns` URL is removed. Use the existing `load_towns` management
  command only with a deliberately selected database and reviewed input data.
- Application startup never creates an administrator. Provision administrators
  explicitly with `createsuperuser` through a trusted administrative session.
- Cloud Build references server secrets rather than literal credentials, includes
  security tests, and tests the full URL configuration. Tests still use an
  isolated SpatiaLite database and do not establish PostGIS migration readiness.

## Required before production rollout

1. Keep the verified backup and identify a known-good image digest for rollback.
2. Test migration `0023_traildescriptionsuggestion` against an isolated restored
   PostGIS database. Do not run a restore or migrations against production as a test.
3. Create Secret Manager secrets `django_secret_key` and `openweathermap_api_key`.
   Generate a new Django key and obtain a replacement weather key from the provider.
   Grant the Cloud Run service account access to these two secrets only.
4. Review any existing administrator created by the removed startup routine;
   removing the code does not remove or reset that account. Reset its password or
   disable it through a trusted administrative session after verifying another
   usable administrator account exists.
5. Rotate any other exposed credentials found during the audit. Do not retain an
   exposed Django key in SECRET_KEY_FALLBACKS. Django key rotation invalidates
   sessions and JWTs, so users should expect to sign in again.
6. Run tests and apply the additive migration as an explicit controlled release
   step before directing traffic to the new image. The Dockerfile does not run
   `entrypoint.sh`; it does not automatically run migrations.
7. Verify staff administration and mobile sign-in/contributions in staging.
8. Merge/deploy only after the prerequisites above are complete. Revoke the old
   provider key after migration of its legitimate consumers.

The mobile weather screen currently uses EXPO_PUBLIC_OPENWEATHERMAP_API_KEY.
Public Expo variables are visible to users of a compiled app; moving the literal
out of source does not make it a server secret. Before distributing a refreshed
mobile build, route weather requests through the backend and retire that public
key. The current branch does not change this screen or rotate live credentials.

## Database protection

Automatic Cloud SQL backups are enabled daily at 12:00 UTC, retaining seven.
Baseline backup `1789074915017` completed successfully on 2026-09-10.
An isolated restoration test is still outstanding. It requires a separate
instance and has storage/compute costs; never overwrite `stay-trek-db` to test it.

## Local verification

On 2026-09-10, all 39 tests (11 security regression tests) passed with Django
system checks reporting no issues. Tests ran with Python 3.14 and the pinned
requirements in a temporary virtual environment; production uses Python 3.11.
The existing workspace virtual environment stalled while importing Django and
was left intact. The full URL configuration was exercised against an in-memory
SpatiaLite database. No production database was contacted by the tests.

Example macOS test command, using an environment with requirements installed:

```sh
SECRET_KEY=local-test-secret-not-for-production DEBUG=0 \
DJANGO_SETTINGS_MODULE=webmapping_project.settings_ci \
SPATIALITE_LIBRARY_PATH=/opt/homebrew/lib/mod_spatialite.dylib \
python manage.py test trails_api.tests --noinput
```

The migration state consistency check reports no missing migrations. Local
PostgreSQL on port 5432 was unavailable; PostGIS migration execution and the
actual Docker image remain release checks, not verified results.

## Release preparation — 2026-09-11

- Draft PR: https://github.com/AaronTU856/stay-and-trek-platform/pull/10
- Production-platform Docker build and 41 application/security tests passed.
- Secret Manager `django_secret_key:1` and `openweathermap_api_key:1` are prepared
  with runtime secret access. The replacement weather key returned valid data.
- Isolated Cloud SQL instance: `stay-trek-security-staging` (europe-west1).
- Restore source: backup `1789074915017` from `stay-trek-db`.
- Restore operation: `d7e77bcd-7e2d-4df3-97fb-7bb400000024`; completed successfully on 2026-09-11.
- Migration/verification job: `stay-trek-staging-migrate`.
- `scripts/verify_staging.py` refuses any database host except the staging socket,
  exercises web login, mobile JWT submissions, staff edits, and approval, and
  cleans up its disposable fixtures. It does not accept production as a target.
- Settings now honour NEW_DB_HOST/NEW_DB_NAME so staging cannot silently use the
  production socket. The production database remains `stay_and_trek`.
- Build images use commit tags; replacement secret versions are pinned to 1.

Rollback target before this release: Cloud Run revision
`stay-and-trek-service-00310-dqb`, image digest
`sha256:76e5422a1369b443b4901c9b600d839d676c7dd495b30fc672e648dcaa1841c5`.
Migration 0023 is additive. Roll back traffic without dropping the suggestion
storage; preserve contributions for investigation. Rolling back to the old
revision also restores its old credentials and security weaknesses, so rollback
is a short-term recovery measure, not a permanent fix.

Staging verification completed successfully in execution
`stay-trek-staging-migrate-hdlp9`. Only migration 0023 was pending; it applied
successfully. Restored trail count was 1055. Staff login, town CSRF/edit,
mobile JWT login/submission, and admin approval passed; fixtures were removed.
Authenticated requests to the private Cloud Run endpoint returned HTTP 200 for
the homepage, login page, and trail API. This verifies mobile API behaviour,
not a physical-device mobile UI test.

Fresh production backup: `1789116189476` (SUCCESSFUL, 2026-09-11T08:43:50Z).
Production migration job `stay-trek-production-migrate` verifies database
identity, checks for an active administrator and the known default password,
and refuses any migration plan except the additive 0023 migration.
