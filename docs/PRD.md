# 🏍️ **PRD - Mapa de Estradas Épicas de Portugal**

**Versão:** 1.0  
**Data:** Outubro 2025  
**Autor:** Desenvolvedor Principal + Claude  
**Estado:** Ready for Implementation

---

## 📋 **Índice**

1. [Visão do Produto](#1-visão-do-produto)
2. [Objetivos e Métricas de Sucesso](#2-objetivos-e-métricas-de-sucesso)
3. [Público-Alvo e User Stories](#3-público-alvo-e-user-stories)
4. [Stack Tecnológica](#4-stack-tecnológica)
5. [Arquitetura do Sistema](#5-arquitetura-do-sistema)
6. [Schema da Base de Dados](#6-schema-da-base-de-dados)
7. [Funcionalidades MVP 1.0](#7-funcionalidades-mvp-10)
8. [Especificações Técnicas Detalhadas](#8-especificações-técnicas-detalhadas)
9. [UX/UI Guidelines](#9-uxui-guidelines)
10. [Roadmap de Implementação](#10-roadmap-de-implementação)
11. [Roadmap Futuro (Post-MVP)](#11-roadmap-futuro-post-mvp)
12. [Critérios de Aceitação](#12-critérios-de-aceitação)

---

## 1. Visão do Produto

### **Conceito**
Uma aplicação web que permite a motards descobrir, explorar e planear viagens pelas estradas mais espetaculares de Portugal (Continental, Madeira e Açores), visualizando-as num mapa interativo com métricas detalhadas relevantes para motociclistas.

### **Proposta de Valor Única**
- **Curadoria especializada:** Seleção manual das melhores estradas para motas
- **Métricas específicas para motards:** Curvas, retas, desnível, tipo de piso
- **Visualização imediata:** Ver trajeto completo animado no mapa
- **Export fácil:** GPX para GPS e link direto Google Maps
- **100% focado em Portugal:** Continental + Ilhas

### **Problema que Resolve**
Atualmente, motards têm que:
- Pesquisar em fóruns desorganizados
- Não sabem métricas objetivas das estradas
- Difícil comparar percursos
- Não há recurso centralizado e visual para estradas portuguesas

---

## 2. Objetivos e Métricas de Sucesso

### **Objetivos MVP 1.0**
1. ✅ Base de dados com 25-30 estradas icónicas
2. ✅ Visualização interativa e responsiva (mobile-first)
3. ✅ Métricas automáticas e precisas
4. ✅ Export GPX funcional
5. ✅ Deploy público em Vercel

### **Métricas de Sucesso (3 meses pós-lançamento)**
- **Uso:** 50+ visitantes únicos/mês
- **Engagement:** Tempo médio sessão >3min
- **Conversão:** >60% dos users clicam em pelo menos 1 estrada
- **Technical:** Page load <2s, 0 crashes
- **Custo:** €0/mês (free tiers)

---

## 3. Público-Alvo e User Stories

### **Persona Primária: "Miguel, o Motard Explorador"**
- **Idade:** 28-45 anos
- **Perfil:** Tem mota, faz viagens fins-de-semana, procura novas rotas
- **Comportamento:** Pesquisa online, usa Google Maps, grupos Facebook
- **Objetivo:** Descobrir estradas novas e planear próximo passeio

### **User Stories (MVP 1.0)**

```
Como motard explorador,
Quero ver uma lista de estradas espetaculares em Portugal
Para descobrir novos percursos que não conheço

Como motard experiente,
Quero ver métricas objetivas (curvas, altitude, distância)
Para escolher percursos adequados ao meu estilo de condução

Como utilizador mobile,
Quero ver o trajeto num mapa interativo
Para visualizar rapidamente se a estrada me interessa

Como planeador de viagens,
Quero exportar o trajeto para GPS ou abrir no Google Maps
Para navegar durante a viagem

Como motard curioso,
Quero filtrar estradas por região (Continental/Madeira/Açores)
Para focar na área onde vou viajar
```

---

## 4. Stack Tecnológica

### **Frontend**
| Tecnologia          | Versão | Propósito                 |
| ------------------- | ------ | ------------------------- |
| **React**           | 18+    | Framework UI              |
| **Vite**            | 5+     | Build tool & dev server   |
| **Mapbox GL JS**    | 3+     | Mapas interativos         |
| **React-Mapbox-GL** | 5+     | Wrapper React para Mapbox |
| **Tailwind CSS**    | 3+     | Styling responsivo        |
| **Axios**           | 1+     | HTTP requests             |
| **React Router**    | 6+     | Routing (se necessário)   |

### **Backend & Database**
| Tecnologia       | Propósito                               |
| ---------------- | --------------------------------------- |
| **Supabase**     | PostgreSQL gerido + PostGIS + APIs REST |
| **PostGIS**      | Extensão geoespacial (queries `ST_*`)   |
| **Python 3.11+** | Scripts de processamento dados          |

### **APIs Externas**
| API                 | Free Tier     | Uso                             |
| ------------------- | ------------- | ------------------------------- |
| **Mapbox**          | 50k loads/mês | Renderização mapas + elevação   |
| **OSM Overpass**    | Ilimitado     | Geometria estradas              |
| **Unsplash/Pexels** | 50 req/hora   | Fotos pontos interesse (futuro) |

### **Hosting & Deploy**
| Serviço      | Custo | Uso             |
| ------------ | ----- | --------------- |
| **Vercel**   | €0    | Frontend React  |
| **Supabase** | €0    | Backend + BD    |
| **GitHub**   | €0    | Controlo versão |

### **Ferramentas Desenvolvimento**
- **VS Code** (IDE)
- **Git** (controlo versão)
- **Claude Code** (agentic coding)
- **QGIS** (validação geometrias - opcional)

---

## 5. Arquitetura do Sistema

### **Diagrama de Alto Nível**

```
┌─────────────────────────────────────────────────┐
│          USER (Browser/Mobile)                  │
└────────────────┬────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────┐
│     FRONTEND (React + Mapbox GL JS)             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ Sidebar  │  │   Map    │  │ Details  │      │
│  │  Roads   │  │  View    │  │  Panel   │      │
│  └──────────┘  └──────────┘  └──────────┘      │
│                                                  │
│  Hosted: Vercel (CDN Global)                    │
└────────┬────────────────────────┬────────────────┘
         │                        │
         ↓                        ↓
┌────────────────┐      ┌────────────────────────┐
│  MAPBOX API    │      │   SUPABASE             │
│                │      │  ┌──────────────────┐  │
│ • Map tiles    │      │  │  PostgreSQL      │  │
│ • Elevation    │      │  │  + PostGIS       │  │
│ • Geocoding    │      │  │                  │  │
└────────────────┘      │  │  Tables:         │  │
                        │  │  • roads         │  │
                        │  │  • photos (fut)  │  │
                        │  │  • reviews (fut) │  │
                        │  └──────────────────┘  │
                        │                         │
                        │  REST API Auto-generated│
                        └─────────────────────────┘
                                   ↑
                                   │
                        ┌──────────┴──────────┐
                        │  PYTHON SCRIPTS     │
                        │  (Data Processing)  │
                        │                     │
                        │  • OSM data fetch   │
                        │  • Metrics calc     │
                        │  • DB population    │
                        └─────────────────────┘
                                   ↑
                                   │
                        ┌──────────┴──────────┐
                        │  OSM OVERPASS API   │
                        │  (Road geometries)  │
                        └─────────────────────┘
```

### **Fluxo de Dados**

#### **Setup Phase (One-time)**
```
1. Python Script → OSM Overpass API
   ↓ (Get road geometries)
2. Python Script → Mapbox Tilequery API
   ↓ (Get elevation data)
3. Python Script → Calcula métricas (curvas, retas)
   ↓
4. Python Script → Supabase PostgreSQL
   ↓ (INSERT road data)
5. Data ready ✅
```

#### **User Interaction (Runtime)**
```
1. User abre website
   ↓
2. React App → Supabase REST API
   ↓ GET /rest/v1/roads?select=*
3. Supabase → Returns JSON (lista estradas)
   ↓
4. React renderiza sidebar com lista
   ↓
5. User clica numa estrada (ex: N222)
   ↓
6. React → Supabase REST API
   ↓ GET /rest/v1/roads?id=eq.5
7. Supabase → Returns full road data + geometry
   ↓
8. React → Mapbox GL JS
   ↓ addSource() + addLayer()
9. Mapbox renderiza trajeto no mapa (animado)
   ↓
10. User vê métricas no painel lateral ✅
```

---

## 6. Schema da Base de Dados

### **Tabela: `roads`**

```sql
CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE roads (
    -- Identificadores
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,           -- Ex: "N222", "N2", "EM567"
    name VARCHAR(200) NOT NULL,                  -- Ex: "Estrada da Torre"
    description TEXT,                            -- Descrição breve da estrada
    
    -- Classificação
    region VARCHAR(20) NOT NULL                  -- "Continental", "Madeira", "Açores"
        CHECK (region IN ('Continental', 'Madeira', 'Açores')),
    category VARCHAR(50),                        -- "Serra", "Costa", "Montanha", etc (futuro)
    
    -- Geometria (PostGIS)
    geometry GEOMETRY(LINESTRING, 4326) NOT NULL,  -- Coordenadas GPS (WGS84)
    
    -- Pontos de início e fim
    start_point_name VARCHAR(100),               -- Ex: "Covilhã"
    start_lat DECIMAL(10, 7) NOT NULL,
    start_lon DECIMAL(10, 7) NOT NULL,
    end_point_name VARCHAR(100),                 -- Ex: "Torre"
    end_lat DECIMAL(10, 7) NOT NULL,
    end_lon DECIMAL(10, 7) NOT NULL,
    
    -- Métricas: Distância
    distance_km DECIMAL(10, 2) NOT NULL,         -- Distância total em km
    
    -- Métricas: Elevação
    elevation_max INTEGER,                       -- Altitude máxima (metros)
    elevation_min INTEGER,                       -- Altitude mínima (metros)
    elevation_gain INTEGER,                      -- Desnível acumulado subida (metros)
    elevation_loss INTEGER,                      -- Desnível acumulado descida (metros)
    
    -- Métricas: Curvas e Retas
    curve_count_total INTEGER,                   -- Total de curvas
    curve_count_gentle INTEGER,                  -- Curvas suaves (20-45°)
    curve_count_moderate INTEGER,                -- Curvas moderadas (45-90°)
    curve_count_sharp INTEGER,                   -- Curvas apertadas (>90°)
    straight_count INTEGER,                      -- Número de troços retos
    longest_straight_km DECIMAL(10, 2),          -- Reta mais comprida (km)
    
    -- Características da Estrada
    surface VARCHAR(50) DEFAULT 'asphalt',       -- "asphalt", "gravel", "unpaved", "mixed"
    surface_verified BOOLEAN DEFAULT FALSE,      -- Validado manualmente?
    road_condition VARCHAR(50),                  -- "excellent", "good", "fair", "poor" (futuro)
    
    -- Metadata
    data_source VARCHAR(50) DEFAULT 'osm',       -- "osm", "manual", "gps_trace"
    last_validated_at TIMESTAMP,                 -- Última validação manual
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Índices geoespaciais
    CONSTRAINT check_lat_start CHECK (start_lat BETWEEN -90 AND 90),
    CONSTRAINT check_lon_start CHECK (start_lon BETWEEN -180 AND 180),
    CONSTRAINT check_lat_end CHECK (end_lat BETWEEN -90 AND 90),
    CONSTRAINT check_lon_end CHECK (end_lon BETWEEN -180 AND 180)
);

-- Índices para performance
CREATE INDEX idx_roads_region ON roads(region);
CREATE INDEX idx_roads_code ON roads(code);
CREATE INDEX idx_roads_geometry ON roads USING GIST(geometry);

-- View para API (dados simplificados)
CREATE VIEW roads_list AS
SELECT 
    id,
    code,
    name,
    region,
    distance_km,
    elevation_max,
    curve_count_total,
    start_point_name,
    end_point_name
FROM roads
ORDER BY region, code;
```

### **Tabelas Futuras (MVP 1.5+)**

```sql
-- Fotos
CREATE TABLE photos (
    id SERIAL PRIMARY KEY,
    road_id INTEGER REFERENCES roads(id) ON DELETE CASCADE,
    url VARCHAR(500) NOT NULL,
    thumbnail_url VARCHAR(500),
    source VARCHAR(50) NOT NULL,         -- "unsplash", "pexels", "user_upload"
    source_attribution TEXT,             -- Créditos do autor
    latitude DECIMAL(10, 7),
    longitude DECIMAL(10, 7),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Reviews (requer auth)
CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    road_id INTEGER REFERENCES roads(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id),
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    visit_date DATE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- User favorites (requer auth)
CREATE TABLE favorites (
    user_id UUID REFERENCES auth.users(id),
    road_id INTEGER REFERENCES roads(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (user_id, road_id)
);
```

---

## 7. Funcionalidades MVP 1.0

### **7.1 Lista de Estradas (Sidebar)**

**Descrição:** Sidebar colapsável do lado esquerdo com lista de todas as estradas disponíveis.

**Comportamento:**
- Lista todas as estradas agrupadas por região (Continental, Madeira, Açores)
- Cada item mostra:
  - Código da estrada (ex: **N222**)
  - Nome (ex: Peso da Régua → Pinhão)
  - Distância (ex: 27km)
  - Ícone representativo da região
- Ao clicar numa estrada, o mapa centra-se nela e mostra o trajeto
- Search box no topo (buscar por código ou nome)
- Filtro por região (tabs ou dropdown)

**Estados:**
- Desktop: Sidebar sempre visível (300px width)
- Mobile: Sidebar colapsável (hamburger menu)
- Estrada selecionada: Highlighted na lista

---

### **7.2 Mapa Interativo**

**Descrição:** Mapa Mapbox ocupando a maior parte do viewport, mostrando Portugal completo inicialmente.

**Comportamento:**
- **Inicial:** Mapa centrado em Portugal (lat: 39.5, lon: -8.0, zoom: 6)
- **Ao clicar estrada:** 
  - Anima zoom para a estrada selecionada
  - Desenha trajeto animado (line animation 2-3s)
  - Marca ponto A (início) com pin verde
  - Marca ponto B (fim) com pin vermelho
- **Interações:**
  - Zoom in/out (scroll ou botões)
  - Pan (arrastar)
  - Hover sobre trajeto: Destaca linha
  - Click em ponto do trajeto: Mostra coordenadas (opcional)

**Estilo do Trajeto:**
- Cor: `#FF6B35` (laranja vibrante)
- Espessura: 4px
- Opacity: 0.9
- Ponto A (início): Pin verde
- Ponto B (fim): Pin vermelho

---

### **7.3 Painel de Detalhes da Estrada**

**Descrição:** Ao selecionar uma estrada, abre painel lateral (ou modal em mobile) com métricas detalhadas.

**Layout (Desktop):**
```
┌─────────────────────────────┐
│ N222 - PESO DA RÉGUA        │
│ ↓                           │
│ PINHÃO                      │
├─────────────────────────────┤
│ 📏 Distância: 27.3 km       │
│ 🏔️ Alt. Máx: 523m           │
│ 🏞️ Alt. Mín: 89m            │
│ 📈 Desnível: +434m          │
├─────────────────────────────┤
│ 🌀 Curvas                   │
│   • Total: 147              │
│   • Suaves: 82              │
│   • Moderadas: 54           │
│   • Apertadas: 11           │
├─────────────────────────────┤
│ ➡️ Retas                    │
│   • Total: 23               │
│   • Mais longa: 1.2 km      │
├─────────────────────────────┤
│ 🛣️ Tipo Piso: Alcatroado   │
│ ℹ️ (Não verificado)         │
├─────────────────────────────┤
│ [📥 Export GPX]             │
│ [🗺️ Abrir Google Maps]     │
└─────────────────────────────┘
```

**Ações:**
- **Export GPX:** Download ficheiro `.gpx` com todas as coordenadas
- **Google Maps:** Abre Google Maps com link para navegação (ponto A)

---

### **7.4 Export para GPX**

**Descrição:** Gerar ficheiro GPX padrão com todas as coordenadas da estrada.

**Formato GPX:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="Mapa Estradas PT">
  <metadata>
    <name>N222 - Peso da Régua a Pinhão</name>
    <desc>27.3km • 147 curvas • Alcatroado</desc>
  </metadata>
  <trk>
    <name>N222</name>
    <trkseg>
      <trkpt lat="41.1579" lon="-7.7538">
        <ele>89</ele>
      </trkpt>
      <trkpt lat="41.1582" lon="-7.7542">
        <ele>92</ele>
      </trkpt>
      <!-- ... mais pontos ... -->
    </trkseg>
  </trk>
</gpx>
```

**Implementação:**
- Frontend gera GPX client-side (biblioteca `togpx` ou similar)
- User clica "Export GPX" → download automático
- Nome ficheiro: `{road_code}_{date}.gpx` (ex: `N222_2025-10-13.gpx`)

---

### **7.5 Link Google Maps**

**Descrição:** Botão que abre Google Maps com ponto de início da estrada.

**Implementação:**
```javascript
const googleMapsUrl = `https://www.google.com/maps/dir/?api=1&destination=${road.start_lat},${road.start_lon}`;
window.open(googleMapsUrl, '_blank');
```

**Comportamento:**
- Abre em novo tab
- Google Maps automaticamente sugere rota do local atual do user até ponto A

---

### **7.6 Filtro por Região**

**Descrição:** Dropdown ou tabs para filtrar estradas por região.

**Opções:**
- 🇵🇹 **Todas** (default)
- 🏔️ **Continental**
- 🏝️ **Madeira**
- 🌋 **Açores**

**Comportamento:**
- Ao selecionar, sidebar mostra apenas estradas dessa região
- Mapa re-centra para região selecionada
- Contador: "12 estradas em Continental"

---

### **7.7 Responsividade (Mobile-First)**

**Breakpoints:**
```css
/* Mobile: <640px */
- Sidebar: Hidden (hamburger menu)
- Mapa: Full viewport
- Detalhes: Modal bottom-sheet

/* Tablet: 640px-1024px */
- Sidebar: Colapsável
- Mapa: 60% viewport
- Detalhes: Overlay lateral

/* Desktop: >1024px */
- Sidebar: Sempre visível (300px)
- Mapa: Restante viewport
- Detalhes: Panel lateral fixo
```

---

## 8. Especificações Técnicas Detalhadas

### **8.1 Obtenção de Dados do OSM**

#### **Tool: Overpass Turbo API**

**Endpoint:**
```
https://overpass-api.de/api/interpreter
```

**Query Example (N222):**
```python
import requests
import json

def get_road_from_osm(road_ref):
    """
    Busca geometria de uma estrada no OSM pelo seu ref (ex: "N 222")
    """
    overpass_url = "https://overpass-api.de/api/interpreter"
    
    # Query Overpass QL
    overpass_query = f"""
    [out:json][timeout:25];
    (
      way["ref"="{road_ref}"]["highway"];
      relation["ref"="{road_ref}"]["highway"];
    );
    out geom;
    """
    
    response = requests.post(overpass_url, data={'data': overpass_query})
    data = response.json()
    
    # Extrair coordenadas
    coordinates = []
    for element in data['elements']:
        if element['type'] == 'way':
            coords = [(node['lon'], node['lat']) for node in element.get('geometry', [])]
            coordinates.extend(coords)
    
    return coordinates

# Uso
coords_n222 = get_road_from_osm("N 222")
print(f"N222 tem {len(coords_n222)} pontos GPS")
```

**Notas:**
- OSM usa formato `"ref"="N 222"` (com espaço) para estradas nacionais
- Algumas estradas podem estar em múltiplos `ways` → precisa juntar
- Validar manualmente no [Overpass Turbo](https://overpass-turbo.eu/) antes

---

### **8.2 Cálculo de Métricas**

#### **8.2.1 Distância Total**

```python
from geopy.distance import geodesic

def calculate_total_distance(coordinates):
    """
    Calcula distância total seguindo as coordenadas GPS
    
    Args:
        coordinates: Lista de tuplos [(lon, lat), ...]
    
    Returns:
        float: Distância em km
    """
    total_distance = 0.0
    
    for i in range(len(coordinates) - 1):
        point1 = (coordinates[i][1], coordinates[i][0])  # (lat, lon)
        point2 = (coordinates[i+1][1], coordinates[i+1][0])
        
        distance = geodesic(point1, point2).kilometers
        total_distance += distance
    
    return round(total_distance, 2)
```

---

#### **8.2.2 Elevação (via Mapbox)**

```python
import requests
import time

MAPBOX_TOKEN = "your_mapbox_token_here"

def get_elevation_from_mapbox(lat, lon):
    """
    Obtém elevação de um ponto via Mapbox Tilequery API
    """
    url = f"https://api.mapbox.com/v4/mapbox.mapbox-terrain-v2/tilequery/{lon},{lat}.json"
    params = {
        "access_token": MAPBOX_TOKEN,
        "layers": "contour"
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    if data.get('features'):
        return data['features'][0]['properties'].get('ele', 0)
    return 0

def calculate_elevation_metrics(coordinates):
    """
    Calcula métricas de elevação para uma estrada
    
    Args:
        coordinates: Lista de tuplos [(lon, lat), ...]
    
    Returns:
        dict: {elevation_max, elevation_min, elevation_gain, elevation_loss}
    """
    # Amostra a cada 100m para não ultrapassar API limits
    sampled_coords = coordinates[::10]  # Pega 1 em cada 10 pontos
    
    elevations = []
    for lon, lat in sampled_coords:
        ele = get_elevation_from_mapbox(lat, lon)
        elevations.append(ele)
        time.sleep(0.05)  # Rate limiting (20 req/s max)
    
    # Calcula métricas
    elevation_max = max(elevations)
    elevation_min = min(elevations)
    
    # Calcula desnível acumulado
    elevation_gain = 0
    elevation_loss = 0
    
    for i in range(len(elevations) - 1):
        diff = elevations[i+1] - elevations[i]
        if diff > 0:
            elevation_gain += diff
        else:
            elevation_loss += abs(diff)
    
    return {
        'elevation_max': int(elevation_max),
        'elevation_min': int(elevation_min),
        'elevation_gain': int(elevation_gain),
        'elevation_loss': int(elevation_loss)
    }
```

---

#### **8.2.3 Quantidade de Curvas**

```python
import math

def calculate_bearing(point1, point2):
    """
    Calcula o bearing (direção) entre 2 pontos GPS
    
    Returns:
        float: Ângulo em graus (0-360)
    """
    lat1, lon1 = math.radians(point1[1]), math.radians(point1[0])
    lat2, lon2 = math.radians(point2[1]), math.radians(point2[0])
    
    dlon = lon2 - lon1
    
    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    
    initial_bearing = math.atan2(x, y)
    initial_bearing = math.degrees(initial_bearing)
    bearing = (initial_bearing + 360) % 360
    
    return bearing

def calculate_angle_difference(bearing1, bearing2):
    """
    Calcula diferença de ângulo entre 2 bearings
    """
    diff = abs(bearing2 - bearing1)
    if diff > 180:
        diff = 360 - diff
    return diff

def analyze_curves(coordinates, min_curve_angle=20):
    """
    Analisa curvas numa estrada
    
    Args:
        coordinates: Lista de tuplos [(lon, lat), ...]
        min_curve_angle: Ângulo mínimo para considerar curva (default: 20°)
    
    Returns:
        dict: {
            curve_count_total,
            curve_count_gentle,
            curve_count_moderate,
            curve_count_sharp,
            straight_count,
            longest_straight_km
        }
    """
    if len(coordinates) < 3:
        return None
    
    curves_gentle = 0    # 20-45°
    curves_moderate = 0  # 45-90°
    curves_sharp = 0     # >90°
    
    straights = []
    current_straight_distance = 0
    
    bearings = []
    for i in range(len(coordinates) - 1):
        bearing = calculate_bearing(coordinates[i], coordinates[i+1])
        bearings.append(bearing)
    
    # Analisa mudanças de direção
    for i in range(len(bearings) - 1):
        angle_change = calculate_angle_difference(bearings[i], bearings[i+1])
        
        if angle_change >= min_curve_angle:
            # É uma curva
            if angle_change < 45:
                curves_gentle += 1
            elif angle_change < 90:
                curves_moderate += 1
            else:
                curves_sharp += 1
            
            # Termina troço reto atual
            if current_straight_distance > 0:
                straights.append(current_straight_distance)
                current_straight_distance = 0
        else:
            # É reta - acumula distância
            point1 = (coordinates[i][1], coordinates[i][0])
            point2 = (coordinates[i+1][1], coordinates[i+1][0])
            segment_distance = geodesic(point1, point2).kilometers
            current_straight_distance += segment_distance
    
    # Última reta
    if current_straight_distance > 0:
        straights.append(current_straight_distance)
    
    total_curves = curves_gentle + curves_moderate + curves_sharp
    longest_straight = max(straights) if straights else 0
    
    return {
        'curve_count_total': total_curves,
        'curve_count_gentle': curves_gentle,
        'curve_count_moderate': curves_moderate,
        'curve_count_sharp': curves_sharp,
        'straight_count': len(straights),
        'longest_straight_km': round(longest_straight, 2)
    }
```

---

### **8.3 Script Completo de Processamento**

**Ficheiro: `scripts/process_roads.py`**

```python
#!/usr/bin/env python3
"""
Script para processar estradas e popular base de dados Supabase
"""

import os
import json
from supabase import create_client, Client
from dotenv import load_dotenv

# Importa funções anteriores
from osm_utils import get_road_from_osm
from metrics import (
    calculate_total_distance,
    calculate_elevation_metrics,
    analyze_curves
)

load_dotenv()

# Supabase config
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Lista de estradas para processar
ROADS_TO_PROCESS = [
    {
        "code": "N222",
        "name": "Peso da Régua → Pinhão",
        "region": "Continental",
        "osm_ref": "N 222",
        "start_point_name": "Peso da Régua",
        "end_point_name": "Pinhão",
        "description": "Uma das estradas mais bonitas da Europa, serpenteando pelo Douro"
    },
    {
        "code": "N2",
        "name": "Chaves → Faro",
        "region": "Continental",
        "osm_ref": "N 2",
        "start_point_name": "Chaves",
        "end_point_name": "Faro",
        "description": "A mítica Rota 66 portuguesa - 739km de Norte a Sul"
    },
    # ... adicionar todas as estradas
]

def process_single_road(road_info):
    """
    Processa uma estrada: busca dados OSM, calcula métricas, insere na BD
    """
    print(f"\n🛣️  Processando {road_info['code']} - {road_info['name']}")
    
    # 1. Buscar coordenadas do OSM
    print("   📡 Buscando dados do OSM...")
    coordinates = get_road_from_osm(road_info['osm_ref'])
    
    if not coordinates or len(coordinates) < 2:
        print(f"   ❌ Erro: Não foram encontradas coordenadas para {road_info['code']}")
        return False
    
    print(f"   ✅ {len(coordinates)} pontos GPS encontrados")
    
    # 2. Calcular distância
    print("   📏 Calculando distância...")
    distance_km = calculate_total_distance(coordinates)
    print(f"   ✅ Distância: {distance_km} km")
    
    # 3. Calcular elevação
    print("   🏔️  Calculando elevação (pode demorar)...")
    elevation_metrics = calculate_elevation_metrics(coordinates)
    print(f"   ✅ Elevação: {elevation_metrics['elevation_min']}m → {elevation_metrics['elevation_max']}m")
    
    # 4. Analisar curvas
    print("   🌀 Analisando curvas...")
    curve_metrics = analyze_curves(coordinates)
    print(f"   ✅ {curve_metrics['curve_count_total']} curvas detectadas")
    
    # 5. Preparar geometria para PostGIS (formato WKT)
    coords_wkt = ", ".join([f"{lon} {lat}" for lon, lat in coordinates])
    geometry_wkt = f"LINESTRING({coords_wkt})"
    
    # 6. Inserir na BD Supabase
    print("   💾 Inserindo na base de dados...")
    
    road_data = {
        "code": road_info['code'],
        "name": road_info['name'],
        "description": road_info.get('description', ''),
        "region": road_info['region'],
        "geometry": geometry_wkt,
        
        "start_point_name": road_info['start_point_name'],
        "start_lat": coordinates[0][1],
        "start_lon": coordinates[0][0],
        "end_point_name": road_info['end_point_name'],
        "end_lat": coordinates[-1][1],
        "end_lon": coordinates[-1][0],
        
        "distance_km": distance_km,
        
        **elevation_metrics,
        **curve_metrics,
        
        "surface": "asphalt",  # Default
        "surface_verified": False,
        "data_source": "osm"
    }
    
    try:
        result = supabase.table('roads').insert(road_data).execute()
        print(f"   ✅ {road_info['code']} inserida com sucesso (ID: {result.data[0]['id']})")
        return True
    except Exception as e:
        print(f"   ❌ Erro ao inserir: {e}")
        return False

def main():
    print("🚀 Iniciando processamento de estradas...")
    print(f"📊 Total de estradas a processar: {len(ROADS_TO_PROCESS)}\n")
    
    success_count = 0
    fail_count = 0
    
    for road in ROADS_TO_PROCESS:
        if process_single_road(road):
            success_count += 1
        else:
            fail_count += 1
    
    print("\n" + "="*50)
    print(f"✅ Processamento concluído!")
    print(f"   Sucesso: {success_count}")
    print(f"   Falhas: {fail_count}")
    print("="*50)

if __name__ == "__main__":
    main()
```

---

### **8.4 Frontend - Integração Mapbox**

**Componente React: `RoadMap.jsx`**

```jsx
import React, { useRef, useEffect, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';

mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_TOKEN;

const RoadMap = ({ selectedRoad }) => {
  const mapContainer = useRef(null);
  const map = useRef(null);
  const [lng, setLng] = useState(-8.0);
  const [lat, setLat] = useState(39.5);
  const [zoom, setZoom] = useState(6);

  // Inicializa mapa
  useEffect(() => {
    if (map.current) return;

    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/outdoors-v12',
      center: [lng, lat],
      zoom: zoom
    });

    map.current.on('load', () => {
      console.log('Mapa carregado');
    });
  }, []);

  // Atualiza quando estrada é selecionada
  useEffect(() => {
    if (!map.current || !selectedRoad) return;

    // Remove layers anteriores
    if (map.current.getLayer('route')) {
      map.current.removeLayer('route');
      map.current.removeSource('route');
    }

    // Converte WKT para GeoJSON
    const geojson = wktToGeoJSON(selectedRoad.geometry);

    // Adiciona source
    map.current.addSource('route', {
      type: 'geojson',
      data: geojson
    });

    // Adiciona layer com animação
    map.current.addLayer({
      id: 'route',
      type: 'line',
      source: 'route',
      layout: {
        'line-join': 'round',
        'line-cap': 'round'
      },
      paint: {
        'line-color': '#FF6B35',
        'line-width': 4,
        'line-opacity': 0.9
      }
    });

    // Anima linha (desenha progressivamente)
    animateLine(map.current, geojson);

    // Adiciona markers início/fim
    new mapboxgl.Marker({ color: '#10B981' })
      .setLngLat([selectedRoad.start_lon, selectedRoad.start_lat])
      .setPopup(new mapboxgl.Popup().setHTML(`<strong>Início:</strong> ${selectedRoad.start_point_name}`))
      .addTo(map.current);

    new mapboxgl.Marker({ color: '#EF4444' })
      .setLngLat([selectedRoad.end_lon, selectedRoad.end_lat])
      .setPopup(new mapboxgl.Popup().setHTML(`<strong>Fim:</strong> ${selectedRoad.end_point_name}`))
      .addTo(map.current);

    // Fit bounds para mostrar trajeto completo
    const bounds = new mapboxgl.LngLatBounds();
    geojson.geometry.coordinates.forEach(coord => bounds.extend(coord));
    map.current.fitBounds(bounds, { padding: 50, duration: 1500 });

  }, [selectedRoad]);

  return (
    <div ref={mapContainer} className="map-container h-full w-full" />
  );
};

// Helper: Anima desenho da linha
function animateLine(map, geojson) {
  let step = 0;
  const steps = 50;
  const coordinates = geojson.geometry.coordinates;
  const segmentLength = Math.ceil(coordinates.length / steps);

  const animate = () => {
    if (step >= steps) return;

    const currentCoords = coordinates.slice(0, (step + 1) * segmentLength);
    
    map.getSource('route').setData({
      type: 'Feature',
      geometry: {
        type: 'LineString',
        coordinates: currentCoords
      }
    });

    step++;
    setTimeout(animate, 50);
  };

  animate();
}

// Helper: Converte WKT para GeoJSON
function wktToGeoJSON(wkt) {
  // Remove "LINESTRING(" e ")"
  const coordsString = wkt.replace('LINESTRING(', '').replace(')', '');
  const coordPairs = coordsString.split(',');
  
  const coordinates = coordPairs.map(pair => {
    const [lon, lat] = pair.trim().split(' ').map(Number);
    return [lon, lat];
  });

  return {
    type: 'Feature',
    geometry: {
      type: 'LineString',
      coordinates: coordinates
    }
  };
}

export default RoadMap;
```

---

## 9. UX/UI Guidelines

### **9.1 Design System**

**Cores Principais:**
```css
:root {
  /* Brand Colors */
  --primary: #FF6B35;        /* Laranja vibrante - roads */
  --secondary: #004E89;      /* Azul escuro - mapas */
  --accent: #10B981;         /* Verde - start point */
  --danger: #EF4444;         /* Vermelho - end point */
  
  /* Neutrals */
  --bg-main: #FFFFFF;
  --bg-secondary: #F9FAFB;
  --text-primary: #111827;
  --text-secondary: #6B7280;
  --border: #E5E7EB;
  
  /* Regions */
  --region-continental: #3B82F6;
  --region-madeira: #F59E0B;
  --region-acores: #8B5CF6;
}
```

**Tipografia:**
```css
font-family: 'Inter', system-ui, sans-serif;

/* Headings */
h1: 2rem (32px), font-weight: 700
h2: 1.5rem (24px), font-weight: 600
h3: 1.25rem (20px), font-weight: 600

/* Body */
body: 1rem (16px), font-weight: 400
small: 0.875rem (14px), font-weight: 400
```

### **9.2 Layout Responsivo**

**Desktop (>1024px):**
```
┌─────────┬─────────────────────────────────┐
│         │                                 │
│ Sidebar │           Mapa                  │
│ (300px) │         (resto)                 │
│         │                                 │
│ Lista   │                                 │
│ Estradas│      [Trajeto renderizado]     │
│         │                                 │
│ [Search]│                                 │
│ [N222  ]│      Markers A→B                │
│ [N2    ]│                                 │
│ [...]   │                                 │
│         │                                 │
└─────────┴─────────────────────────────────┘
```

**Mobile (<640px):**
```
┌─────────────────────┐
│ [☰] Header          │  ← Hamburger menu
├─────────────────────┤
│                     │
│       Mapa          │
│    (full screen)    │
│                     │
│  [Trajeto visível]  │
│                     │
│  Markers A→B        │
│                     │
└─────────────────────┘
     ↓ (scroll)
┌─────────────────────┐
│  Detalhes Estrada   │  ← Bottom sheet
│  [collapse/expand]  │
└─────────────────────┘
```

### **9.3 Componentes Principais**

**RoadListItem (Sidebar):**
```jsx
<div className="road-item p-4 hover:bg-gray-50 cursor-pointer">
  <div className="flex justify-between items-start">
    <div>
      <span className="font-bold text-lg text-primary">N222</span>
      <p className="text-sm text-gray-600">Peso da Régua → Pinhão</p>
    </div>
    <span className="text-sm font-medium text-gray-500">27km</span>
  </div>
  <div className="flex gap-2 mt-2">
    <Badge>147 curvas</Badge>
    <Badge>523m ↑</Badge>
  </div>
</div>
```

**MetricsPanel (Detalhes):**
```jsx
<div className="metrics-panel bg-white shadow-lg rounded-lg p-6">
  <h2 className="text-2xl font-bold mb-4">N222</h2>
  
  <MetricRow icon="📏" label="Distância" value="27.3 km" />
  <MetricRow icon="🏔️" label="Alt. Máxima" value="523m" />
  
  <Divider />
  
  <h3 className="font-semibold mb-2">🌀 Curvas</h3>
  <ul className="space-y-1">
    <li>Total: <strong>147</strong></li>
    <li className="text-sm">Suaves: 82 • Moderadas: 54 • Apertadas: 11</li>
  </ul>
  
  <Divider />
  
  <div className="flex gap-2 mt-4">
    <Button variant="primary">📥 Export GPX</Button>
    <Button variant="secondary">🗺️ Google Maps</Button>
  </div>
</div>
```

---

## 10. Roadmap de Implementação

### **Fase 1: Setup Inicial (Semana 1)**

#### **Milestone 1.1: Ambiente de Desenvolvimento**
- [ ] Setup repositório Git
- [ ] Criar projeto React com Vite
- [ ] Instalar dependências (Mapbox GL, Tailwind, Axios, etc)
- [ ] Configurar Supabase
  - [ ] Criar projeto
  - [ ] Criar tabela `roads` com schema definido
  - [ ] Ativar PostGIS extension
- [ ] Setup variáveis ambiente (`.env`)
- [ ] README inicial

**Tempo estimado:** 2-3 horas

---

#### **Milestone 1.2: Script de Processamento Dados**
- [ ] Criar pasta `scripts/`
- [ ] Implementar `osm_utils.py` (fetch OSM data)
- [ ] Implementar `metrics.py` (cálculo curvas, distâncias)
- [ ] Implementar `elevation.py` (Mapbox Tilequery)
- [ ] Criar `process_roads.py` (script principal)
- [ ] Testar com 3 estradas piloto (N222, N2, N339)
- [ ] Validar dados no Supabase Dashboard

**Tempo estimado:** 8-10 horas

---

### **Fase 2: Frontend Base (Semana 2)**

#### **Milestone 2.1: Estrutura React + Mapa**
- [ ] Criar componente `RoadMap.jsx`
- [ ] Integrar Mapbox GL JS
- [ ] Mapa renderiza centrado em Portugal
- [ ] Configurar estilo `outdoors-v12`

**Tempo estimado:** 3-4 horas

---

#### **Milestone 2.2: Sidebar com Lista**
- [ ] Criar componente `Sidebar.jsx`
- [ ] Fetch estradas de Supabase (`GET /rest/v1/roads`)
- [ ] Renderizar lista de estradas
- [ ] Implementar search box básico
- [ ] Click em estrada → emit event para Mapa

**Tempo estimado:** 4-5 horas

---

#### **Milestone 2.3: Visualização Trajeto**
- [ ] Ao clicar estrada, fetch geometria completa
- [ ] Converter WKT → GeoJSON
- [ ] Renderizar trajeto no mapa
- [ ] Adicionar markers início/fim
- [ ] Implementar animação linha (desenho progressivo)
- [ ] Fit bounds para mostrar trajeto completo

**Tempo estimado:** 5-6 horas

---

### **Fase 3: Detalhes e Interações (Semana 3)**

#### **Milestone 3.1: Painel de Detalhes**
- [ ] Criar componente `RoadDetails.jsx`
- [ ] Layout das métricas (distância, elevação, curvas)
- [ ] Icons e formatação
- [ ] Responsividade (desktop vs mobile)

**Tempo estimado:** 4-5 horas

---

#### **Milestone 3.2: Export GPX**
- [ ] Instalar biblioteca GPX (`togpx` ou `@tmcw/togeojson`)
- [ ] Função: GeoJSON → GPX XML
- [ ] Botão download
- [ ] Nome ficheiro dinâmico (`{code}_{date}.gpx`)
- [ ] Testar com dispositivo GPS real

**Tempo estimado:** 3-4 horas

---

#### **Milestone 3.3: Link Google Maps**
- [ ] Botão "Abrir no Google Maps"
- [ ] Gerar URL: `google.com/maps/dir/?api=1&destination=...`
- [ ] Abrir em novo tab
- [ ] Testar em mobile

**Tempo estimado:** 1 hora

---

### **Fase 4: Filtros e Polish (Semana 4)**

#### **Milestone 4.1: Filtro por Região**
- [ ] Dropdown/tabs Continental/Madeira/Açores
- [ ] Filtrar lista sidebar
- [ ] Re-centrar mapa para região
- [ ] Contador estradas visíveis

**Tempo estimado:** 2-3 horas

---

#### **Milestone 4.2: Responsividade Mobile**
- [ ] Sidebar colapsável (hamburger menu)
- [ ] Bottom sheet para detalhes (mobile)
- [ ] Touch gestures no mapa
- [ ] Testar em iOS Safari e Android Chrome

**Tempo estimado:** 5-6 horas

---

#### **Milestone 4.3: Loading States & Error Handling**
- [ ] Skeleton loaders
- [ ] Mensagens erro (sem dados, API falha)
- [ ] Fallbacks
- [ ] Toast notifications

**Tempo estimado:** 3-4 horas

---

### **Fase 5: Conteúdo e Deploy (Semana 5)**

#### **Milestone 5.1: Processar Todas Estradas**
- [ ] Definir manualmente pontos A/B de cada estrada
- [ ] Rodar `process_roads.py` para 25-30 estradas
- [ ] Validar cada entrada no Supabase
- [ ] Correção manual de erros

**Tempo estimado:** 10-12 horas (trabalhoso!)

---

#### **Milestone 5.2: Testes Finais**
- [ ] Testes funcionais (cada funcionalidade)
- [ ] Testes cross-browser (Chrome, Firefox, Safari)
- [ ] Testes mobile (iOS, Android)
- [ ] Performance audit (Lighthouse)
- [ ] Correção bugs

**Tempo estimado:** 6-8 horas

---

#### **Milestone 5.3: Deploy**
- [ ] Deploy frontend para Vercel
- [ ] Configurar domínio (opcional)
- [ ] Setup analytics (opcional - Google Analytics)
- [ ] Soft launch (partilhar com amigos motards)
- [ ] Coletar feedback inicial

**Tempo estimado:** 2-3 horas

---

**TOTAL ESTIMADO:** ~60-80 horas (5-6 semanas part-time)

---

## 11. Roadmap Futuro (Post-MVP)

### **MVP 1.5 - Fotos & Partilha (Mês 2-3)**
- [ ] Integração API fotos (Unsplash/Pexels)
- [ ] Galeria fotos por estrada
- [ ] Botão "Partilhar" (link direto estrada)
- [ ] Meta tags OG para social media

### **MVP 2.0 - Comunidade (Mês 4-6)**
- [ ] Sistema autenticação (Supabase Auth)
- [ ] User profiles
- [ ] Reviews e comentários
- [ ] Upload fotos por users
- [ ] Sistema de favoritos

### **MVP 2.5 - Planeamento Avançado (Mês 7-9)**
- [ ] Planeamento rotas multi-estradas
- [ ] Comparação lado-a-lado (2-3 estradas)
- [ ] Filtros avançados (>50km, montanha, costa)
- [ ] Mapa de calor (estradas mais populares)

### **MVP 3.0 - Mobile App (Mês 10-12)**
- [ ] React Native app
- [ ] Navegação offline (mapas cached)
- [ ] Tracking GPS em tempo real
- [ ] Modo "riding" (UI simplificada)

---

## 12. Critérios de Aceitação

### **MVP 1.0 considerado "Done" quando:**

✅ **Funcionalidades Core:**
- [ ] 25+ estradas processadas e visíveis
- [ ] Mapa renderiza corretamente em qualquer device
- [ ] Trajeto anima suavemente ao selecionar estrada
- [ ] Métricas (distância, curvas, elevação) precisas
- [ ] Export GPX funciona 100%
- [ ] Link Google Maps abre corretamente

✅ **Performance:**
- [ ] Page load <2s (teste 3G)
- [ ] Mapbox tiles carregam <1s
- [ ] Scroll sidebar smooth (60fps)
- [ ] Zero crashes em 20 sessões teste

✅ **Responsividade:**
- [ ] Funciona iPhone SE (375px) até 4K
- [ ] Touch gestures funcionam em mobile
- [ ] Sidebar colapsável opera sem bugs

✅ **Qualidade Código:**
- [ ] Código comentado
- [ ] README com setup instructions
- [ ] `.env.example` com variáveis necessárias
- [ ] Git commits semânticos

✅ **Deploy:**
- [ ] Live em Vercel
- [ ] HTTPS ativo
- [ ] Sem erros console
- [ ] Analytics básico configurado (opcional)

---

## 📦 **Anexos**

### **A. Lista Completa de Estradas para MVP 1.0**

#### **Portugal Continental (22 estradas)**

**Norte:**
1. **N2** - Chaves → Faro (icónica - 739km)
2. **N103** - Viana do Castelo → Bragança
3. **EN13** - Viana do Castelo → Caminha
4. **N222** - Peso da Régua → Pinhão (TOP Europa)
5. **N304** - Serra do Marão (Vila Real → Amarante)
6. **N101** - Gerês → Braga
7. **N308** - Serra da Freita
8. **N108** - Bragança → Miranda do Douro
9. **N221** - Estrada da Barca d'Alva
10. **Estrada do Mezio** - Off-road Gerês

**Centro:**
11. **N230** - Aveiro → Covilhã
12. **N339** - Covilhã → Torre (1993m altitude!)
13. **N17** - Serra da Estrela (Covilhã → Seia)
14. **N236** - Serra da Lousã
15. **N342** - Portas de Ródão → Castelo Branco
16. **IC8** - Coimbra → Castelo Branco (troços sinuosos)

**Lisboa & Oeste:**
17. **N247** - Estrada Atlântica (Cascais → Nazaré)
18. **N118** - Montijo → Alpalhão
19. **N246-1** - Marvão ↔ Castelo de Vide

**Sul:**
20. **N267** - São Marcos da Serra → Monchique
21. **N124** - Portimão → Alcoutim
22. **N383** - Tróia → Comporta
23. **N123** - Alentejo profundo
24. **N266** - Costa Vicentina
25. **N268** - Vale do Guadiana
26. **N232** - Sabugal → Guarda
27. **EM567** - Estrada Enforca-cães

#### **Madeira (3 estradas)**
28. **ER101** - Via Rápida (Funchal → São Vicente)
29. **ER110** - Estrada da Encumeada
30. **ER228** - Paul da Serra

#### **Açores (2 estradas)**
31. **Estrada da Lagoa do Fogo** (São Miguel)
32. **Estrada da Caldeira** (Faial)

**TOTAL: 32 estradas**

---

### **B. Estrutura de Pastas Projeto**

```
road-explorer/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Map/
│   │   │   │   ├── RoadMap.jsx
│   │   │   │   └── MapControls.jsx
│   │   │   ├── Sidebar/
│   │   │   │   ├── Sidebar.jsx
│   │   │   │   ├── RoadList.jsx
│   │   │   │   ├── RoadListItem.jsx
│   │   │   │   └── SearchBox.jsx
│   │   │   ├── Details/
│   │   │   │   ├── RoadDetails.jsx
│   │   │   │   ├── MetricsPanel.jsx
│   │   │   │   └── ActionButtons.jsx
│   │   │   └── UI/
│   │   │       ├── Button.jsx
│   │   │       ├── Badge.jsx
│   │   │       ├── Modal.jsx
│   │   │       └── Loader.jsx
│   │   ├── hooks/
│   │   │   ├── useRoads.js
│   │   │   ├── useSupabase.js
│   │   │   └── useMapbox.js
│   │   ├── utils/
│   │   │   ├── geoUtils.js       # WKT↔GeoJSON converters
│   │   │   ├── gpxExport.js      # GPX generation
│   │   │   └── formatters.js     # Number, date formatters
│   │   ├── services/
│   │   │   └── api.js            # Supabase client
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── public/
│   ├── .env.example
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
│
├── scripts/                      # Python data processing
│   ├── osm_utils.py
│   ├── metrics.py
│   ├── elevation.py
│   ├── process_roads.py
│   ├── roads_data.json           # Manual definitions
│   ├── requirements.txt
│   └── .env.example
│
├── docs/
│   ├── PRD.md                    # Este documento
│   ├── API_DOCUMENTATION.md
│   └── DEPLOYMENT_GUIDE.md
│
├── .github/
│   └── workflows/
│       └── deploy.yml            # CI/CD
│
├── .gitignore
├── README.md
└── LICENSE
```

---

### **C. Variáveis de Ambiente**

**`.env.example` (Frontend):**
```bash
VITE_MAPBOX_TOKEN=pk.your_mapbox_public_token_here
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key_here
```

**`.env.example` (Scripts Python):**
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_service_role_key_here
MAPBOX_TOKEN=pk.your_mapbox_token_here
```

---

### **D. Dependências Principais**

**Frontend (`package.json`):**
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "mapbox-gl": "^3.0.0",
    "react-map-gl": "^7.1.0",
    "@supabase/supabase-js": "^2.38.0",
    "axios": "^1.6.0",
    "togpx": "^0.5.5"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "tailwindcss": "^3.4.0",
    "@vitejs/plugin-react": "^4.2.0"
  }
}
```

**Python (`requirements.txt`):**
```txt
requests==2.31.0
geopy==2.4.1
python-dotenv==1.0.0
supabase==2.0.0
```