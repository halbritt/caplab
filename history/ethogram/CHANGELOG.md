# Changelog

This project does not yet publish numbered releases. Dated entries record
notable repository changes.

## Unreleased

### Changed

- Separated Pincite corpus, doctrine curation, retrieval, conversion, generated
  books, and source inputs from this repository.
- Added a fail-closed dependency contract for an exact Pincite release commit,
  corpus identity, and doctrine identity.
- Updated evaluation, adjudication, gold-queue, section-resolution, and Harbor
  projection tools to read Pincite inputs from `PINCITE_RELEASE_HOME` while
  preserving historical study outputs locally.
- Adopted Ethogram (`ethogram`) as the repository identity for agent-skill
  evaluation, judgment measurement, and governed model fine-tuning evidence.
- Preserved sealed historical experiment records, including old `books` mount
  paths, without treating them as live configuration.

### Added

- Added the Study 001 capability card and context-first review dashboard.
- Added the CAPLAB/Pincite boundary decision and context map.

## 2026-07-15

- Selected the Agent Capability Lab v0 product boundary and Study 001.
- Added the first reviewer-facing Study 001 projection and dashboard.

## 2026-07-12

- Added the Doctrine Robustness Laboratory contracts, behavioral evaluation
  harness, Harbor tasks, and adjudication records now retained by CAPLAB.
