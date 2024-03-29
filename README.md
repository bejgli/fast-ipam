# Szakdolgozat munka
## Torhosi László - ZNDJKD - IPAM alkalmazás tervezése és fejlesztése

## Telepítés manuálisan:

### clone repository
```
git clone https://github.com/bejgli/fast-ipam.git
```

```
cd fast-ipam
```

### python virtuális környezet
```
python -m venv ./venv
```

```
source venv/bin/activate
```

### csomagok
```
pip install -r requirements/dev.txt
```

### inicializálás
```
./init_app.sh
```
Alapbeállítások:

belépési adatok: 
- email: admin@example.com
- jelszó: admin

adatbázis:
- sqlite:///ipam.db
   
Az első admin felhasználó a következő környezeti változókkal adható meg:
- SUPERUSER
- SUPERUSER_EMAIL
- SUPERUSER_PASSWORD

### adatbázis
SQLACLHEMY_DATABASE_URL változóval adható meg. Alapérték: SQLite.

Teljes elérési útvonal kell, pl:
- sqlite:///ipam.db vagy postgresql://ipam:admin@localhost:5432/ipam

### szerver indítás
```
uvicorn fastipam.main:app
```
alap port: 8000

további szerver beállítások: https://www.uvicorn.org/deployment/


## Telepítés containerként:
### clone repository
```
git clone https://github.com/bejgli/fast-ipam.git
```

```
cd fast-ipam
```

### container
```
podman build -t ipam 
```

```
podman run -d -p 8000:80 <CONTAINER-ID>
```


## Használat
### Web app
- localhost:8000/
- bejelentkezés az alap felhasználóval
- Admin/Users menüpont -> Felhasználók létrehozása, törlése, jogosultságok módosítása
- Network management/Subnets menüpont -> hálózatok létrehozása, módosítása, törlése
  - Kötelező mezők: name, ip
- Network management/Hosts menüpont -> hostok létrehozása, módosítása, törlése
  - Kötelező mezők: name, subnet id
  - Amennyiben nem adunk meg IP címet, a program automatikusan a legelső elérhetőt választja
- Account/Me menüpont -> saját név, email, jelszó módosítása
  - Az üresen hagyot mezők nem frissülnek
- Account/Logout -> kijelentkezés
### API
- localhost:8000/api
- Interaktív dokumentáció: localhost:8000/api/docs

        
## Tesztelt környezet:
- OS: Fedora 37
- Python: 3.11.3
- Adatbázis: SQLite, Postgresql



