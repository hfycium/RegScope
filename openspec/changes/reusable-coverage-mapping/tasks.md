## 1. Add reusable mapping input

- [x] 1.5 Add `regscope collect <target> --output <mapping-file>` and support an
  explicit mapping output path in the collector.
- [x] 1.1 Load and validate an optional saved mapping in `run_pipeline()`;
  preserve normal collection when none is provided.
- [x] 1.2 Add the `--mapping` CLI option and pass it through to the pipeline.
- [x] 1.3 Persist the supplied mapping under the run output directory.
- [x] 1.4 Add an opt-in selected-only mode that skips full-suite comparison.

## 2. Verify the behavior

- [x] 2.7 Test the standalone `collect` command and exact output path.
- [x] 2.1 Test that a supplied mapping bypasses coverage collection and is used
  for selection/evaluation.
- [x] 2.2 Test invalid mapping input and preserve the existing no-mapping path.
- [x] 2.3 Run the existing 58-test real-project mapping through the new CLI mode
  and verify the known failure remains selected.
- [x] 2.4 Verify selected-only mode invokes pytest only for selected tests and
  records the full-suite comparison as skipped.
- [x] 2.5 Verify the CLI propagates the selected test run's exit status.
- [x] 2.6 Run the RegScope suite and strict OpenSpec validation.
