PYTHON ?= python3
PINCITE_RELEASE_HOME ?= $(HOME)/.local/share/pincite/release

CAPLAB_TEST_MODULES := \
	tests.test_adjudication_server \
	tests.test_authority_contract \
	tests.test_caplab_dashboard \
	tests.test_doctrine_scaffolding \
	tests.test_doctrine_injection_probe \
	tests.test_evaluation_error_taxonomy \
	tests.test_evaluation_fixture_hygiene \
	tests.test_evaluation_regression_gate \
	tests.test_entailment_eval \
	tests.test_pincite_dependency \
	tests.test_run_checkout_activation \
	tests.test_section_extraction \
	tests.test_summarize_harbor_trials

PINCITE_INTEGRATION_TEST_MODULES := \
	tests.test_doctrine_skill_eval \
	tests.test_gold_queue_contract \
	tests.test_robustness_lab \
	tests.test_section_oracle

.PHONY: check evaluation-gate fixture-hygiene gold-check gold-write
.PHONY: integration-check pincite-check test

test:
	$(PYTHON) -m unittest -v $(CAPLAB_TEST_MODULES)

evaluation-gate: fixture-hygiene
	$(PYTHON) doctrine/tools/evaluation_regression_gate.py check --root .

fixture-hygiene:
	$(PYTHON) doctrine/tools/check_evaluation_fixtures.py

pincite-check:
	PINCITE_RELEASE_HOME="$(PINCITE_RELEASE_HOME)" \
		$(PYTHON) -m caplab.pincite \
		--repo-root . \
		--pincite-home "$(PINCITE_RELEASE_HOME)"

gold-check:
	$(PYTHON) doctrine/tools/build_gold_queue.py \
		--root . \
		--pincite-root "$(PINCITE_RELEASE_HOME)" \
		--check

gold-write:
	$(PYTHON) doctrine/tools/build_gold_queue.py \
		--root . \
		--pincite-root "$(PINCITE_RELEASE_HOME)" \
		--write

integration-check: pincite-check gold-check
	PINCITE_RELEASE_HOME="$(PINCITE_RELEASE_HOME)" \
		$(PYTHON) -m unittest -v $(PINCITE_INTEGRATION_TEST_MODULES)

check: test evaluation-gate integration-check
