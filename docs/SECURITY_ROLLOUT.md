# Security hardening rollout

Updated 2026-09-12. Security hardening was deployed through PR #10; CARTO
integration and its referrer-policy correction followed in PRs #11 and #12.
This is a completed-release record and a guide to remaining cleanup, not a
request to repeat backups, restores, migrations or staging validation.

## Current production checkpoint

- Commit: `cc7e344459febd867465a71d83b9c18f0bdc8923` on `dev`.
- Revision: `stay-and-trek-service-00328-veh`, verified at 100% traffic.
- Successful matching build: `966d952c-fff8-4f72-bc9e-0f97b2de8288`.
- Image digest: `sha256:8b18f944e286ae1ee78cf251440a678395230a0b440056f9dc7dd3da6773d5e6`.
- Project `long-octane-477515-k6`, region `europe-west1`.
- Runtime account: `cloud-run-service-account@long-octane-477515-k6.iam.gserviceaccount.com`.
- Verified secret bindings: `SECRET_KEY=django_secret_key:1`,
  `OPENWEATHERMAP_API_KEY=openweathermap_api_key:1`,
  `CARTO_BASEMAP_API_KEY=carto_basemap_api_key:1`,
  `NEW_DB_PASSWORD=cloud_sql_password:latest`, `MY_API_KEY=api_key_secret:latest`.
  These are secret references, not credential values.
- The renamed GitHub repository link is `stay-and-trek-platform`; trigger
  `stay-and-trek-dev-trigger` uses `^dev$` and `cloudbuild.yaml`.
- Builds deploy a tagged candidate with `--no-traffic`. Promotion is an explicit
  step after validation; a successful build alone does not switch production.

## CARTO validation and rollback

The original CARTO candidate exposed the configured key, but Django's
`same-origin` referrer policy prevented browser domain validation. Production
was restored to the preceding revision while PR #12 corrected the policy to
`strict-origin-when-cross-origin`. All 44 Docker tests passed, including a
response-header regression test.

The corrected candidate's Trails & Stays, Townland Explorer and dashboard map
pages returned HTTP 200 with the expected policy and map configuration. The user
confirmed that the candidate browser map had no watermark. After promotion,
the production map returned HTTP 200 with the corrected policy. A CARTO tile
requested using production configuration and the production referrer returned
HTTP 200; its saved image was visually checked and had no watermark. A full
production browser sweep and physical-device mobile testing remain unverified.

For recovery from this CARTO release, the preceding security-release revision is
`stay-and-trek-service-00311-v59`. Restore traffic to that exact revision if
needed; do not reverse migration 0023 or drop suggestion data. This rollback
restores the map watermark issue because it predates CARTO integration.

```sh
gcloud run services update-traffic stay-and-trek-service \
  --project=long-octane-477515-k6 --region=europe-west1 \
  --to-revisions=stay-and-trek-service-00311-v59=100
```

The temporary CARTO `*.a.run.app` allowance was used for candidate browser
validation. Its removal has been requested but not confirmed. Retain the two
production referrers, `stay-and-trek.com` and `www.stay-and-trek.com`. Never put
key values in documentation, screenshots, commits or diagnostic output.

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

## Completed release prerequisites

- Backup `1789074915017` was restored into isolated
  `stay-trek-security-staging`; migration 0023 and guarded staging workflows
  succeeded. Production was not overwritten to test restoration.
- Replacement Django/weather secrets were provisioned, runtime access granted,
  and bindings activated in production. CARTO was subsequently provisioned and
  bound without removing the existing secrets.
- Production migration 0023 succeeded in execution
  `stay-trek-production-migrate-zltt2`, after backup `1789116189476` succeeded.
- Staging web login, staff edits, CSRF checks, mobile JWT submissions and admin
  moderation passed. These do not establish physical-device mobile UI readiness.

## Remaining credential and application cleanup

- Confirm removal of the temporary CARTO candidate referrer allowance.
- The user confirmed the replacement OpenWeather key is in Secret Manager;
  its production binding and weather responses were already verified. Do not
  revoke that replacement key. Revocation of the old exposed provider key is
  still unconfirmed and is a separate cleanup item.
- Current scope is finishing the web application. The mobile app is a prototype;
  its weather/trail-detail screens still reference
  `EXPO_PUBLIC_OPENWEATHERMAP_API_KEY`, but compatibility with prototype builds
  does not gate web work. Mobile backend integration and device tests are deferred.
- Explicitly verify the administrator account formerly created by startup code.
  Removing that routine does not reset existing accounts. The production
  migration guard checked for an active administrator and the known default
  password; this is not evidence that a full account review was completed.
- Verify rotation/revocation of any other exposed credentials from the audit.
  Do not retain an exposed Django key in `SECRET_KEY_FALLBACKS`.
- Track `/dashboard/analytics/` HTTP 500 separately. It failed on both the old
  production revision and the CARTO candidate. Its view references an unimported
  `Accommodation` and a nonexistent model `category` field. The main dashboard
  map is a separate working page; no analytics fix was included in this release.

## Database protection

Automatic Cloud SQL backups were verified as daily at 12:00 UTC, retaining
seven. Baseline backup `1789074915017` and fresh pre-release backup
`1789116189476` succeeded. Isolated restoration, staging migration and production
migration 0023 are complete. Do not repeat them to close stale checklist items.

## Historical local verification — 2026-09-10

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

At that checkpoint, the migration state consistency check found no missing
migrations and local PostgreSQL was unavailable. Subsequent Docker and restored
PostGIS checks passed as recorded below; the latest Docker suite passed 44 tests.

## Completed security release evidence — 2026-09-11

- Merged PR: https://github.com/AaronTU856/stay-and-trek-platform/pull/10
- Production-platform Docker build and 41 application/security tests passed.
- Secret Manager `django_secret_key:1` and `openweathermap_api_key:1` were provisioned
  with runtime secret access and are active in production. The replacement weather key returned valid data.
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

Historical rollback target before PR #10 (not the CARTO rollback target): Cloud Run revision
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
and refuses any migration plan except the additive 0023 migration. Execution
`stay-trek-production-migrate-zltt2` succeeded; this migration is complete.
