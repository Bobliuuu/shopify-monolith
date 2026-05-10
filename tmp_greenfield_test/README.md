# GreenField Ultra-Cheap Dataset

Target docs requested: 10000
Bundles generated: 60
Actual docs generated: 648
Images selected under budget: 230
Estimated image budget: $40.0
Estimated cost/image: $0.08
Estimated image spend if run: $18.40

## Use
Text-only:
```bash
python greenfield_10k_generator.py --target-docs 10000 --dry-run --overwrite
```

Generate images:
```bash
export OPENAI_API_KEY=...
python greenfield_10k_generator.py --target-docs 10000 --generate-images --image-budget-usd 40 --estimated-cost-per-image 0.08 --overwrite
```

## Dataset strategy
Most examples are text-only for cheap scale. Images are prioritized for:
1. handwritten notes
2. invoices
3. vendor receipts
4. delivery tickets
5. bank/payment proofs
6. SMS/email screenshots
7. inventory/catalog/website edge cases
