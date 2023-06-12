# Szakdolgozat munka
## ZNDJKD

## Telepítés:

1. clone repository
```
git clone https://github.com/bejgli/fast-ipam.git
```

```
cd fast-ipam
```

2. python virtuális környezet
```
python -m venv ./venv
```

```
source venv/bin/active
```

3. csomagok
```
pip install -r requirements/dev.txt
```

4. inicializálás
```
./init_app.sh
```
Az első admin felhasználó a következő környezeti változókkal adható meg:
- SUPERUSER
- SUPERUSER_EMAIL
- SUPERUSER_PASSWORD

Változók nélkül az alap felhasználó az alábbi email címmel és jelszóval érhető el:
- admin@example.com
- admin

5. szerver
```
uvicorn fastipam.main:app
```

további szerver beállítások: https://www.uvicorn.org/deployment/
        
## Tesztelt környezet:
    - Fedora 37
    - Python 3.11.3




