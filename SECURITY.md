# Security Policy

I take security seriously and I am committed to ensuring the safety and reliability of the **ansible-hpc** project. This document outlines how to report vulnerabilities and our approach to handling security issues.

---

## 🔒 Supported Versions

The following versions of the **playbooks-ansible** repository are actively supported and receive security updates:

| Version       | Supported          |
|---------------|--------------------|
| Latest (main) | ✅ Yes             |
| Older versions | ❌ No (archived) |

If you are using an older version, we recommend upgrading to the latest version to benefit from security patches and improvements.

---

## 🐛 Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it as soon as possible. **Do not publicly disclose the vulnerability** until it has been resolved.

### How to Report:
1. **Email**: Send an email to [pausantanapi2@gmail.com](mailto:pausantanapi2@gmail.com) with the subject line: `Security Vulnerability Report`.
2. Include the following details:
   - A clear description of the vulnerability.
   - Steps to reproduce the issue.
   - Potential impact of the vulnerability.
   - Any relevant logs, screenshots, or code snippets.

I will acknowledge receipt of your report within **48 hours** and provide updates as we investigate and address the issue.

---

## 🔧 Handling Security Issues

Once a vulnerability is reported, I will follow these steps:
1. **Acknowledgment**: Confirm receipt of the report with the reporter.
2. **Investigation**: Assess the severity and scope of the vulnerability.
3. **Fix Development**: Develop a patch or mitigation for the issue.
4. **Testing**: Test the fix in a controlled environment to ensure it resolves the issue without introducing new problems.
5. **Release**: Deploy the fix in a new version and notify users.
6. **Disclosure**: Publicly disclose the vulnerability and credit the reporter (if desired).

---

## 🔑 Security Best Practices

To help keep your deployment secure:
- Regularly update your playbooks and dependencies.
- Use encrypted variables (`vault.yml`) for sensitive data like passwords and keys.
- Limit access to inventory files containing host details.
- Test playbooks in isolated environments before deploying them in production.

---

## 🤝 Responsible Disclosure

I encourage responsible disclosure practices. If you report a vulnerability responsibly, I will:
- Work with you to resolve it quickly.
- Credit you for your contribution (if desired).
- Keep you informed throughout the process.

---

## 📫 Contact

For any security-related inquiries, please contact me at [pausantanapi2@gmail.com](mailto:pausantanapi2@gmail.com).

Thank you for helping me keep **playbooks-ansible** secure! 🙏
