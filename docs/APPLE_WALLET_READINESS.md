# Apple Wallet readiness — Exponenta

Status: PREPARED / BLOCKED ONLY BY APPLE ORGANIZATION APPROVAL + PASS CERTIFICATE

## Target architecture
- Web-first; no iOS app required for MVP.
- Loyalty passes use Apple Wallet Store Card passes.
- Exponenta remains the issuer; each business supplies branding and loyalty configuration.
- Backend generates signed .pkpass files and later supports Apple Wallet Web Service updates.
- Existing Google Wallet flow remains independent.

## Planned identifiers
Do not create these until the Apple Developer Organization membership is active.
- Pass Type ID candidate: `pass.mx.exponenta.club`
- Team ID: pending Apple Developer activation.

## Required Railway secrets (DO NOT COMMIT VALUES)
- APPLE_WALLET_ENABLED=false
- APPLE_PASS_TYPE_IDENTIFIER=
- APPLE_TEAM_IDENTIFIER=
- APPLE_WWDR_CERT_B64=
- APPLE_PASS_CERT_P12_B64=
- APPLE_PASS_CERT_PASSWORD=
- APPLE_WALLET_WEB_SERVICE_URL=https://wallet.exponenta.mx
- APPLE_WALLET_AUTH_SECRET=

Keep private keys/certificates only in Railway secrets. Never commit .p12, private keys, passwords, or decoded certificate material.

## MVP endpoints to implement after certificate issuance
1. `GET /wallet/apple/{membership_id}`
   - Authenticate/authorize the membership.
   - Build pass.json from business + loyalty membership.
   - Add business branding assets.
   - Add QR/barcode payload with opaque membership token.
   - Sign manifest using Pass Type certificate + Apple WWDR chain.
   - Return `application/vnd.apple.pkpass`.

2. Apple Wallet Web Service
   - Register device for pass.
   - Unregister device.
   - List changed serial numbers since update tag.
   - Fetch latest pass.
   - Receive Apple log messages.

3. Loyalty event hook
   - Existing visit/points/stamp mutation updates membership.
   - Mark pass update tag.
   - Push APNs notification to registered devices.
   - Wallet fetches the new pass.

## Data model additions
- apple_pass_serial_number: stable opaque UUID per membership.
- apple_auth_token_hash: never expose DB IDs.
- apple_update_tag / updated_at.
- apple_device_registrations: device_library_identifier, push_token, serial_number.
- business wallet branding: logo, icon, foreground/background/label colors.

## Pass fields
- formatVersion: 1
- passTypeIdentifier: from Railway secret
- teamIdentifier: from Railway secret
- serialNumber: opaque stable value
- organizationName: Exponenta / business presentation rules to validate before production
- description: loyalty card
- storeCard: balance/stamps/reward fields
- barcode: QR with opaque validation token
- webServiceURL + authenticationToken when live updates are enabled

## Security rules
- No customer PII in QR payload.
- QR carries only an opaque, revocable token.
- Pass authentication tokens stored hashed where feasible.
- Certificate rotation must not require changing membership identity.
- Rate-limit pass downloads and Wallet web-service routes.
- Validate tenant ownership on every generation/update.
- Log issuance/update failures without certificate contents.

## Activation checklist
1. D-U-N-S confirmed by Dun & Bradstreet.
2. Apple Developer Program enrolled as EXPONENTA, S.A.S. DE C.V. (Organization).
3. Create Pass Type ID.
4. Create/download Pass Type ID certificate.
5. Export signing certificate + private key to password-protected .p12.
6. Obtain current Apple WWDR intermediate certificate.
7. Add certificate material to Railway secrets.
8. Enable staging generation and produce one Café Exponenta test pass.
9. Install on a real iPhone.
10. Validate QR, branding, stamp/points update, re-download and push update.
11. Set APPLE_WALLET_ENABLED=true only after end-to-end validation.

## Current blocker
D-U-N-S request is processing at Dun & Bradstreet. No certificate-dependent code should be enabled in production until Apple Developer Organization enrollment is active.
