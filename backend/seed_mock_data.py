"""
Script para llenar la base de datos con datos de ejemplo (mock data)
Sin consumir tokens de OpenAI/Anthropic
"""

from datetime import datetime, timedelta
import random
from uuid import uuid4
from supabase import create_client
import os
from dotenv import load_dotenv
import requests

load_dotenv()

# Datos mock realistas sobre noticias colombianas
MOCK_THREADS = [
    {
        "title_id": "@ReformaTributaria2026",
        "display_title": "ÚLTIMA HORA: Congreso aprueba reforma tributaria en debate madrugador",
        "summary": "En una sesión extraordinaria que se extendió hasta las 3 AM de hoy, el Congreso aprobó en primer debate la reforma tributaria 2026 con 78 votos a favor. La propuesta busca recaudar $50 billones mediante nuevos impuestos a bebidas azucaradas y ajustes al impuesto de renta empresarial. Gremios empresariales anunciaron que evaluarán acciones legales. El debate pasa ahora al Senado donde se esperan modificaciones. Ministro de Hacienda celebró el avance como 'histórico para el país'.",
        "trending_score": 0.98,
    },
    {
        "title_id": "@DólarDispara",
        "display_title": "Dólar se dispara a $4.920 en apertura tras anuncios de la Fed",
        "summary": "La divisa estadounidense abrió hoy en $4.920, un nuevo máximo histórico impulsado por declaraciones de la Reserva Federal sobre posibles alzas de tasas. En las primeras dos horas de operación, el peso perdió 2.3% de su valor. El Banco de la República convocó reunión de emergencia para evaluar intervención. Importadores suspendieron órdenes de compra mientras exportadores anticipan mejores márgenes. Analistas prevén mayor volatilidad esta semana.",
        "trending_score": 0.96,
    },
    {
        "title_id": "@TransMetroMedellín",
        "display_title": "Metro de Medellín inaugurará tres nuevas estaciones que beneficiarán 500 mil personas",
        "summary": "El Metro de Medellín anunció la apertura de tres nuevas estaciones en la Línea B que conectarán municipios del sur del Valle de Aburrá. La obra, que costó $2.3 billones, beneficiará directamente a medio millón de personas y reducirá tiempos de desplazamiento hasta en 40 minutos. Las estaciones incluirán zonas comerciales, parqueaderos inteligentes y conexión con rutas alimentadoras. La inauguración está prevista para marzo de 2025.",
        "trending_score": 0.88,
    },
    {
        "title_id": "@ParoCampesino",
        "display_title": "URGENTE: Campesinos bloquean vías principales en 8 departamentos",
        "summary": "Desde las 5 AM de hoy, organizaciones campesinas iniciaron bloqueos en vías principales de Boyacá, Cundinamarca, Tolima y otros 5 departamentos. Más de 15 mil agricultores protestan por incumplimiento de subsidios prometidos. La vía Bogotá-Tunja está completamente cerrada con filas de hasta 20 kilómetros. TransMilenio reporta desabastecimiento en frutas y verduras. El Gobierno envió comisiones de paz a negociar pero líderes campesinos exigen presencia del ministro. Policía reforzó presencia en puntos críticos.",
        "trending_score": 0.94,
    },
    {
        "title_id": "@LuisDíazGol",
        "display_title": "Luis Díaz marca triplete y Liverpool vence 4-1 al Manchester City",
        "summary": "El colombiano Luis Díaz brilló esta madrugada con tres goles en la victoria del Liverpool 4-1 sobre Manchester City en Anfield. El primer gol llegó a los 8 minutos, seguido por un doblete en el segundo tiempo que selló el marcador. Con esta actuación, Díaz se convierte en el máximo goleador colombiano en la Premier League esta temporada con 14 anotaciones. Las redes sociales explotaron con celebraciones desde Colombia. Liverpool consolida liderato a 7 puntos del segundo lugar.",
        "trending_score": 0.97,
    },
    {
        "title_id": "@CaféColombianoExportaciones",
        "display_title": "Exportaciones de café colombiano crecen 23% impulsadas por demanda asiática",
        "summary": "La Federación Nacional de Cafeteros reportó un crecimiento histórico del 23% en exportaciones durante el primer trimestre. China, Japón y Corea del Sur aumentaron sus compras significativamente, posicionando a Colombia como el tercer exportador mundial de café especial. Los precios internacionales favorables y la calidad del grano colombiano impulsaron ventas por US$1.200 millones. Caficultores celebran mejores ingresos tras años difíciles.",
        "trending_score": 0.85,
    },
    {
        "title_id": "@ViviendaNueva",
        "display_title": "Lanzamiento de 100 mil viviendas gratuitas para familias vulnerables en 2025",
        "summary": "El Ministerio de Vivienda anunció la construcción de 100 mil viviendas de interés social prioritario en 32 ciudades. El programa, con inversión de $15 billones, beneficiará a familias con ingresos inferiores a dos salarios mínimos. Proyectos incluyen apartamentos ecológicos con paneles solares y recolección de agua lluvia. Constructoras privadas se unieron mediante esquema de subsidios. Entregas iniciarán en junio en Cali, Barranquilla y Cartagena.",
        "trending_score": 0.84,
    },
    {
        "title_id": "@InflaciónEnero",
        "display_title": "Inflación de enero sorprende al ubicarse en 0.8%, la más baja en dos años",
        "summary": "El DANE reportó una inflación mensual de 0.8% para enero, la cifra más baja desde 2023. La desaceleración se atribuyó a menores precios en alimentos, combustibles y servicios públicos. La inflación anual se ubicó en 5.2%, acercándose a la meta del Banco de la República. Analistas prevén posibles recortes en tasas de interés en los próximos meses, lo que dinamizaría el crédito y la economía.",
        "trending_score": 0.82,
    },
    {
        "title_id": "@TurismoCartagena",
        "display_title": "Cartagena rompe récord con 2 millones de turistas en temporada alta",
        "summary": "La ciudad amurallada recibió más de 2 millones de visitantes entre diciembre y febrero, superando cifras pre-pandemia. Turistas estadounidenses, europeos y latinoamericanos impulsaron ocupación hotelera del 95%. Sector turístico generó 15 mil empleos temporales y movió $800 mil millones en la economía local. Autoridades reforzaron seguridad y mejoraron infraestructura turística. Cartagena consolida posición como destino caribeño premium.",
        "trending_score": 0.81,
    },
    {
        "title_id": "@TecnologíaBogotá",
        "display_title": "Bogotá será sede del evento tech más grande de Latinoamérica con 50 mil asistentes",
        "summary": "La capital colombiana albergará TechSummit LATAM 2025, el congreso de tecnología más importante de la región. Se esperan más de 50 mil participantes, 500 empresas expositoras y ponentes de Google, Meta, Microsoft y Amazon. El evento incluirá hackathons, competencias de IA y ruedas de inversión por US$200 millones. Organizadores destacan a Colombia como hub tecnológico emergente en América Latina.",
        "trending_score": 0.78,
    },
    {
        "title_id": "@PetróleoCrudoBrent",
        "display_title": "Precio del petróleo sube 15% y beneficia las finanzas públicas colombianas",
        "summary": "El barril de petróleo tipo Brent alcanzó los US$92, su nivel más alto en 8 meses, impulsado por recortes de producción de la OPEP+ y tensiones geopolíticas. Colombia, como exportador neto, verá incrementos significativos en regalías y ganancias de Ecopetrol. El Ministerio de Hacienda estima ingresos adicionales por $8 billones que podrían destinarse a inversión social. Expertos advierten sobre la volatilidad del mercado energético.",
        "trending_score": 0.89,
    },
    {
        "title_id": "@MinasIlegalesAntioquia",
        "display_title": "Autoridades desmantelan red de minería ilegal que operaba en 12 municipios",
        "summary": "La Fiscalía y el Ejército desarticularon una organización criminal dedicada a la minería ilegal de oro en Antioquia y Chocó. La operación incautó maquinaria pesada valorada en $25 mil millones y capturó a 34 personas. La red extraía mensualmente 200 kilos de oro sin controles ambientales, causando deforestación masiva y contaminación con mercurio. Comunidades indígenas celebraron la intervención tras años de denuncias.",
        "trending_score": 0.76,
    },
    {
        "title_id": "@UniversidadesPúblicas",
        "display_title": "Presupuesto para universidades públicas aumenta $1.2 billones en 2025",
        "summary": "El Gobierno Nacional anunció un incremento histórico de $1.2 billones en el presupuesto para las 32 universidades públicas del país. Los recursos permitirán contratar 2.500 nuevos docentes, modernizar laboratorios e infraestructura, y ampliar programas de bienestar estudiantil. Rectores destacaron el compromiso con la educación superior pública tras años de déficit presupuestal. Se espera aumentar la cobertura en 50 mil cupos adicionales.",
        "trending_score": 0.74,
    },
    {
        "title_id": "@EnergíasRenovablesCesar",
        "display_title": "Cesar inaugura el parque solar más grande de Suramérica con 500 MW",
        "summary": "El departamento del Cesar puso en marcha el complejo de energía solar más extenso del continente, capaz de generar 500 megavatios y abastecer 800 mil hogares. La inversión de US$420 millones generó 2.000 empleos durante la construcción. El proyecto reducirá emisiones de CO2 en 300 mil toneladas anuales y diversificará la matriz energética nacional. Colombia avanza hacia su meta de 30% de energías renovables para 2030.",
        "trending_score": 0.80,
    },
    {
        "title_id": "@ArrozColombiano",
        "display_title": "Producción de arroz rompe récord con 3.2 millones de toneladas",
        "summary": "Fedearroz anunció la cosecha más grande de arroz en la historia del país, superando las 3.2 millones de toneladas. Mejores técnicas de cultivo, semillas certificadas y clima favorable impulsaron los rendimientos. El sector prevé autoabastecimiento nacional y posibles exportaciones a Venezuela y Ecuador. Agricultores del Tolima, Meta y Casanare lideran la producción. Los precios al consumidor se mantendrán estables.",
        "trending_score": 0.72,
    },
    {
        "title_id": "@TransMilenioBRT",
        "display_title": "TransMilenio anuncia renovación total de su flota con buses eléctricos",
        "summary": "Bogotá modernizará el sistema TransMilenio con la compra de 1.485 buses eléctricos que reemplazarán completamente la flota diésel para 2027. La inversión de $4.8 billones reducirá emisiones contaminantes en 40% y mejorará la calidad del aire capitalino. Los nuevos vehículos incluyen aire acondicionado, WiFi gratuito y sistema de pago contactless. Es el proyecto de electromovilidad masiva más ambicioso de Latinoamérica.",
        "trending_score": 0.86,
    },
    {
        "title_id": "@CienciaVacunaDengue",
        "display_title": "Científicos colombianos desarrollan vacuna contra el dengue con 85% de eficacia",
        "summary": "Un equipo del Instituto Nacional de Salud logró crear una vacuna experimental contra el dengue que mostró 85% de efectividad en ensayos clínicos fase III. El desarrollo 100% colombiano podría revolucionar la salud pública en zonas tropicales. La vacuna protege contra los cuatro serotipos del virus y requiere solo dos dosis. Se esperan aprobaciones regulatorias para iniciar producción masiva a mediados de 2026.",
        "trending_score": 0.93,
    },
    {
        "title_id": "@AguacateExportación",
        "display_title": "Colombia se convierte en el tercer exportador mundial de aguacate Hass",
        "summary": "Las exportaciones de aguacate Hass alcanzaron 120 mil toneladas, posicionando a Colombia como tercer proveedor global después de México y Perú. Estados Unidos, Europa y Asia aumentaron sus importaciones debido a la calidad y precios competitivos. Antioquia, Caldas y Tolima concentran el 70% de la producción. El sector genera 45 mil empleos directos y proyecta duplicar ventas internacionales en tres años.",
        "trending_score": 0.77,
    },
    {
        "title_id": "@CiberataqueBancario",
        "display_title": "Frustran ciberataque masivo contra sistema financiero colombiano",
        "summary": "La Superintendencia Financiera y el CSIRT Nacional detectaron y neutralizaron un ataque informático coordinado contra 15 entidades bancarias. Los hackers intentaron robar datos de 2 millones de clientes usando técnicas de ransomware y phishing sofisticado. Las medidas de ciberseguridad evitaron pérdidas millonarias. Autoridades rastrean al grupo criminal con presencia internacional. Expertos recomiendan fortalecer protocolos de seguridad digital.",
        "trending_score": 0.91,
    },
    {
        "title_id": "@FeriadoLaboral",
        "display_title": "Congreso aprueba puente festivo obligatorio para impulsar turismo interno",
        "summary": "El Senado aprobó en cuarto debate la ley que establece 6 puentes festivos obligatorios al año para reactivar el sector turístico. La medida beneficiará a hoteles, restaurantes y operadores en destinos nacionales, generando ingresos estimados en $3 billones anuales. Sindicatos apoyan la iniciativa que garantiza descanso remunerado. Empresarios piden flexibilidad en sectores productivos que no pueden parar operaciones.",
        "trending_score": 0.68,
    },
    {
        "title_id": "@PastaBasaCocaína",
        "display_title": "Incautan 18 toneladas de cocaína en mayor operativo antidrogas del año",
        "summary": "En un golpe histórico al narcotráfico, la Armada y la DEA interceptaron un buque con 18 toneladas de clorhidrato de cocaína en el Pacífico. El cargamento, valuado en US$500 millones, estaba destinado a México y Estados Unidos. Se capturaron 12 tripulantes de nacionalidades mixtas. La operación internacional desarticuló una ruta clave del Clan del Golfo. Es la mayor incautación marítima en la historia de Colombia.",
        "trending_score": 0.94,
    },
    {
        "title_id": "@StartupUnicornio",
        "display_title": "Startup colombiana Habi alcanza valuación de US$1.300 millones",
        "summary": "La proptech Habi se convirtió en el nuevo unicornio tecnológico colombiano tras cerrar ronda de inversión serie C por US$200 millones. La plataforma que digitaliza compra-venta de viviendas opera en 5 países y ha transado 15 mil propiedades. Inversionistas destacan su modelo disruptivo que reduce tiempos de negociación de 6 meses a 7 días. Colombia suma 4 unicornios en el ecosistema tech latinoamericano.",
        "trending_score": 0.83,
    },
    {
        "title_id": "@SalarioMínimo2026",
        "display_title": "Proponen salario mínimo de $1.520.000 para 2026 con aumento del 12%",
        "summary": "Las centrales obreras y gremios empresariales iniciaron negociaciones para definir el salario mínimo de 2026. Los trabajadores solicitan incremento del 12% que lo llevaría a $1.520.000, argumentando recuperación del poder adquisitivo. Empresarios proponen 7% atado a productividad e inflación. El Gobierno actuará como mediador si no hay acuerdo en diciembre. Más de 3 millones de colombianos dependen del mínimo.",
        "trending_score": 0.79,
    },
    {
        "title_id": "@AeropuertoBogotá",
        "display_title": "El Dorado amplía segunda pista y aumentará capacidad en 40%",
        "summary": "Opain invierte US$800 millones en la ampliación y modernización de la pista sur del aeropuerto El Dorado. Las obras permitirán 50 operaciones por hora, aumentando capacidad anual a 45 millones de pasajeros. Se construirán 12 posiciones de contacto adicionales y se modernizará la torre de control con tecnología satelital. Bogotá consolida su posición como hub aéreo de Suramérica. Finalización prevista para 2027.",
        "trending_score": 0.75,
    },
    {
        "title_id": "@DesempleoReducción",
        "display_title": "Desempleo cae a 9.2%, el nivel más bajo desde 2019",
        "summary": "El DANE reportó que la tasa de desempleo nacional se ubicó en 9.2% en enero, representando una reducción de 2.1 puntos frente al año anterior. Se crearon 620 mil nuevos empleos formales, principalmente en comercio, construcción y servicios. Las ciudades con mayor recuperación fueron Medellín, Cali y Barranquilla. Analistas atribuyen la mejora a reactivación económica y programas de formalización laboral.",
        "trending_score": 0.81,
    },
    {
        "title_id": "@TrenRegionalPacífico",
        "display_title": "Gobierno anuncia tren de pasajeros que conectará Cali con Buenaventura",
        "summary": "El presidente firmó el decreto que da vía libre al proyecto ferroviario Valle-Pacífico, un tren de pasajeros que recorrerá 120 kilómetros entre Cali y Buenaventura en 90 minutos. La inversión de US$1.200 millones contempla 8 estaciones intermedias y tecnología de última generación. El sistema transportará 15 mil pasajeros diarios y dinamizará el corredor logístico más importante del país. Inicio de obras en 2026.",
        "trending_score": 0.73,
    },
    {
        "title_id": "@FloresValentín",
        "display_title": "Exportaciones de flores baten récord por San Valentín con 800 millones de tallos",
        "summary": "Asocolflores reportó que Colombia exportó 800 millones de tallos para San Valentín, consolidándose como segundo proveedor mundial después de Holanda. Estados Unidos importó el 78% de las flores colombianas, valoradas en US$320 millones. Rosas, claveles y crisantemos lideraron las ventas. El sector genera 200 mil empleos, especialmente en Cundinamarca y Antioquia. La logística aérea movilizó 100 mil toneladas en 15 días.",
        "trending_score": 0.70,
    },
    {
        "title_id": "@CascosAzulesONU",
        "display_title": "Colombia enviará 450 cascos azules a misión de paz en África",
        "summary": "Las Fuerzas Militares desplegarán un batallón de 450 efectivos a la misión MINUSCA en República Centroafricana. Es el contingente colombiano más grande en operaciones de paz de la ONU. Los soldados entrenarán fuerzas locales, protegerán civiles y apoyarán procesos de desarme. El país fortalece su perfil internacional en construcción de paz tras la experiencia doméstica. La misión durará 12 meses con posible extensión.",
        "trending_score": 0.67,
    },
    {
        "title_id": "@InfluencerEscándalo",
        "display_title": "Influencer colombiana con 8 millones de seguidores acusada de estafa piramidal",
        "summary": "La Fiscalía imputó cargos por captación ilegal de dinero a reconocida influencer que promocionó plataforma de inversiones. Más de 15 mil colombianos perdieron $45 mil millones en el esquema tipo Ponzi que prometía rendimientos del 30% mensual. Las autoridades congelaron cuentas bancarias y propiedades de lujo. El caso reabre debate sobre regulación de publicidad en redes sociales y responsabilidad de creadores de contenido.",
        "trending_score": 0.88,
    },
    {
        "title_id": "@BicicletasMontaña",
        "display_title": "Ciclista colombiano gana etapa reina del Tour de Francia",
        "summary": "Egan Bernal conquistó la etapa 17 del Tour de Francia con llegada en Alpe d'Huez, consolidando su regreso al máximo nivel tras grave accidente. El colombiano atacó a 5 kilómetros de meta y llegó en solitario con 42 segundos de ventaja. Trepa al tercer lugar de la general a dos días del final. Los aficionados celebran el regreso del campeón de 2019. Nairo Quintana y Sergio Higuita también brillaron.",
        "trending_score": 0.96,
    },
    {
        "title_id": "@PuertoAguas",
        "display_title": "Puerto de aguas profundas en Urabá recibe primera inversión por US$600 millones",
        "summary": "El puerto de Urabá, proyecto estratégico para conectar el Pacífico y el Atlántico, inició su fase de construcción con inversión inicial de US$600 millones. La infraestructura manejará 2 millones de contenedores anuales y creará 8 mil empleos permanentes. Empresarios ven oportunidad para reducir costos logísticos en 30%. Las comunidades de Turbo y Necoclí recibirán programas de desarrollo social. Operación prevista para 2029.",
        "trending_score": 0.71,
    },
]

