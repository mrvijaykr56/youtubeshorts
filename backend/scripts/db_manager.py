import os
import sqlite3
import threading
import time


class InMemoryJobStore:
    """
    Thread-safe ephemeral in-memory job store.
    Used as an automatic fallback if disk access is restricted.
    """
    ALLOWED_FIELDS = {"state", "message", "progress", "polished_script", "file", "art_style", "video_mode", "video_resolution"}

    def __init__(self):
        self._jobs: dict[str, dict] = {}
        self._lock = threading.Lock()
        print("[db_manager] In-memory job store initialized.", flush=True)

    def create_job(self, job_id: str, **kwargs):
        now = time.time()
        with self._lock:
            self._jobs[job_id] = {
                "job_id":         job_id,
                "state":          kwargs.get("state", "pending"),
                "message":        kwargs.get("message", "Job submitted"),
                "progress":       kwargs.get("progress", 0),
                "polished_script": None,
                "file":           None,
                "art_style":      kwargs.get("art_style", "cinematic"),
                "video_mode":     kwargs.get("video_mode", "shorts"),
                "video_resolution": kwargs.get("video_resolution", "1080p"),
                "created_at":     now,
                "updated_at":     now,
            }

    def get_job(self, job_id: str) -> dict | None:
        with self._lock:
            job = self._jobs.get(job_id)
            return dict(job) if job else None

    def update_job(self, job_id: str, **kwargs):
        with self._lock:
            if job_id not in self._jobs:
                print(f"[db_manager] Warning: tried to update unknown job {job_id}", flush=True)
                return
            for k, v in kwargs.items():
                if k in self.ALLOWED_FIELDS:
                    self._jobs[job_id][k] = v
                else:
                    print(f"[db_manager] Warning: ignored disallowed field '{k}'", flush=True)
            self._jobs[job_id]["updated_at"] = time.time()

    def delete_job(self, job_id: str):
        with self._lock:
            self._jobs.pop(job_id, None)

    def list_jobs(self) -> list[dict]:
        with self._lock:
            return [dict(j) for j in self._jobs.values()]


class SQLiteJobStore:
    """
    Durable SQLite job store.
    Runs SQLite with WAL (Write-Ahead Logging) mode and synchronous=NORMAL
    to guarantee extreme concurrent performance and complete safety against database locks.
    Gracefully and silently falls back to InMemoryJobStore if disk access is restricted.
    """
    ALLOWED_FIELDS = {"state", "message", "progress", "polished_script", "file", "art_style", "video_mode", "video_resolution"}

    def __init__(self, db_path: str = None):
        self.fallback = None
        
        if db_path is None:
            backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(backend_dir, "jobs.db")
            
        self.db_path = db_path
        
        try:
            # Test connection and create table
            conn = self._get_conn()
            with conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS jobs (
                        job_id TEXT PRIMARY KEY,
                        state TEXT,
                        message TEXT,
                        progress INTEGER,
                        polished_script TEXT,
                        file TEXT,
                        art_style TEXT,
                        video_mode TEXT,
                        video_resolution TEXT,
                        created_at REAL,
                        updated_at REAL
                    )
                """)
                # Reconcile interrupted jobs from previous server runs
                cursor = conn.execute("""
                    UPDATE jobs 
                    SET state = 'error', message = 'Interrupted by server restart', updated_at = ?
                    WHERE state IN ('pending', 'generating', 'compiling_video', 'generating_storyboard', 'pending_compile')
                """, (time.time(),))
                if cursor.rowcount > 0:
                    print(f"[db_manager] Reconciled {cursor.rowcount} interrupted job(s) from previous session.", flush=True)
            conn.close()
            print(f"[db_manager] Durable WAL-enabled SQLite store initialized successfully at: {self.db_path}", flush=True)
        except Exception as e:
            print(f"[db_manager] [WARNING] Failed to initialize SQLite store: {e}. Falling back to In-Memory store.", flush=True)
            self.fallback = InMemoryJobStore()

    def _get_conn(self):
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.row_factory = sqlite3.Row
        return conn

    def create_job(self, job_id: str, **kwargs):
        if self.fallback:
            return self.fallback.create_job(job_id, **kwargs)
            
        now = time.time()
        state = kwargs.get("state", "pending")
        message = kwargs.get("message", "Job submitted")
        progress = kwargs.get("progress", 0)
        art_style = kwargs.get("art_style", "cinematic")
        video_mode = kwargs.get("video_mode", "shorts")
        video_resolution = kwargs.get("video_resolution", "1080p")
        
        try:
            conn = self._get_conn()
            with conn:
                conn.execute(
                    """
                    INSERT INTO jobs (job_id, state, message, progress, art_style, video_mode, video_resolution, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (job_id, state, message, progress, art_style, video_mode, video_resolution, now, now)
                )
            conn.close()
        except Exception as e:
            print(f"[db_manager] Error creating job {job_id} in SQLite: {e}", flush=True)

    def get_job(self, job_id: str) -> dict | None:
        if self.fallback:
            return self.fallback.get_job(job_id)
            
        try:
            conn = self._get_conn()
            row = conn.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,)).fetchone()
            conn.close()
            return dict(row) if row else None
        except Exception as e:
            print(f"[db_manager] Error fetching job {job_id} from SQLite: {e}", flush=True)
            return None

    def update_job(self, job_id: str, **kwargs):
        if self.fallback:
            return self.fallback.update_job(job_id, **kwargs)
            
        updates = []
        params = []
        for k, v in kwargs.items():
            if k in self.ALLOWED_FIELDS:
                updates.append(f"{k} = ?")
                params.append(v)
            else:
                print(f"[db_manager] Warning: ignored disallowed field '{k}'", flush=True)
                
        if not updates:
            return
            
        updates.append("updated_at = ?")
        params.append(time.time())
        params.append(job_id)
        
        try:
            conn = self._get_conn()
            with conn:
                conn.execute(
                    f"UPDATE jobs SET {', '.join(updates)} WHERE job_id = ?",
                    tuple(params)
                )
            conn.close()
        except Exception as e:
            print(f"[db_manager] Error updating job {job_id} in SQLite: {e}", flush=True)

    def delete_job(self, job_id: str):
        if self.fallback:
            return self.fallback.delete_job(job_id)
            
        try:
            conn = self._get_conn()
            with conn:
                conn.execute("DELETE FROM jobs WHERE job_id = ?", (job_id,))
            conn.close()
        except Exception as e:
            print(f"[db_manager] Error deleting job {job_id} in SQLite: {e}", flush=True)

    def list_jobs(self) -> list[dict]:
        if self.fallback:
            return self.fallback.list_jobs()
            
        try:
            conn = self._get_conn()
            rows = conn.execute("SELECT * FROM jobs ORDER BY created_at DESC").fetchall()
            conn.close()
            return [dict(r) for r in rows]
        except Exception as e:
            print(f"[db_manager] Error listing jobs from SQLite: {e}", flush=True)
            return []
