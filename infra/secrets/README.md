SOPS + age example

This repo includes guidance for using Mozilla SOPS with age for encrypting repository secrets.

Quick start:
1. Install sops and age.
2. Generate an age key:

```bash
age-keygen -o key.txt
```

3. Add the public key to your CI/CD environment variable store (if you plan to decrypt in CI). Keep the private key safe.
4. Encrypt a file:

```bash
sops --encrypt --age "<AGE_PUBLIC_KEY>" secrets.yaml > secrets.yaml.enc
```

5. Decrypt locally:

```bash
sops --decrypt secrets.yaml.enc > secrets.yaml
```

CI note:
- Store the age private key as a GitHub secret (e.g., `SOPS_AGE_KEY`) and use it in your workflow to decrypt files before deploy.
