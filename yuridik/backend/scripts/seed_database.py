"""
Database Seeding Script
Pre-populates the ChromaDB with sample legal documents for demo.
Run with: python -m scripts.seed_database
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import get_settings
from app.rag_engine.chunker import chunk_legal_document


# Sample legal documents for demo (excerpts from real decrees)
SAMPLE_DOCUMENTS = [
    {
        "id": "PQ-60",
        "title": "Yoshlar tadbirkorligini qo'llab-quvvatlash to'g'risida",
        "url": "https://lex.uz/docs/7084623",
        "content": """
O'ZBEKISTON RESPUBLIKASI PREZIDENTINING QARORI

Yoshlar tadbirkorligini yanada rivojlantirish va ularni qo'llab-quvvatlash chora-tadbirlari to'g'risida

1-modda. Yoshlar tadbirkorligini rivojlantirish davlat maqsadli jamg'armasi tashkil etilsin.

Jamg'arma mablag'lari:
- 100 million AQSh dollari miqdorida ajratiladi
- Kamida 50 000 nafar yoshni tadbirkorlikka jalb qilish maqsadida ishlatiladi

2-modda. Yoshlar uchun quyidagi imtiyozlar belgilansin:
- 30 yoshgacha bo'lgan yoshlar tomonidan tashkil etiladigan mikrofirma va kichik korxonalar uchun mulk solig'idan 3 yil muddatga ozod qilish
- Yoshlar loyihalariga 10 million AQSh dollari hajmida venchur jamg'armasi tashkil etish
- Yoshlar biznes-loyihalariga imtiyozli kreditlar

3-modda. Yoshlar tadbirkorligi agentligi zimmasiga:
- Yoshlarni tadbirkorlikka tayyorlash
- Mentorlik dasturlarini tashkil etish
- Grant tanlovlarini o'tkazish vazifalari yuklanadi

4-modda. Daryolar, kanallar va qirg'oqlar bo'ylab joylashgan yer uchastkalarini xizmat ko'rsatish, ko'ngilochar va dam olish zonalari uchun elektron onlayn auktsion orqali ajratish belgilandi.
        """,
    },
    {
        "id": "PD-50",
        "title": "Kichik va o'rta biznes ulushini oshirish chora-tadbirlari to'g'risida",
        "url": "https://lex.uz/docs/7129456",
        "content": """
O'ZBEKISTON RESPUBLIKASI PREZIDENTINING FARMONI

Kichik va o'rta biznes (KO'B) subʼyektlarining iqtisodiyotdagi rolini oshirish chora-tadbirlari to'g'risida

1-modda. Quyidagi maqsadlar belgilansin:
- KO'B ulushini YaIMda 55 foizga yetkazish
- 1,5 million doimiy ish o'rni yaratish

2-modda. 2025-yil 1-maydan boshlab:
- 20 ta tumanda sanoatni jadal rivojlantirish bo'yicha loyiha ofislari ishga tushiriladi
- Tadbirkorlarga maslahat xizmatlari ko'rsatiladi
- Mutaxassislarni jalb qilishga yordam beriladi

3-modda. 2025-yil 1-iyuldan boshlab:
- Yuqori texnologiyali ishlab chiqarish sohasidagi tadbirkorlar 5 yil muddatga 10 000 kvadrat metrgacha davlat ko'chmas mulkini BEPUL foydalanishga olishi mumkin

4-modda. 15 ta shahar va tumanda:
- Davlat muassasalari avval foydalangan binolarning birinchi qavatlari tadbirkorlarga mulk sifatida beriladi
- KO'B subʼyektlarini joylashtirish dasturi ishga tushiriladi

5-modda. Soliq imtiyozlari:
- Yangi tashkil etilgan KO'B subʼyektlari uchun dastlabki 2 yil daromad solig'idan ozod qilish
        """,
    },
    {
        "id": "PQ-306",
        "title": "Kichik biznesni uzluksiz qo'llab-quvvatlash kompleks dasturi",
        "url": "https://lex.uz/docs/6577289",
        "content": """
O'ZBEKISTON RESPUBLIKASI PREZIDENTINING QARORI

2023-2026 yillar uchun kichik biznesni uzluksiz qo'llab-quvvatlash kompleks dasturi to'g'risida

1-modda. Dastur moliyalashtirish manbalari:
- Davlat fondlaridan 6 trillion so'm
- Xalqaro moliya institutlaridan 1,2 milliard AQSh dollari

2-modda. Biznesni rivojlantirish banki (sobiq Qishloq qurilish banki) dasturni amalga oshiruvchi asosiy bank etib belgilandi.

3-modda. Kredit imtiyozlari:
- Biznes tashkil etish yoki kengaytirish uchun 1,5 milliard so'mgacha kredit
- Qaytarish muddati 7 yilgacha
- Imtiyozli davr 2 yilgacha

4-modda. Aylanma mablag'lar uchun:
- 3 yilgacha muddatli kreditlar
- Yillik stavka Markaziy bank stavkasidan 4 foiz band yuqori

5-modda. Garovsiz kreditlar:
- 100 million so'mgacha garovsiz
- 150 million so'mgacha kamaytiriladigan garov talablari bilan