MOCK_SOURCES = [
    "El Tiempo",
    "El Espectador",
    "Semana",
    "Portafolio",
    "La República",
    "RCN Radio",
    "Caracol Radio",
]

SUGGESTED_QUESTIONS_TEMPLATES = [
    "¿Cuál es el impacto económico de {topic}?",
    "¿Qué opinan los expertos sobre {topic}?",
    "¿Cómo afecta esto a la ciudadanía?",
    "¿Cuáles son las principales críticas a {topic}?",
    "¿Qué medidas se están tomando?",
    "¿Cuál es el contexto histórico de {topic}?",
]

# Mapeo de topics a keywords de búsqueda en Unsplash
# Keywords más específicos y variados para evitar fotos genéricas
UNSPLASH_KEYWORDS = {
    "@ReformaTributaria2026": "congress government meeting debate politics",
    "@DólarDispara": "currency exchange dollar bills money crisis",
    "@TransMetroMedellín": "modern metro train station urban transport",
    "@ParoCampesino": "protest road block farmers demonstration",
    "@LuisDíazGol": "soccer player celebration goal scoring stadium",
    "@CaféColombianoExportaciones": "coffee beans plantation harvest sack",
    "@ViviendaNueva": "new apartment building construction housing development",
    "@InflaciónEnero": "grocery shopping basket prices supermarket",
    "@TurismoCartagena": "cartagena colonial architecture colorful buildings caribbean",
    "@TecnologíaBogotá": "technology conference startup innovation laptop",
    "@PetróleoCrudoBrent": "oil rig petroleum industry offshore drilling",
    "@MinasIlegalesAntioquia": "illegal mining gold heavy machinery excavator",
    "@UniversidadesPúblicas": "university campus students library education",
    "@EnergíasRenovablesCesar": "solar panels renewable energy farm sustainable",
    "@ArrozColombiano": "rice field paddy harvest agriculture grain",
    "@TransMilenioBRT": "electric bus public transport charging station",
    "@CienciaVacunaDengue": "scientist laboratory research vaccine microscope",
    "@AguacateExportación": "avocado fruit plantation export agriculture",
    "@CiberataqueBancario": "cyber security hacker computer code screen",
    "@FeriadoLaboral": "beach vacation holiday relaxation tourism",
    "@PastaBasaCocaína": "coast guard navy ship ocean patrol",
    "@StartupUnicornio": "startup office workspace team innovation tech",
    "@SalarioMínimo2026": "workers meeting negotiation union labor",
    "@AeropuertoBogotá": "airport runway airplane departure terminal",
    "@DesempleoReducción": "employment job interview hiring office work",
    "@TrenRegionalPacífico": "train railway tracks modern locomotive passenger",
    "@FloresValentín": "roses flowers bouquet valentine colorful petals",
    "@CascosAzulesONU": "peacekeepers united nations military uniform helmet",
    "@InfluencerEscándalo": "social media influencer smartphone followers",
    "@BicicletasMontaña": "cycling road bike mountain race professional",
    "@PuertoAguas": "port containers cargo ship logistics maritime",
}


