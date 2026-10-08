# github-actions-aws-terraform
Repository for Reusable OpenTofu GitHub Actions used to deploy resources in AWS.

## OpenTofu version

The reusable plan, apply and scheduled-plan workflows accept an optional
`opentofu_version` string input. Set the same exact version in each caller to
use it for validation, formatting, planning and applying saved plans:

```yaml
with:
  opentofu_version: "1.13.1"
```

When omitted or empty, existing defaults are preserved: validation and formatting
use 1.12.3, while the CLI setup uses latest. After changing the selected version,
generate and review a new plan before applying; do not reuse an older saved plan.
