# Contributing to FlowState

First off, thank you for considering contributing to FlowState! It's people like you that make open-source such a great community.

## 🔄 How a Change Works and Gets Accepted

To ensure high-quality code and a smooth review process, please follow this workflow when contributing to FlowState:

### 1. Find or Create an Issue
Before writing any code, check the GitHub Issues tab to see if the feature or bug you want to work on is already being tracked. If not, open a new Issue describing the problem or feature so we can discuss it before you spend time coding.

### 2. Fork and Create a Branch
1. Fork the repository on GitHub.
2. Clone your fork locally.
3. Create a descriptive branch from the `develop` branch.
   ```bash
   git checkout develop
   git checkout -b feat/your-amazing-feature
   ```

### 3. Write Your Code
- Keep your code clean, modular, and well-documented.
- FlowState is an anti-hallucination tool, so practice what we preach: **Avoid excessive, redundant comments.** Only comment "why", not "what".
- Ensure you have type hints on all new Python function signatures.

### 4. Test Your Changes
Run the FlowState CLI and UI locally to ensure nothing is broken.
```bash
pip install -e .
flowstate ui
```
Test your specific feature end-to-end.

### 5. Commit and Push
We highly recommend using FlowState to write your commits!
```bash
git add .
flowstate commit "Brief description of changes"
git push origin feat/your-amazing-feature
```

### 6. Open a Pull Request (PR)
- Open a Pull Request against the **`develop`** branch of the main repository (not `main`).
- Use `flowstate finish` to automatically generate your PR description, or fill out the provided PR template manually.
- Link the original Issue in your PR description (e.g., `Fixes #12`).

### 7. Code Review
Maintainers will review your PR. We might request a few changes or ask clarifying questions. Once everything looks good, your PR will be approved and merged into the `develop` branch!

## 🌿 Branching Strategy
- **`main`**: Stable, production-ready code. Releases are cut from here.
- **`develop`**: The active development branch. All feature branches and PRs must target `develop`.

Welcome to the FlowState team! 🌊
