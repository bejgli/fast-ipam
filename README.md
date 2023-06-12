# Szakdolgozat munka
## ZNDJKD

# Telepítés:
    1. clone
        - `git clone https://github.com/bejgli/fast-ipam.git`
        - `cd fast-ipam`
    2. python virtuális környezet
        - `python -m venv ./venv`
        - `source venv/bin/active`
    3. csomagok
        - `pip install -r requirements/dev.txt`
    4. szerver
        - `uvicorn fastipam.main:app`
        - további opciók https://www.uvicorn.org/deployment/

# Tesztelt környezet:
    - Fedora 37
    - Python 3.11.3




