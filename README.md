---

# PAD – Laborator 3 (2025)

Migrare aplicație Web Proxy + Data-Warehouse pe VPS

---

## 1. Scopul lucrării

În acest laborator, aplicația realizată în **Laboratorul 2 – Web Proxy pentru Data-Warehouse** a fost migrată pe un **server VPS**. Infrastructura rulează în containere Docker, orchestratată prin Docker Compose, iar accesul extern este asigurat prin **Nginx** configurat ca reverse proxy pe portul 80.

Lucrarea demonstrează:

* utilizarea unui VPS ca mediu de execuție;
* migrarea unei aplicații existente în acest mediu;
* configurarea serviciilor prin reverse proxy;
* accesarea aplicației local și extern prin IP public.

---

## 2. Arhitectura sistemului

Componentele utilizate:

* **Nginx** – punct unic de acces public;
* **Proxy FastAPI** – load balancing și caching;
* **DW1 / DW2** – noduri Data-Warehouse cu stocare în memorie.

Fluxul cererilor:

```
Client extern → Nginx → Proxy FastAPI → DW1 / DW2
```

---

## 3. Structura proiectului

```
lab3-cloud-vps-web-proxy/
│
├── app/
│   ├── requirements.txt        # dependințe Python
│   ├── dw_server.py            # server Data-Warehouse
│   └── proxy_server.py         # reverse proxy FastAPI
│
└── deploy/
    ├── Dockerfile.dw           # imagine DW (dw1 și dw2)
    ├── Dockerfile.proxy        # imagine Web Proxy
    ├── docker-compose.prod.yml # orchestrare containere
    └── nginx/
        └── nginx.conf          # configurare Nginx (port 80)
```

---

## 4. Demonstrarea funcționalităților

### 4.1. Creare employee (POST, local)

```
curl -X POST http://localhost/employees \
  -H "Content-Type: application/json" \
  -d '{"name":"Alice","role":"Dev","salary":15000}'
```

Răspuns:

```
{"status":"ok","id":1}
```

### 4.2. Listare employees (GET, local)

```
curl "http://localhost/employees?offset=0&limit=10&format=json"
```

Răspuns:

```
[
  {"id":1,"name":"Alice","role":"Dev","salary":15000.0}
]
```

### 4.3. Acces extern prin IP public

```
curl "http://<IP_PUBLIC_VPS>/employees?offset=0&limit=10&format=json"
```

Serviciul răspunde corect din Internet.

### 4.4. Observații tehnice

* DW1 și DW2 rulează independent, fiecare cu propriile date.
* Proxy-ul FastAPI folosește **round-robin** pentru distribuirea cererilor.
* Nginx expune un singur endpoint public.
* Lipsa replicării duce la răspunsuri diferite în funcție de DW-ul selectat, comportament tipic în sisteme distribuite.

---

## 5. Legătura cu cerințele laboratorului

### Utilizare Cloud Provider

Aplicația rulează pe VPS-ul cu IP: **161.97.166.85**
Endpoint public:

```
http://161.97.166.85/employees
```

### Migrare aplicație existentă

Componentele din Lab 2 au fost transformate în imagini Docker și rulate pe VPS.

### Reverse Proxy

* Nginx gestionează toate cererile externe.
* Proxy-ul FastAPI efectuează load balancing și caching.

### Scalabilitate

DW1 și DW2 simulează un cluster distribuit cu stocare separată în memorie.

---

## 6. Concluzii

Lucrarea a realizat:

* migrarea aplicației din Lab 2 pe VPS;
* containerizarea serviciilor și orchestrarea cu Docker Compose;
* expunerea sistemului prin Nginx;
* validarea funcționalității prin teste locale și externe;
* demonstrarea mecanismelor de load balancing, caching și procesare distribuită.

Arhitectura obținută reproduce structuri utilizate în sisteme moderne bazate pe microservicii și API Gateway.

---
