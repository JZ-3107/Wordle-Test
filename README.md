# Wordle

## Virtual Enviroment

### Setup

```text
conda env create -f environment.yml --name myenv
```

### Generating the .yml file
```bash
conda env export --from-history --no-builds | grep -vE "^(name|prefix): " > environment.yml
```

```cmd
conda env export --from-history --no-builds | findstr /v "^name: ^prefix:" > environment.yml
```

```powershell
conda env export --from-history --no-builds | Where-Object { $_ -notmatch '^(name|prefix):' } | Set-Content environment.yml
```