# IT Operations Analytics MVP

Sistema de análisis de operaciones IT con IA integrada para evaluación automática de tickets, SLAs y satisfacción de usuario.

## 🚀 Quick Start

### Prerrequisitos
- Docker y Docker Compose
- Node.js 18+ (para desarrollo frontend)
- Python 3.11+ (para desarrollo backend)

### Instalación

1. **Clonar y configurar**
```bash
cd it-ops-analytics-mvp
cp .env.example .env
# Editar .env con tus claves API
```

2. **Levantar servicios**
```bash
docker-compose up -d
```

3. **Verificar instalación**
- Backend API: http://localhost:8000/docs
- Frontend: http://localhost:3000
- Adminer (DB): http://localhost:8080

### Servicios

| Servicio | Puerto | URL |
|----------|--------|-----|
| Backend API | 8000 | http://localhost:8000 |
| Frontend | 3000 | http://localhost:3000 |
| MySQL | 3306 | localhost:3306 |
| Redis | 6379 | localhost:6379 |
| Adminer | 8080 | http://localhost:8080 |

### APIs Disponibles

#### EazyBI Integration
- `GET /api/v1/data/sla-overview` - SLA metrics
- `GET /api/v1/data/ticket-creation` - Ticket creation analysis
- `GET /api/v1/data/satisfaction` - User satisfaction metrics

#### AI Analysis
- `POST /api/v1/analysis/evaluate` - Analyze data with AI
- `GET /api/v1/analysis/reports` - Generated reports
- `POST /api/v1/analysis/user-input` - Add user insights

## 🏗️ Arquitectura

```
Frontend (Next.js)
     ↓
Backend API (FastAPI)
     ↓
MySQL + Redis
     ↓
EazyBI APIs + OpenAI
```

## 📊 Desarrollo

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Base de datos
```bash
# Conectar a MySQL
mysql -h localhost -u it_ops -p it_operations

# Ver logs
docker-compose logs mysql
```

## 🔧 Configuración Producción

1. Cambiar contraseñas en `.env`
2. Configurar SSL certificates
3. Usar `docker-compose.prod.yml`
4. Setup monitoring y backups

## 📈 Métricas Clave

- **SLA Compliance**: P1 < 1h, P2 < 2h
- **Satisfacción**: ≥ 4.7/5
- **Completitud datos**: > 95%
- **Tiempo análisis IA**: < 5s