6-modda. Maslahat xizmatlari:
- Biznes-rejalar tuzish bo'yicha yordam
- Buxgalteriya va soliq maslahatlari
- Eksportga chiqish bo'yicha ko'mak
        """,
    },
    {
        "id": "IT-PARK",
        "title": "IT Park rezidentlari uchun soliq imtiyozlari",
        "url": "https://lex.uz/docs/-4548291",
        "content": """
IT PARK REZIDENTLARI UCHUN SOLIQ IMTIYOZLARI

1-modda. IT Park rezidentlari quyidagi soliqlardan ozod:
- Foyda solig'i
- Mol-mulk solig'i
- Ijtimoiy soliq (kamaytirilgan stavkada)
- Dividend solig'i

2-modda. Xodimlar uchun imtiyozlar:
- Jismoniy shaxslardan olinadigan daromad solig'i 7,5% stavkada (odatda 12%)
- Ijtimoiy soliq 1% stavkada

3-modda. Eksport imtiyozlari:
- Eksport xizmatlari QQS dan ozod
- Chet el valyutasini erkin olish-sotish

4-modda. Ro'yxatdan o'tish:
- Onlayn ariza orqali ro'yxatdan o'tish mumkin
- Minimal hujjatlar talab qilinadi
- 5 ish kuni ichida qaror qabul qilinadi

5-modda. 2028-yil 1-yanvardan 2040-yil 1-yanvargacha:
- Eksport hajmi 50% dan oshsa, barcha soliqlardan (QQS dan tashqari) ozod
        """,
    },
    {
        "id": "FERMER",
        "title": "Fermer xo'jaliklarini qo'llab-quvvatlash",
        "url": "https://lex.uz/docs/6541282",
        "content": """
FERMER XO'JALIKLARINI QO'LLAB-QUVVATLASH CHORA-TADBIRLARI

1-modda. Fermerlar uchun yer solig'i imtiyozlari:
- Yangi tashkil etilgan fermer xo'jaliklari 3 yil yer solig'idan ozod
- Tog'li hududlarda 5 yil muddatga ozod qilish

2-modda. Kredit imtiyozlari:
- Qishloq xo'jaligi texnikasi sotib olish uchun 5 yillik imtiyozli kredit
- Dastlabki to'lov 10% dan boshlanadi
- Yillik stavka 7-10%

3-modda. Subsidiyalar:
- Mineral o'g'itlar sotib olishga 30% subsidiya
- Sug'orish tizimlarini o'rnatishga 50% subsidiya
- Issiqxonalar qurishga 40% subsidiya

4-modda. Grant dasturlari:
- Yosh fermerlar uchun 50 million so'mgacha startap grantlar
- Innovatsion loyihalar uchun 200 million so'mgacha grantlar

5-modda. Ta'minot imtiyozlari:
- Urug'lik sotib olishda 20% chegirma
- Qishloq xo'jaligi dorialariga imtiyozli narx
        """,
    },
]


def seed_database():
    """Seed the ChromaDB with sample documents."""
    settings = get_settings()
    
    print("🌱 Starting database seeding...")
    print(f"   ChromaDB path: {settings.chroma_persist_directory}")
    
    # Initialize ChromaDB
    client = chromadb.PersistentClient(
        path=settings.chroma_persist_directory,
        settings=ChromaSettings(anonymized_telemetry=False)
    )
    
    # Get or create collection
    collection = client.get_or_create_collection(
        name=settings.chroma_collection_name,
        metadata={"description": "Uzbek legal documents for entrepreneur privileges"}
    )
    
    existing_count = collection.count()
    print(f"   Existing documents: {existing_count}")
    
    # Process and add each document
    total_chunks = 0
    
    for doc in SAMPLE_DOCUMENTS:
        print(f"\n📄 Processing: {doc['id']} - {doc['title'][:40]}...")
        
        # Chunk the document
        chunks = chunk_legal_document(
            text=doc["content"],
            document_id=doc["id"],
            title=doc["title"],
            metadata={
                "source_url": doc["url"],
                "document_type": "sample"
            }
        )
        
        if not chunks:
            print(f"   ⚠️ No chunks generated for {doc['id']}")
            continue
        
        # Prepare data for ChromaDB
        documents = [c.text for c in chunks]
        metadatas = [c.metadata for c in chunks]
        ids = [f"{doc['id']}_{c.index}" for c in chunks]
        
        # Check for existing IDs and remove them
        existing_ids = collection.get(ids=ids)["ids"]
        if existing_ids:
            print(f"   Updating {len(existing_ids)} existing chunks...")
            collection.delete(ids=existing_ids)
        
        # Add to collection
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        total_chunks += len(chunks)
        print(f"   ✅ Added {len(chunks)} chunks")
    
    # Final count
    final_count = collection.count()
    print(f"\n🎉 Seeding complete!")
    print(f"   Total documents: {len(SAMPLE_DOCUMENTS)}")
    print(f"   Total chunks: {total_chunks}")
    print(f"   Collection size: {final_count}")


if __name__ == "__main__":
    seed_database()
