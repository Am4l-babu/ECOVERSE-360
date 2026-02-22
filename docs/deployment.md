# Deployment Guide — Ecoverse 360

---

## Quick Deploy (Docker Compose)

```bash
# 1. Clone the repo
git clone https://github.com/your-org/ecoverse-360.git
cd ecoverse-360

# 2. Create environment file
cp backend/.env.example backend/.env

# 3. Edit .env — IMPORTANT: change JWT_SECRET_KEY
notepad backend/.env

# 4. Launch all services
docker compose up -d

# 5. Verify
docker compose ps
curl http://localhost:8000/health
```

### Services

| Service | Internal Port | External Port | Health Check |
|---------|--------------|---------------|-------------|
| Backend (FastAPI) | 8000 | 8000 | `GET /health` |
| Frontend (Next.js) | 3000 | 3000 | — |
| PostgreSQL | 5432 | 5432 | `pg_isready` |
| Redis | 6379 | 6379 | `redis-cli ping` |
| Mosquitto (MQTT) | 1883, 9001 | 1883, 9001 | — |

---

## Manual Deployment

### Prerequisites

- Python 3.12+
- Node.js 20+
- PostgreSQL 16
- Redis 7
- Eclipse Mosquitto 2

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Apply database schema
psql -U ecoverse -d ecoverse_db -f ../database/schema.sql
psql -U ecoverse -d ecoverse_db -f ../database/seed_data.sql

# Run with uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Frontend

```bash
cd frontend
npm install
npm run build
npm start
# → listening on http://localhost:3000
```

### Mosquitto

```bash
# Install
sudo apt install mosquitto mosquitto-clients

# Use our config (or copy to /etc/mosquitto/)
mosquitto -c docker/mosquitto/mosquitto.conf
```

---

## Production Configuration

### Environment Variables

Create `backend/.env`:

```env
# Database
DATABASE_URL=postgresql+asyncpg://ecoverse:STRONG_PASSWORD@db-host:5432/ecoverse_db

# Redis
REDIS_URL=redis://:REDIS_PASSWORD@redis-host:6379/0

# MQTT
MQTT_BROKER_HOST=mqtt-host
MQTT_BROKER_PORT=1883

# Security — CHANGE THESE
JWT_SECRET_KEY=your-256-bit-random-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# CORS
CORS_ORIGINS=["https://ecoverse.campus.edu"]
```

### Reverse Proxy (Nginx)

```nginx
server {
    listen 443 ssl http2;
    server_name ecoverse.campus.edu;

    ssl_certificate     /etc/ssl/ecoverse.crt;
    ssl_certificate_key /etc/ssl/ecoverse.key;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Rate limiting
        limit_req zone=api burst=20 nodelay;
    }

    # WebSocket (future)
    location /ws/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}

# Rate limit zone
limit_req_zone $binary_remote_addr zone=api:10m rate=100r/m;
```

### PostgreSQL Hardening

```sql
-- Create dedicated user
CREATE USER ecoverse WITH PASSWORD 'STRONG_PASSWORD';
CREATE DATABASE ecoverse_db OWNER ecoverse;

-- Restrict permissions
REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO ecoverse;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO ecoverse;

-- Enable SSL
-- In postgresql.conf:
-- ssl = on
-- ssl_cert_file = '/etc/ssl/server.crt'
-- ssl_key_file = '/etc/ssl/server.key'
```

### Mosquitto Authentication

Edit `docker/mosquitto/mosquitto.conf`:

```conf
listener 1883
allow_anonymous false
password_file /mosquitto/config/passwd

listener 9001
protocol websockets
```

Create password file:

```bash
mosquitto_passwd -c /mosquitto/config/passwd ecoverse
# Enter password when prompted
```

---

## Monitoring

### Health Checks

```bash
# Backend
curl http://localhost:8000/health
# {"status": "healthy", "version": "1.0.0"}

# PostgreSQL
pg_isready -h localhost -p 5432 -U ecoverse

# Redis
redis-cli ping

# Mosquitto
mosquitto_sub -t '$SYS/broker/uptime' -C 1
```

### Logging

Backend logs to stdout (Docker captures them):

```bash
# View backend logs
docker compose logs -f backend

# View all logs
docker compose logs -f
```

### Backup

```bash
# Database backup
docker compose exec postgres pg_dump -U ecoverse ecoverse_db > backup_$(date +%Y%m%d).sql

# Automated daily backup (crontab)
0 2 * * * docker compose exec -T postgres pg_dump -U ecoverse ecoverse_db | gzip > /backups/ecoverse_$(date +\%Y\%m\%d).sql.gz
```

---

## Scaling

### Horizontal Backend Scaling

```yaml
# docker-compose.override.yml
services:
  backend:
    deploy:
      replicas: 3
```

Add a load balancer (Nginx upstream) in front of backend replicas.

### Database Read Replicas

For high read throughput, configure PostgreSQL streaming replication and point read-heavy queries to replicas.

### MQTT Clustering

For 10K+ concurrent IoT devices, deploy Mosquitto in bridge mode or switch to EMQX/VerneMQ cluster.

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Backend won't start | Check `DATABASE_URL` in `.env`; ensure PostgreSQL is running |
| MQTT not connecting | Verify Mosquitto is up: `mosquitto_sub -t '#' -v` |
| Schema not applied | Run `schema.sql` manually: `psql -f database/schema.sql` |
| JWT errors | Ensure `JWT_SECRET_KEY` is set and consistent across restarts |
| CORS errors | Add your frontend URL to `CORS_ORIGINS` in `.env` |
| Port conflicts | Change ports in `docker-compose.yml` or stop conflicting services |
