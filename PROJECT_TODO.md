# Stay & Trek development checklist

Started: 2026-09-10. Application code is unchanged. This checklist records the
post-FYP audit and development plan; unchecked work is not yet implemented.

## 1. Preserve and verify the baseline — complete

- [x] Confirm local and GitHub `dev`: `6e5515ee151be926f27205373256a183f2e9f385`.
- [x] Confirm the production image corresponds to that commit.
- [x] Confirm existing Cloud SQL backup settings and backup inventory.
- [x] Verify the new on-demand database backup finishes successfully.
- [x] Preserve final submission commit `119522457a8e700be4f65bef80944785d8bb10cd`
      using GitHub tag `fyp-final`.
- [x] Leave existing `submission-v1` tag and submission branch intact.

### Production evidence

- Project: `long-octane-477515-k6`; region: `europe-west1`.
- Cloud Run service: `stay-and-trek-service`.
- Serving revision: `stay-and-trek-service-00310-dqb`, receiving 100% of traffic.
- Revision created: 2026-06-06T17:55:45Z.
- Image digest: `sha256:76e5422a1369b443b4901c9b600d839d676c7dd495b30fc672e648dcaa1841c5`.
- Matching regional Cloud Build: `64836004-6b47-44d0-8823-28af21a0e785`.
- Build completed successfully on 2026-04-15; source provenance resolves to
  `6e5515ee151be926f27205373256a183f2e9f385` on GitHub. Build results contain the
  same image digest as the live revision. Build includes the Django test step.
- Cloud SQL instance: `stay-trek-db`.
- Initial backup inventory was empty; automatic backups were disabled.
- New on-demand backup: `1789074915017`, requested 2026-09-10T21:15:15Z.
- Backup status: `SUCCESSFUL`, completed 2026-09-10T21:16:46Z.
- Automatic backups were subsequently enabled on 2026-09-10 at 12:00 UTC,
  retaining seven backups. A successful backup does not establish restore
  readiness; restoration requires a separate test.
- Existing `submission-v1` points to `66a6bbe50eab80f848fb958599e3d225ea106828`,
  the parent of the final-submission commit. It was not moved.
- New tag: https://github.com/AaronTU856/stay-and-trek-platform/tree/fyp-final
- The historical source contains previously identified embedded credentials.
  No additional source archive or release attachment was published. The tag
  references a commit already present on the public submission branch.

## 2. Protect production data and credentials

- [x] Create `security/post-fyp-hardening` from `dev`.
- [x] Restrict trail writes and administrative town operations to staff (local branch).
- [x] Remove the data-changing town GET endpoint; retain the management-command import.
- [x] Remove automatic administrator creation and its predictable password fallback.
- [x] Prepare replacement Django/weather secrets and grant runtime access.
- [ ] Activate replacement secrets through the verified production release.
- [ ] Revoke the old weather key at the provider after checking remaining consumers.
- [x] Enforce staff/CSRF town edits and separate suggestions from published descriptions.
- [x] Configure automatic database backups: daily at 12:00 UTC, retain seven.
- [x] Restore backup into `stay-trek-security-staging` and apply migration 0023 successfully.

Step 2 implementation was authorised on 2026-09-10 and is on the security
branch. Local tests: 39 passed, including 11 security regression tests; Django
system checks passed. Tests used a fresh temporary Python 3.14 environment and
in-memory SpatiaLite, not the Python 3.11 production image or PostGIS. Migration
state check reports no missing model migrations. Live credentials have not been
rotated; the new Secret Manager references require provisioning before deployment.
No application deployment or production migration has been performed.
See `docs/SECURITY_ROLLOUT.md` for release prerequisites.

## 3. Establish local development and staging

- [ ] Document a reproducible fresh-checkout setup with example configuration.
- [ ] Provide development data isolated from production.
- [ ] Establish staging, explicit migration execution, and rollback procedures.

## 4. Strengthen validation

- [x] Add permission/authentication, CSRF, and moderation regression coverage.
- [x] Verify production-platform image includes tests: all 41 tests passed.
- [x] Exercise migration and core application workflows against restored staging PostGIS.
- [x] Test full URL configuration and staging web login, staff edits, JWT submissions, moderation.
- [ ] Verify the mobile UI on physical devices or simulators.
- [x] Remove Dockerfile suppression of static-file collection failures.

## 5. Align mobile and backend

- [x] Accept mobile JWTs in backend authentication; regression test passes.
- [ ] Correct shared helper URLs, request methods, and weather parameters.
- [ ] Consolidate screen requests into the shared API client.
- [ ] Configure development/staging/production URLs and token refresh handling.
- [ ] Verify core workflows on physical devices or simulators.

## 6. Reconcile branches and deployment

- [ ] Review unique changes before merging or retiring old branches.
- [ ] Reconcile useful changes on `main` and `dev` through a pull request.
- [ ] Protect production branches and require appropriate checks.
- [ ] Plan and verify any deployment-trigger switch; `dev` currently deploys.

## 7. Refresh repository presentation

- [ ] Rewrite product documentation and archive FYP-specific material.
- [ ] Remove generated tracked files only after generation is reproducible.
- [ ] Review duplicate templates, prototypes, and obsolete scripts.
- [ ] Retire or replace `cleanup.sh`; it deletes the active `maps` app and backups.

## 8. Improve maintainability and product experience

- [ ] Split large backend and map modules incrementally with regression coverage.
- [ ] Prioritise accessibility, mobile usability, performance, and data quality.
- [ ] Maintain a small, demonstrable feature roadmap for the portfolio.

## Release checkpoint — 2026-09-11

Draft PR #10 targets dev. Candidate commit: 6c559a7. All 41 tests passed inside
the Linux/AMD64 production image. Staging image digest:
`sha256:66839fc804a8429d4fe8fb57b9c40fb55773d42927069efffba0acf8cf23a8e7`.
The private staging service is `stay-and-trek-staging`; its database is
`stay-trek-security-staging`. Restore operation completed successfully.
Execution `stay-trek-staging-migrate-hdlp9` applied only migration 0023 and passed
all guarded staging workflows, cleaning up its disposable fixtures.
Fresh production backup `1789116189476` completed successfully before release.
Production migration and deployment are being tracked in the rollout notes.
