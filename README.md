# 📄 Telegram RAG Bot для анализа документов

AI-ассистент для анализа документов, реализованный в виде Telegram-бота.  
Система использует Retrieval-Augmented Generation (RAG) для ответа на вопросы по загруженным файлам.

---

## 🚀 Основные возможности

- Загрузка документов (PDF, DOC, DOCX, TXT)
- Извлечение текста (включая OCR для сканов)
- Ответы на вопросы по содержимому документов
- Поддержка нескольких файлов
- Контекстный диалог с пользователем

---

## 🧩 Архитектура системы

### 1. 📂 Работа с файлами (Document Parsing)

Пользователь может загружать документы следующих форматов:
- `pdf`, `doc`, `docx`, `txt`

При обработке файлов:
- выполняется **извлечение текста (text extraction)**
- для PDF:
  - сначала используется **text layer**
  - если текст отсутствует (скан), применяется **OCR (Tesseract)**

---

### 2. 🧠 Краткосрочная память (Short-term Memory)

Для хранения контекста диалога используется **Redis**:
- сохраняются сообщения пользователя и ответы ассистента
- хранится до **10 последних сообщений**
- используется для поддержания диалога

---

### 3. 🗄️ Долгосрочная память (Knowledge Base)

После загрузки документа:

1. Документ разбивается на **чанки**
2. Далее выполняется параллельная обработка:

#### 📌 Ветка 1 — Чанки

- chunk → **dense embedding**
- chunk → **sparse embedding**
- запись в коллекцию **`documents_collection`**

#### 📌 Ветка 2 — Суммаризация

- chunk → извлечение **фактов и сущностей**
- агрегация → summary документа
- summary → **dense embedding**
- запись в коллекцию **`document_summaries`**

---

### 📊 Используемые модели

- **Dense embedding:**  
  `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`

- **Sparse embedding:**  
  `Qdrant/bm25`

---

### 4. 🔍 RAG (Retrieval-Augmented Generation)

Используется **гибридный поиск (hybrid search)**:

- Dense поиск (semantic similarity)
- Sparse поиск (BM25)
- Объединение через RRF (Reciprocal Rank Fusion)

В контекст LLM передаётся:
- до **5 чанков документов**
- до **3 summary документов**

---

### 5. 🎯 Reranking

После retrieval применяется **reranking**:

- из расширенного набора кандидатов выбираются наиболее релевантные
- снижает шум и повышает точность ответа

**Используемая модель:**
jinaai/jina-reranker-v2-base-multilingual


---

### 6. 🤖 LLM (Генерация ответов)

LLM используется для:
- ответа на вопросы пользователя
- суммаризации документов

**Провайдер:**
- OpenRouter

**Модель:**
gpt-4o-mini


---

### 7. 🌐 Хостинг

Приложение развернуто на Hugging Face Spaces:

👉 https://huggingface.co/spaces/zaitsev-e-a/test_center_ai/

---

## 🔄 Общий pipeline

```text
Документ
   ↓
Парсинг (text layer / OCR)
   ↓
Chunking
   ↓
Embedding (dense + sparse)
   ↓
Qdrant (documents_collection + document_summaries)
   ↓
Запрос пользователя
   ↓
Hybrid Search
   ↓
Rerank
   ↓
Формирование контекста
   ↓
LLM
   ↓
Ответ пользователю


📌 Особенности реализации
Поддержка мультимодального ingestion (text layer + OCR)
Гибридный поиск (dense + sparse)
Двухуровневая память:
Redis (диалог)
Qdrant (знания)
Reranking для повышения качества retrieval
Summary + chunk-level RAG