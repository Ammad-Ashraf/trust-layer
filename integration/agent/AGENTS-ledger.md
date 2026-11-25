
## Normalization ledger (required)

Record every factor of your signal normalization, expected events = σ × L × BR × ε × (any corrections), in the ledger with `bin/record-quantity`. Use one call per factor, each with its unit and where it came from:

```
bin/record-quantity cross_section --value <sigma> --unit fb --source-type prospino --process <process> --mass <particle>=<GeV> --source "<tool and settings, or table>"
bin/record-quantity luminosity --value <L> --unit fb^-1 --source "<where>"
bin/record-quantity branching_fraction --value <BR> --source "<where>"        # or: --value 1 --reason "<why>"
bin/record-quantity efficiency --value <eps> --n-pass <N> --n-gen <N> --source "<script>"
bin/record-quantity correction --name <label> --value <x> --source "<where>"  # each extra factor you apply
bin/record-quantity generator_cross_section --value <sigma_gen> --unit fb --source "<generator output>"   # optional
bin/record-quantity show                                                      # print the ledger and its product
```

- `--source-type` is one of: prospino, xsec_wg, paper, hepdata, generator, other.
- `bin/record-quantity --help` lists the process and particle names.
- The sum of the bins you submit in `results/*.yaml` should equal the ledger's product.
- When you finish, a checker reads `ledger.yaml` and your results file. If something doesn't add up, it tells you what.
