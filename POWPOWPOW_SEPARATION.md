# PowPowPow — Separate Project

PowPowPow is a separate project from Datagarden/UKBoring.

## Status

- **PowPowPow repo**: `/home/box/powpowpow/`
- **Datagarden repo**: `/home/box/datagarden/`
- **Shared primitives**: Copied to `/home/box/powpowpow/datagarden/`

## What's Shared

The Data Garden framework (core/ and shared/) is garden-agnostic and lives in both repos:
- Observation, Entity, Source, DerivedFact, QualityGate, Storage, Receipt, Manifest
- Warehouse (two-tier storage), Manifest (Merkle proofs), Schema (domain types)

## What's NOT Shared

- Collectors (each project owns its own)
- MCP servers (each project owns its own)
- API keys (separate vaults)
- Data (separate canonical stores)

## Rules

1. Do not add powpowpow-specific logic to datagarden
2. Do not add UK-specific logic to powpowpow
3. Do not import from each other's collectors or MCP servers
4. Keep core/ primitives in sync across both repos
5. Each project is independently deployable

## PowPowPow Has

- 12/12 MCP tools real (100% real data)
- 17+ chains tracked
- Real-time stratum data, pool state, exchange ticks
- Historical backfill collectors
- Warehouse with canonical/ephemeral tiers

## Datagarden Has

- 86 MCP tools across 6 servers (42% real data)
- 2,629 canonical observations
- UK planning, contracts, complaints, salary data
- Jev semantic classification via OpenRouter
- earn() endpoint with 7 routes from 3 sources
