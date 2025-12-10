1. Scopul lucrării
În acest laborator, aplicația dezvoltată în Laboratorul 2 – Web Proxy pentru Data-Warehouse a fost migrată pe un server VPS. Infrastructura este containerizată cu Docker, orchestrată cu Docker Compose, iar accesul extern se face prin Nginx, configurat ca reverse proxy pe portul 80.

Lucrarea demonstrează:
Utilizarea unui VPS ca mediu de execuție.
Migrarea unei aplicații existente către acest mediu.
Configurarea serviciilor printr-un reverse proxy.
Testarea accesului local și extern prin IP public.

2. Arhitectura sistemului
Arhitectura include:
- Nginx ca punct de acces public.
- Serviciul Web Proxy (FastAPI) care gestionează load balancing și caching.
- Două instanțe Data-Warehouse (DW1, DW2) cu stocare în memorie.
- Client extern → Nginx → Proxy FastAPI → DW1 / DW2

3. Structura proiectului
lab3-cloud-vps-web-proxy/
│
├── app/
│   ├── requirements.txt
│   ├── dw_server.py
│   └── proxy_server.py
│
└── deploy/
    ├── Dockerfile.dw
    ├── Dockerfile.proxy
    ├── docker-compose.prod.yml
    └── nginx/
        └── nginx.conf

4. Demonstrarea funcționalităților
4.1. POST – creare employee (local, din VPS)
curl -X POST http://localhost/employees \
  -H "Content-Type: application/json" \
  -d '{"name":"Alice","role":"Dev","salary":15000}'
Răspuns:
{"status":"ok","id":1}

4.2. GET – listare employees (local)
curl "http://localhost/employees?offset=0&limit=10&format=json"
Exemplu răspuns:
[
  {"id":1,"name":"Alice","role":"Dev","salary":15000.0}
]

4.3. Acces extern prin IP public
curl "http://<IP_PUBLIC_VPS>/employees?offset=0&limit=10&format=json"
Afișarea datelor confirmă că serviciul este accesibil din Internet.

4.4. Observații tehnice
DW1 și DW2 funcționează independent, fiecare având propria memorie.
Proxy-ul FastAPI distribuie cererile între noduri (round-robin).
Nginx expune un singur endpoint către exterior.
Lipsa replicării face ca răspunsurile să depindă de nodul selectat – comportament normal în sisteme distribuite.

5. Legătura cu cerințele laboratorului
Utilizare Cloud Provider
Aplicația rulează pe un VPS public (IP: 161.97.166.85) și este accesibilă la:
http://161.97.166.85/employees
Migrare aplicație existentă
Componentele din Lab 2 au fost convertite în imagini Docker și rulate în containere pe VPS.
Reverse Proxy
Nginx gestionează traficul extern.
Proxy-ul FastAPI asigură load balancing și caching.
Scalabilitate
DW1 și DW2 simulează un cluster distribuit cu stocare independentă.

6. Concluzii
Lucrarea a realizat:
- migrarea aplicației din Lab 2 pe VPS,
- containerizarea și orchestrarea serviciilor cu Docker Compose,
- expunerea sistemului prin Nginx,
- testarea funcționalității prin cereri locale și externe,
- demonstrarea mecanismelor de load balancing, caching și procesare distribuită.
Arhitectura obținută reproduce un model utilizat în aplicații moderne bazate pe microservicii și gateway-uri API.
