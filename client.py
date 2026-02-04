import requests

BASE_URL = "http://127.0.0.1:8000"

# Вставь сюда requestid, который у тебя уже работает (из твоего ответа)
REQUEST_ID = 11705369183

def main():
    print("Запрашиваю туры у локального MCP-сервера...")
    payload = {"requestid": REQUEST_ID, "lastblock": 3}

    r = requests.post(f"{BASE_URL}/mcp/get_results", json=payload, timeout=30)
    r.raise_for_status()
    data = r.json()

    print("\nRAW RESPONSE FROM SERVER:\n", data)

    results = data.get("results", [])
    print(f"\nНайдено результатов: {len(results)}")

    print("\nТОП туров:")
    for i, item in enumerate(results, 1):
        hotel = item.get("hotel", {})
        print(f"{i}. {hotel.get('name')} ({hotel.get('stars')}*) — {item.get('price_rub')} ₽")
        print(f"   Дата: {item.get('date_from')}, Ночей: {item.get('nights')}, Питание: {item.get('meal')}")
        print(f"   Город: {item.get('city')}")
        print(f"   Фото: {hotel.get('image')}")
        print()

if __name__ == "__main__":
    main()

