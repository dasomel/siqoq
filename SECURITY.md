# Security Policy

Please do not report vulnerabilities through public issues when exploitation details, secrets, or unsafe physical-control behavior are involved.

When reporting a security issue, include:

- affected version/commit
- impact
- reproduction steps
- relevant logs without secrets
- suggested mitigation if known

## Physical safety

Siqoq may eventually interact with actuators and robots. Examples and default configurations must prefer mocks or non-destructive behavior. Hardware adapters should fail closed where practical and must not bypass explicit policy/safety boundaries.

## Secrets

Never commit credentials, API tokens, private keys, device secrets, or production certificates.
