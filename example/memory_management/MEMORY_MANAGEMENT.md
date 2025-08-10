# Memory Management in PyTgCalls

PyTgCalls sekarang dilengkapi dengan sistem manajemen memori yang canggih untuk mencegah memory leaks dan mengoptimalkan penggunaan memori.

## Fitur Utama

### 1. Memory Manager Otomatis
- **Cleanup Otomatis**: Membersihkan cache yang expired secara berkala
- **Monitoring Memory**: Memantau penggunaan memori secara real-time
- **Garbage Collection**: Memaksa garbage collection untuk membebaskan memori
- **Logging**: Mencatat statistik memori dan peringatan

### 2. Cache Management yang Diperbaiki
- **Expired Entry Cleanup**: Menghapus cache entries yang sudah expired
- **Size Monitoring**: Memantau ukuran cache
- **Manual Cleanup**: Kemampuan untuk membersihkan cache secara manual

### 3. Resource Cleanup yang Komprehensif
- **ThreadPoolExecutor Shutdown**: Mematikan executor dengan benar
- **Handler Cleanup**: Membersihkan semua registered handlers
- **Chat Lock Cleanup**: Membersihkan chat locks yang tidak terpakai
- **Weak References**: Menggunakan weak references untuk cleanup otomatis

## Cara Penggunaan

### Inisialisasi dengan Memory Management

```python
from pytgcalls import PyTgCalls

# Dengan memory management enabled (default)
call_py = PyTgCalls(
    app,
    enable_memory_manager=True,
    memory_cleanup_interval=300,  # Cleanup setiap 5 menit
    cache_duration=3600,  # Cache duration 1 jam
)

# Tanpa memory management
call_py = PyTgCalls(
    app,
    enable_memory_manager=False,
)
```

### Monitoring Memory

```python
# Dapatkan statistik memori
stats = call_py.get_memory_stats()
print(f"Memory Usage: {stats['usage']['rss_mb']:.1f} MB")
print(f"Memory Increase: +{stats['increase']['rss_increase_mb']:.1f} MB")

# Force cleanup manual
cleanup_stats = await call_py.force_cleanup()
print(f"Cleaned {cleanup_stats['user_peer_cache']['cleaned']} cache entries")
```

### Proper Shutdown

```python
# Shutdown dengan cleanup yang proper
await call_py.shutdown()
```

## Konfigurasi Memory Manager

### Parameter Konfigurasi

- `enable_memory_manager` (bool): Mengaktifkan/menonaktifkan memory manager
- `memory_cleanup_interval` (int): Interval cleanup dalam detik (default: 300)
- `cache_duration` (int): Durasi cache dalam detik (default: 3600)

### Logging

Memory manager akan mencatat informasi berikut:
- Penggunaan memori saat ini
- Peningkatan memori sejak startup
- Jumlah item yang dibersihkan
- Peringatan jika ada peningkatan memori yang signifikan

## Best Practices

### 1. Gunakan Memory Management untuk Production
```python
# Untuk aplikasi production
call_py = PyTgCalls(
    app,
    enable_memory_manager=True,
    memory_cleanup_interval=300,  # Cleanup setiap 5 menit
)
```

### 2. Monitor Memory Usage
```python
# Periksa memory usage secara berkala
stats = call_py.get_memory_stats()
if stats['increase']['rss_increase_mb'] > 50:
    print("Warning: Memory increase detected!")
```

### 3. Force Cleanup Saat Diperlukan
```python
# Force cleanup setelah operasi berat
await call_py.force_cleanup()
```

### 4. Proper Shutdown
```python
# Selalu gunakan shutdown yang proper
try:
    # Your application code
    pass
finally:
    await call_py.shutdown()
```

## Troubleshooting

### Memory Leak Detection

Jika Anda mendeteksi memory leak:

1. **Enable Memory Manager**:
   ```python
   call_py = PyTgCalls(app, enable_memory_manager=True)
   ```

2. **Monitor Logs**:
   Memory manager akan mencatat peringatan jika ada peningkatan memori > 10MB

3. **Force Cleanup**:
   ```python
   await call_py.force_cleanup()
   ```

4. **Check Cache Sizes**:
   ```python
   stats = call_py.get_memory_stats()
   print(f"Cache size: {stats['usage']}")
   ```

### Performance Optimization

1. **Adjust Cleanup Interval**:
   - Interval yang lebih pendek = cleanup lebih sering = memory lebih rendah
   - Interval yang lebih panjang = performance lebih baik = memory lebih tinggi

2. **Adjust Cache Duration**:
   - Durasi yang lebih pendek = cache lebih kecil = memory lebih rendah
   - Durasi yang lebih panjang = cache hit lebih tinggi = performance lebih baik

## Dependencies

Untuk menggunakan fitur memory monitoring, install psutil:

```bash
pip install psutil
```

Atau install dengan optional dependencies:

```bash
pip install "anthraleia-pytgcalls[memory-monitoring]"
```

## Contoh Lengkap

Lihat file `example/memory_management_example.py` untuk contoh penggunaan lengkap dengan command handlers untuk monitoring dan testing memory management.

## Perubahan dari Versi Sebelumnya

### Perbaikan Memory Leak:
1. **ThreadPoolExecutor Shutdown**: Executor sekarang di-shutdown dengan benar
2. **Cache Cleanup**: Cache entries yang expired dihapus otomatis
3. **Handler Cleanup**: Handlers dibersihkan saat shutdown
4. **Chat Lock Cleanup**: Chat locks dibersihkan untuk mencegah memory leak
5. **Weak References**: Menggunakan weak references untuk cleanup otomatis

### Fitur Baru:
1. **Memory Manager**: Sistem monitoring dan cleanup otomatis
2. **Memory Statistics**: API untuk mendapatkan statistik memori
3. **Force Cleanup**: Kemampuan untuk memaksa cleanup manual
4. **Proper Shutdown**: Method shutdown yang komprehensif

### Optimasi:
1. **Reduced Memory Footprint**: Penggunaan memori yang lebih efisien
2. **Automatic Cleanup**: Cleanup otomatis untuk mencegah memory leak
3. **Better Resource Management**: Manajemen resource yang lebih baik
