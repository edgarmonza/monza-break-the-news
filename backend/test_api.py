"""
Script de prueba para API REST
"""
import requests
import json
from typing import Dict, Any

API_BASE_URL = "http://localhost:8000"


def print_response(response: requests.Response, title: str):
    """Pretty print de respuesta"""
    print("\n" + "="*70)
    print(f"{title}")
    print("="*70)
    print(f"Status: {response.status_code}")

    try:
        data = response.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except:
        print(response.text)

    print()


def test_health():
    """Test health check"""
    response = requests.get(f"{API_BASE_URL}/health")
    print_response(response, "1. HEALTH CHECK")
    return response.status_code == 200


def test_feed():
    """Test feed endpoint"""
    response = requests.get(
        f"{API_BASE_URL}/api/feed",
        params={"limit": 5, "offset": 0}
    )
    print_response(response, "2. FEED (primeros 5 threads)")

    if response.status_code == 200:
        data = response.json()
        threads = data.get('threads', [])
        print(f"✅ {len(threads)} threads encontrados")
        return threads
    return []


def test_thread_detail(thread_id: str):
    """Test thread detail endpoint"""
    response = requests.get(f"{API_BASE_URL}/api/thread/{thread_id}")
    print_response(response, "3. THREAD DETAIL")

    if response.status_code == 200:
        print("✅ Thread encontrado con artículos")
        return True
    return False


def test_chat(question: str, thread_id: str = None):
    """Test chat endpoint"""
    payload = {"question": question}
    if thread_id:
        payload["thread_id"] = thread_id

    response = requests.post(
        f"{API_BASE_URL}/api/chat",
        json=payload
    )
    print_response(response, f"4. CHAT: '{question}'")

    if response.status_code == 200:
        print("✅ Respuesta generada")
        return True
    return False


def test_search(query: str):
    """Test search endpoint"""
    response = requests.get(
        f"{API_BASE_URL}/api/search",
        params={"query": query, "limit": 5}
    )
    print_response(response, f"5. SEARCH: '{query}'")

    if response.status_code == 200:
        data = response.json()
        results = data.get('results', [])
        print(f"✅ {len(results)} resultados encontrados")
        return True
    return False


def main():
    """Ejecuta todas las pruebas"""
    print("\n" + "="*70)
    print("PRUEBAS DE API - Colombia News")
    print("="*70)
    print()
    print("⚠️  NOTA: Asegúrate de que:")
    print("   1. La API está corriendo: python backend/api/main.py")
    print("   2. Hay datos en la BD: python backend/run_pipeline_to_db.py")
    print()

    input("Presiona Enter para continuar...")

    # Test 1: Health
    print("\n🏥 Probando health check...")
    if not test_health():
        print("\n❌ API no está disponible")
        print("   Ejecuta: cd backend && python api/main.py")
        return

    # Test 2: Feed
    print("\n📰 Probando feed...")
    threads = test_feed()

    if not threads:
        print("\n⚠️  No hay threads en la base de datos")
        print("   Ejecuta: python backend/run_pipeline_to_db.py")
        return

    # Test 3: Thread Detail
    if threads:
        first_thread = threads[0]
        thread_id = first_thread['id']
        thread_title_id = first_thread['title_id']

        print(f"\n🔍 Probando detalle de thread: {thread_title_id}")
        test_thread_detail(thread_id)

        # Test 4: Chat sobre thread específico
        print(f"\n💬 Probando chat sobre thread: {thread_title_id}")
        test_chat(
            question="¿Por qué es importante esto?",
            thread_id=thread_id
        )

    # Test 5: Chat global
    print("\n💬 Probando chat global...")
    test_chat(
        question="¿Qué está pasando en Colombia hoy?",
        thread_id=None
    )

    # Test 6: Search
    print("\n🔎 Probando búsqueda semántica...")
    test_search(query="economía")

    print("\n" + "="*70)
    print("PRUEBAS COMPLETADAS")
    print("="*70)
    print()
    print("📚 Explora la documentación interactiva:")
    print(f"   {API_BASE_URL}/docs")
    print()


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ No se puede conectar a la API")
        print("   Asegúrate de que está corriendo:")
        print("   cd backend && python api/main.py")
    except KeyboardInterrupt:
        print("\n\nPruebas canceladas")
