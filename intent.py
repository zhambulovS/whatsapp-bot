# intent.py

def detect_intent(message):
    message = message.lower().strip()
    
    # Улучшенные ключевые слова для бронирования
    booking_keywords = [
        "бронь", "брондау", "жазылу", "жазылу", "записаться", "запись", 
        "брон", "резерв", "резервация", "регистрация", "жаздыру",
        "күн", "сағат", "уақыт", "дата", "кезек", "слот", "мезгіл",
        "таңдау", "босату", "бос", "жай", "қол", "қой", "қойыңыз", "қабылдау",
        "келу", "бару", "қатысу", "қатынасу", "бар", "келе", "қалай"
    ]
    
    # Конкретные фразы для бронирования
    booking_phrases = [
        "жазып қой", "бронь жасау", "уақыт таңдау", "кезекке жазу", 
        "брондауға келеді", "дата босатасыз ба", "күн таңдасам бола ма",
        "қандай уақыт бос", "мезгіл бар ма", "слот босатыңыз"
    ]

    # Проверка по ключевым словам
    if any(keyword in message for keyword in booking_keywords):
        return "booking"
    
    # Проверка по конкретным фразам
    if any(phrase in message for phrase in booking_phrases):
        return "booking"
    
    # Остальные интенты
    if any(word in message for word in ["баға", "қанша", "ақша", "тұрады", "тұр"]):
        return "price"
    elif any(word in message for word in ["қайда", "мекенжай", "локация", "адрес", "орналасқан"]):
        return "location"
    elif any(word in message for word in ["қызмет", "не істейсіз", "қандай қызмет", "ұсынасыз", "фотосессия"]):
        return "services"
    
    return "general"