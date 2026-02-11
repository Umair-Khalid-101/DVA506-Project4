## Branch: `asli-update` – State Machine & Controller Improvements

This branch introduces architectural improvements to the SmartMove core engine
by centralizing state transitions, improving telemetry handling, and enhancing
audit log integrity.

---

### 📁 Modified Files

- `smartmove/core/controller.py`
  - Added centralized `transition_vehicle()` gateway.
  - All vehicle state updates now go through a single controlled flow.
  - Added user and vehicle validation logic.

- `smartmove/core/state_machine.py`
  - Extended validation with guard conditions.
  - Added lifecycle constraints required by the LAB specification.
  - Prevents invalid transitions such as Maintenance without fault/low battery.

- `smartmove/core/telemetry.py`
  - Refactored to use controller transition gateway.
  - Added automatic safety interventions:
    - Overheating → EmergencyLock
    - Critical battery → Maintenance
    - Movement without active rental → Theft alarm.

- `smartmove/persistence/audit_log.py`
  - Added sequential `seq_id` field to audit entries.
  - Maintains checksum chain for audit integrity.
  - Supports rollback if audit write fails.

- `smartmove/rules/base.py`
  - Improved base class by enforcing method overrides with `NotImplementedError`.

---

### ℹ️ Notes
This branch is intended for team review and testing before merging into `master`.
No direct changes to production logic were made outside the centralized transition flow.
