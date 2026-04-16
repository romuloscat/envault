# envault

A CLI tool to manage and encrypt environment variables across multiple projects.

---

## Installation

```bash
pip install envault
```

Or with pipx:

```bash
pipx install envault
```

---

## Usage

Initialize envault in your project:

```bash
envault init
```

Add and encrypt an environment variable:

```bash
envault set API_KEY "my-secret-key"
```

Retrieve a variable:

```bash
envault get API_KEY
```

Export all variables to a `.env` file:

```bash
envault export --output .env
```

Switch between projects:

```bash
envault use my-other-project
```

Variables are encrypted using AES-256 and stored locally in `~/.envault/`.

---

## License

This project is licensed under the [MIT License](LICENSE).