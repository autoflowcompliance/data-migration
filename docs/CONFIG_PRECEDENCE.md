# Config precedence: one chain, and what it does not cover

This document records a decision. Before it, "defaults < YAML < env < CLI" was
written in a specification but was not how the code behaved: YAML blocks were
read by `app_files/config_bindings.py` with no env layer, and environment
variables were read ad hoc at call sites (`PAYMENT_*`, `DATAREADY_TEST_POSTGRES_URL`,
the connector URLs). Nothing was wrong, but "one config pattern" was an
aspiration rather than a fact.

## The decision

**Adopt the chain. Four layers, later wins:**

```
defaults  <  YAML  <  env  <  CLI
```

A module's effective setting is resolved by walking those layers in order and
taking the last one that supplies a value. This is the standard going forward
for every module that declares a config block.

## What each layer is for

| Layer | Source | Who sets it | Use it for |
|---|---|---|---|
| defaults | the module's own dataclass | the developer | the safe value when nothing is configured |
| YAML | the config block under `app_files/configs/` | the operator, per source | what a source needs, committed with it |
| env | `AUTOFLOW_<MODULE>_<SETTING>` | the deployment | secrets and per-environment overrides that must not be committed |
| CLI | a command-line flag | whoever runs the job | a one-off, this run only |

The layers are ordered by **scope**, not by importance: a default is global, a
YAML block is per source, an env var is per deployment, a flag is per
invocation. Later layers are narrower, so they win.

## The naming rule for env

Env overrides are namespaced so two modules cannot collide:

```
AUTOFLOW_<MODULE>_<SETTING>
```

`AUTOFLOW_QUALITY_SLA_COMPLETENESS=0.99` overrides the `quality.sla.completeness`
YAML key. Nested keys join with `_`. Uppercase. This is deliberately different
from the existing `PAYMENT_*` and `DATAREADY_*` variables, which predate this
decision and are **not** migrated — see "What this does not change" below.

## The two rules that make it safe

1. **Fail closed.** An unset or unparseable value falls back to the layer
   below, and ultimately to the default. It never silently becomes "off" or
   zero when the module was asked to be on. A malformed env override is
   reported, not ignored.

2. **A layer that is not present is not a layer that said nothing.** The
   resolver distinguishes "this layer did not mention the key" from "this layer
   set it to empty". Absence falls through; an explicit empty value is a value.

## What this does not change

This decision governs **new** module config blocks. It does not retrofit the
existing layers, and it does not touch:

- `PAYMENT_*` and `DATAREADY_*` variables, read through `app_files/settings.py`
  and the buy route. Those are deployment settings, not module config, and they
  already have documented precedence of their own (`PORT` > `DATAREADY_PORT`).
- `AUTOFLOW_HOME` / `DATAREADY_HOME`, which are state-location variables, not
  config values. They are read where state is written.
- The connector URLs (`DATAREADY_TEST_POSTGRES_URL` and friends), which name a
  connection, not a module setting.

Changing any of those would alter behaviour for existing deployments, which the
additive rule forbids. If a future change wants them on the standard chain, it
is a migration with its own tests, not a drive-by edit.

## Where it is implemented

`app_files/core/config.py` — `resolve(block, defaults, yaml_values, env, cli,
namespace)`. The four layers are applied in one place so no module invents its
own order, and `tests/unit/test_core_config.py` pins the order, the fallback and
the empty-vs-absent distinction.

## Why a new package (`app_files/core/`) and not an existing one

The specification asked for `app_files/core/registry.py` and
`app_files/core/schema.py` as well. The registry half is already built and is
**not** duplicated: `app_files/plugins/registry.py` is the binding pattern, and
it stays the only one. `app_files/core/` holds only what had no home — the
precedence resolver and the config error type. It registers nothing.
