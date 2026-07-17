# github-actions-aws-terraform

Reusable OpenTofu/Terraform GitHub workflows for planning, applying, drift checks, merge gating, docs generation, and config parsing.

## What this repo provides

Reusable workflows in `.github/workflows/`:

- `read-config.yml`: reads `.github/config.yaml` and exposes outputs
- `githubaction-comment-plan.yml`: runs plan and comments on PR
- `githubaction-comment-apply.yml`: runs apply and can auto-merge PR
- `githubaction-scheduled-plan.yml`: scheduled plan run
- `githubaction-scheduled-check.yml`: scheduled drift check
- `githubaction-merge-check.yml`: blocks merge when plan was not applied
- `githubaction-GenerateTerraformDocs.yml`: updates Terraform docs in `README.md`
- `githubaction-ds-deploy.yml`: documentation-site deployment workflow

You call these workflows from your own repository workflows via `uses: arvatoaws-labs/github-actions-aws-terraform/...@v2`.

---

## Step-by-step: use these workflows in your repository

### 1) Add required organizational secrets

At minimum, add these repository secrets:

- `TERRAFORM_GITHUB_ACTION_CLIENT_ID`
- `TERRAFORM_GITHUB_ACTION_PRIVATE_KEY`
- `TERRAFORM_GITHUB_ACTION_APP_ID`

Terraform variable secrets are read automatically if prefixed with `TF_VAR_` (for example `TF_VAR_MY_SECRET`) and the repository belongs to the Bertelsmann organization. Otherwise you have to also create them as organizational secrets.

- `TF_VAR_SDMSI_SUBSCRIPTION_KEY`
- `TF_VAR_SDMS_OCP_APIM_SUBSCRIPTION_KEY`
- `TF_VAR_SDMS_AUTH_RESOURCE`
- `TF_VAR_SDMS_CLIENT_SECRET`

### 2) Create GitHub App

We also need to configure the following GitHub Apps. This has to be done by the Org Administrator.

* TofuAutomation

### 3) Add `.github/config.yaml`

Create this file in your target repo:

```yaml
profiles:
  - name: <profileName>
    roleArn: <roleArn>
    region: <region>

accounts:
  - stack: dev
    environment: dev
    roleArn: <roleArn>
    region: <region>
    s3bucketName: <s3bucketName>
```

`profiles` is optional and only necessary if you want to reference AWS profiles in your terraform code.

Each `accounts` entry becomes one matrix item. `stack` is your subfolder. `environment` the name of your environment.

### 4) Add PR plan workflow (`tf-pull-request.yml`)

This runs plan automatically on PR activity. 

Just copy `tf-pull-request.yml` from `examples/org_internal/` or `examples/org_external` to `.github/workflows`, `org_internal` for Bertelsmann organization and `org_external` for the rest.

### 5) Add PR comment workflow (`tf-comment.yml`)

This enables `/plan` and `/apply` comments on PRs.

Just copy `tf-conmment.yml` from `examples/org_internal/` or `examples/org_external` to `.github/workflows`, `org_internal` for Bertelsmann organization and `org_external` for the rest.

### 6) Add merge check workflow (`tf-merge-check.yml`)

Checks if PR is ready to be merged.

Just copy `tf-merge-check.yml` from `examples/org_internal/` or `examples/org_external` to `.github/workflows`, `org_internal` for Bertelsmann organization and `org_external` for the rest.

### 7) (Optional) Add scheduled plan and drift workflows

Scheduled plan:

Just copy `tf-scheduled-plan.yml` from `examples/org_internal/` or `examples/org_external` to `.github/workflows`, `org_internal` for Bertelsmann organization and `org_external` for the rest.


Scheduled drift check:

Just copy `tf-scheduled-drift.yml` from `examples/org_internal/` or `examples/org_external` to `.github/workflows`, `org_internal` for Bertelsmann organization and `org_external` for the rest.

### 8) (Optional) Add Terraform docs workflow

Just copy `tf-docs` from `examples/org_internal/` or `examples/org_external` to `.github/workflows`, `org_internal` for Bertelsmann organization and `org_external` for the rest.

### 9) Other mandatory files

These file are identical for internal and external.

1. `examples/org_internal/.github/.terraform-docs.yml` to `.github/.terraform-docs.yml`
2. `examples/renovate.json` to `renovate.json`

---

## Bertelsmann org vs cross-org usage

- **Same org (recommended):** use `secrets: inherit`
- **Cross org:** pass secrets explicitly in each caller workflow (`secrets:` block), as shown in `examples/org_external/.github/workflows/`

---

## Complete examples

Copy full, ready-to-use examples from:

- `examples/org_internal`
- `examples/org_external`
