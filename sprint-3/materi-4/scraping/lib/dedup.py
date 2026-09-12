"""
lib/dedup.py — Near-duplicate detection menggunakan MinHash LSH
GRAK 2026 · Sprint 3

Cara pakai:
    from lib.dedup import find_near_duplicates
    
    texts = ["paragraf satu...", "paragraf dua...", ...]
    duplicate_indices = find_near_duplicates(texts, threshold=0.85)
    # duplicate_indices = {3, 7, 15, ...}  ← index yang merupakan duplikat
"""

from datasketch import MinHash, MinHashLSH


def _text_to_shingles(text: str, k: int = 3) -> set[str]:
    """
    Pecah text menjadi k-shingles (subsequence k kata berurutan).
    
    Contoh (k=3):
        "saya suka makan nasi goreng" → {"saya suka makan", "suka makan nasi", "makan nasi goreng"}
    
    Kenapa shingles, bukan words?
        - Shingles menangkap urutan kata (konteks)
        - Lebih akurat daripada bag-of-words untuk deteksi duplikat
    """
    words = text.lower().split()
    if len(words) < k:
        return {text.lower()}
    return {" ".join(words[i:i+k]) for i in range(len(words) - k + 1)}


def _create_minhash(shingles: set[str], num_perm: int = 128) -> MinHash:
    """Buat MinHash signature dari set of shingles."""
    m = MinHash(num_perm=num_perm)
    for s in shingles:
        m.update(s.encode("utf-8"))
    return m


def find_near_duplicates(
    texts: list[str],
    threshold: float = 0.85,
    num_perm: int = 128,
) -> set[int]:
    """
    Temukan index-index yang merupakan near-duplicate.
    
    Untuk setiap cluster duplikat, SIMPAN yang pertama (index terkecil),
    dan TANDAI sisanya untuk dihapus.
    
    Args:
        texts: List of text strings
        threshold: Similarity threshold (0.0 - 1.0). Default 0.85 = 85% mirip
        num_perm: Jumlah permutasi MinHash. Lebih tinggi = lebih akurat tapi lambat.
    
    Returns:
        Set of indices yang merupakan duplikat (harus dihapus)
    
    Contoh:
        texts = ["halo dunia", "hello world", "halo dunia ini"]
        duplicates = find_near_duplicates(texts, threshold=0.8)
        # duplicates mungkin = {2} (index 2 mirip dengan index 0)
    """
    if len(texts) < 2:
        return set()
    
    # Step 1: Buat MinHash untuk setiap text
    minhashes = []
    for text in texts:
        shingles = _text_to_shingles(text)
        mh = _create_minhash(shingles, num_perm)
        minhashes.append(mh)
    
    # Step 2: Masukkan ke LSH index
    lsh = MinHashLSH(threshold=threshold, num_perm=num_perm)
    
    for i, mh in enumerate(minhashes):
        try:
            lsh.insert(str(i), mh)
        except ValueError:
            # Duplicate key — text persis sama, tandai untuk hapus
            pass
    
    # Step 3: Query setiap text, cari yang mirip
    to_remove = set()
    
    for i, mh in enumerate(minhashes):
        if i in to_remove:
            continue
        
        # Cari semua text yang mirip dengan text[i]
        candidates = lsh.query(mh)
        
        for candidate_str in candidates:
            j = int(candidate_str)
            if j > i and j not in to_remove:
                # j mirip dengan i → hapus j (simpan yang pertama)
                to_remove.add(j)
    
    return to_remove