def fetch_unsplash_image(query: str) -> str:
    """
    Busca una imagen en Unsplash basada en el query
    Retorna la URL de la imagen en alta calidad
    """
    access_key = os.getenv("UNSPLASH_ACCESS_KEY")
    if not access_key:
        print("⚠️  UNSPLASH_ACCESS_KEY no encontrado, usando gradient por defecto")
        return ""

    try:
        url = "https://api.unsplash.com/search/photos"
        headers = {"Authorization": f"Client-ID {access_key}"}
        params = {
            "query": query,
            "per_page": 1,
            "orientation": "landscape",
        }

        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        if data["results"] and len(data["results"]) > 0:
            # Usar URL regular (1080px width) para mejor calidad
            image_url = data["results"][0]["urls"]["regular"]
            photographer = data["results"][0]["user"]["name"]
            print(f"    📷 Imagen obtenida: {photographer}")
            return image_url
        else:
            print(f"    ⚠️  No se encontraron imágenes para: {query}")
            return ""

    except Exception as e:
        print(f"    ⚠️  Error obteniendo imagen de Unsplash: {e}")
        return ""


def seed_mock_data():
    """Inserta datos de ejemplo en Supabase"""

    print("🌱 Iniciando seed de datos mock...")

    # Conectar a Supabase
    supabase = create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_KEY")
    )

    print("✅ Conectado a Supabase")

    # Ejecutar migración para añadir image_url si no existe
    print("\n🔧 Verificando schema de base de datos...")
    try:
        # Intentar hacer un query que incluya image_url
        # Si falla, es que la columna no existe
        test_query = supabase.table("threads").select("image_url").limit(1).execute()
        print("✅ Columna image_url ya existe")
    except Exception:
        print("⚠️  La columna image_url no existe en la tabla threads")
        print("💡 Por favor ejecuta manualmente en Supabase Dashboard SQL Editor:")
        print("   ALTER TABLE threads ADD COLUMN IF NOT EXISTS image_url TEXT;")
        print("")

    # Limpiar datos existentes (opcional)
    print("\n🗑️  Limpiando datos existentes...")
    try:
        supabase.table("thread_questions").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        supabase.table("thread_articles").delete().neq("thread_id", "00000000-0000-0000-0000-000000000000").execute()
        supabase.table("threads").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        supabase.table("articles").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        print("✅ Datos limpiados")
    except Exception as e:
        print(f"⚠️  Error limpiando datos: {e}")

    # Insertar threads con artículos
    print("\n📰 Insertando threads y artículos...")

    for idx, thread_data in enumerate(MOCK_THREADS):
        print(f"\n  {idx + 1}/{len(MOCK_THREADS)} - {thread_data['title_id']}")

        # Obtener imagen de Unsplash
        keywords = UNSPLASH_KEYWORDS.get(thread_data["title_id"], "colombia news")
        image_url = fetch_unsplash_image(keywords)

        # Crear thread
        thread_id = str(uuid4())
        num_articles = random.randint(5, 12)
        # Noticias de las últimas 12 horas para que se vean frescas
        created_at = datetime.utcnow() - timedelta(hours=random.randint(1, 12))

        thread = {
            "id": thread_id,
            "title_id": thread_data["title_id"],
            "display_title": thread_data["display_title"],
            "summary": thread_data["summary"],
            "trending_score": thread_data["trending_score"],
            "article_count": num_articles,
            "image_url": image_url,
            "created_at": created_at.isoformat(),
            "updated_at": created_at.isoformat(),
        }

        supabase.table("threads").insert(thread).execute()
        print(f"    ✅ Thread creado")

        # Crear artículos para este thread
        article_ids = []
        for i in range(num_articles):
            article_id = str(uuid4())
            source = random.choice(MOCK_SOURCES)
            # Artículos publicados en las últimas 6 horas
            published_at = created_at - timedelta(hours=random.randint(0, 6))

            article = {
                "id": article_id,
                "url": f"https://www.{source.lower().replace(' ', '')}.com/noticia-{article_id[:8]}",
                "title": f"{thread_data['display_title']} - Análisis de {source}",
                "content": f"Contenido completo del artículo sobre {thread_data['display_title']}. " * 20,
                "source": source,
                "author": f"Redacción {source}",
                "published_at": published_at.isoformat(),
                "scraped_at": created_at.isoformat(),
                "created_at": created_at.isoformat(),
            }

            supabase.table("articles").insert(article).execute()
            article_ids.append(article_id)

        print(f"    ✅ {num_articles} artículos creados")

        # Asociar artículos con thread
        for position, article_id in enumerate(article_ids):
            thread_article = {
                "thread_id": thread_id,
                "article_id": article_id,
                "position": position,
            }
            supabase.table("thread_articles").insert(thread_article).execute()

        print(f"    ✅ Artículos asociados al thread")

        # Crear preguntas sugeridas
        topic_short = thread_data["title_id"].replace("@", "").replace("_", " ")
        questions = random.sample(SUGGESTED_QUESTIONS_TEMPLATES, 3)

        for position, q_template in enumerate(questions):
            question = {
                "id": str(uuid4()),
                "thread_id": thread_id,
                "question": q_template.format(topic=topic_short),
                "position": position,
                "created_at": created_at.isoformat(),
            }
            supabase.table("thread_questions").insert(question).execute()

        print(f"    ✅ Preguntas sugeridas creadas")

    print("\n\n🎉 ¡Seed completado exitosamente!")
    print(f"📊 Total insertado:")
    print(f"   - {len(MOCK_THREADS)} threads")
    print(f"   - ~{sum(random.randint(5, 12) for _ in MOCK_THREADS)} artículos")
    print(f"   - {len(MOCK_THREADS) * 3} preguntas sugeridas")
    print(f"\n🚀 Visita http://localhost:3000 para ver el resultado")


if __name__ == "__main__":
    seed_mock_data()
