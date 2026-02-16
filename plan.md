# IntegrateAgent Voicemeeter Integration Plan (Phased + Trackable)

Summary: add Voicemeeter Potato control/readback to the IntegrateAgent HTTP API while preserving the current security model. This repository (Pi controller) tracks only controller-side work and API contract usage.

## Scope Split
- Pi Controller repo scope: payload wiring, seeded controls, docs.
- IntegrateAgent repo scope: actual Voicemeeter API calls, allowlist enforcement, readback, server logging.

## Milestones
- M1: Controller payload readiness.
- M2: IntegrateAgent write actions (`voicemeeter_apply`, `voicemeeter_group_bus_gain`, `voicemeeter_command`).
- M3: IntegrateAgent read action (`voicemeeter_get`).
- M4: IntegrateAgent security/allowlist/logging.
- M5: End-to-end validation and docs.

## Phase Checklist

### Phase 1: Controller-Side (this repo)
- [x] Seed vertical faders with gain range `-60..12`.
- [x] Seed actions for `voicemeeter_apply` and `voicemeeter_group_bus_gain`.
- [x] Document seeded Voicemeeter mappings in `USER_GUIDE.md` and `README.md`.
- [x] Update `STATUS.md` to reflect controller-side Voicemeeter readiness.

### Phase 2: IntegrateAgent Write Actions (server repo)
- [ ] Add Voicemeeter dependency to server runtime.
- [ ] Implement `voicemeeter_apply(settings)` with gain/mute validation.
- [ ] Implement `voicemeeter_group_bus_gain(gain)` for buses `0..2`.
- [ ] Implement `voicemeeter_command(command)` for allowlisted commands.

### Phase 3: IntegrateAgent Read Action (server repo)
- [ ] Implement `voicemeeter_get(targets, fields)` with allowlisted reads.
- [ ] Return structured results for strips/buses.

### Phase 4: Security + Observability (server repo)
- [ ] Config-driven allowlist for strips/buses/fields/commands.
- [ ] Strict request validation and clear error responses.
- [ ] Structured logs for VM actions and outcomes.

### Phase 5: Validation
- [ ] `voicemeeter_apply` accepts valid gains/mutes.
- [ ] Out-of-range gain is rejected.
- [ ] Unknown field/target is rejected.
- [ ] `voicemeeter_group_bus_gain` updates bus `0..2`.
- [ ] `voicemeeter_command` reset/restart path succeeds.
- [ ] `voicemeeter_get` returns requested values.
- [ ] Existing `run_app` and `key_press` remain functional.

## Change Log (Append-Only)
- 2026-02-14: Initial plan created. Scope: VM Potato integration with read/write and group bus gain.
- 2026-02-15: Continued plan in Pi controller repo; completed controller-side payload seeding and docs updates, with remaining phases explicitly marked as IntegrateAgent server work.
