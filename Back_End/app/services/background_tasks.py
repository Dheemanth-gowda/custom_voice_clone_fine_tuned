import os
import psutil
import time
from celery import Celery
from celery.signals import worker_process_init
from app.core.config import settings
from app.services.voice_cloning import VoiceCloningService
from app.core.logging import get_logger

logger = get_logger(__name__)

# Initialize Celery
celery_app = Celery(
    "voice_clone_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Add performance-related settings
    worker_max_tasks_per_child=1,  # Restart worker after each task
    worker_prefetch_multiplier=1,  # Process one task at a time
    task_time_limit=3600,  # 1 hour max per task
    task_soft_time_limit=3000,  # Soft limit at 50 minutes
    worker_max_memory_per_child=512000,  # 512MB max memory per worker
)

class PerformanceMonitor:
    def __init__(self):
        self.cpu_threshold = 80  # 80% CPU usage threshold
        self.memory_threshold = 80  # 80% memory usage threshold
        self.disk_threshold = 90  # 90% disk usage threshold

    def check_system_resources(self):
        """Check if system resources are within acceptable limits."""
        try:
            # Check CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > self.cpu_threshold:
                logger.warning(f"High CPU usage detected: {cpu_percent}%")
                return False

            # Check memory usage
            memory = psutil.virtual_memory()
            if memory.percent > self.memory_threshold:
                logger.warning(f"High memory usage detected: {memory.percent}%")
                return False

            # Check disk usage
            disk = psutil.disk_usage('/')
            if disk.percent > self.disk_threshold:
                logger.warning(f"High disk usage detected: {disk.percent}%")
                return False

            return True

        except Exception as e:
            logger.error(f"Error checking system resources: {str(e)}")
            return False

    def wait_for_resources(self, timeout=300):
        """
        Wait for system resources to become available.
        
        Args:
            timeout: Maximum time to wait in seconds
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.check_system_resources():
                return True
            time.sleep(10)  # Wait 10 seconds before checking again
        return False

class BackgroundTaskService:
    def __init__(self):
        self.voice_cloning = VoiceCloningService()
        self.performance_monitor = PerformanceMonitor()

    @celery_app.task(name="train_voice_model", bind=True)
    def train_voice_model(self, task, model_id: int):
        """
        Background task for training voice models.
        
        Args:
            model_id: ID of the voice model to train
        """
        try:
            # Check system resources before starting
            if not self.performance_monitor.wait_for_resources():
                raise Exception("System resources not available for training")

            logger.info(f"Starting background training for model {model_id}")
            
            # Get database session
            from app.db.session import SessionLocal
            db = SessionLocal()
            
            # Train model
            result = self.voice_cloning.train_model(model_id, db)
            
            logger.info(f"Completed training for model {model_id}")
            return result

        except Exception as e:
            logger.error(f"Error in background training for model {model_id}: {str(e)}")
            raise
        finally:
            db.close()

    @celery_app.task(name="generate_long_speech", bind=True)
    def generate_long_speech(self, task, model_id: int, text: str):
        """
        Background task for generating long speech.
        
        Args:
            model_id: ID of the voice model to use
            text: Text to convert to speech
        """
        try:
            # Check system resources before starting
            if not self.performance_monitor.wait_for_resources():
                raise Exception("System resources not available for generation")

            logger.info(f"Starting background speech generation for model {model_id}")
            
            # Get database session
            from app.db.session import SessionLocal
            db = SessionLocal()
            
            # Generate speech
            output_path = self.voice_cloning.generate_speech(model_id, text, db)
            
            logger.info(f"Completed speech generation for model {model_id}")
            return {"output_path": output_path}

        except Exception as e:
            logger.error(f"Error in background speech generation for model {model_id}: {str(e)}")
            raise
        finally:
            db.close()

    @celery_app.task(name="cleanup_storage", bind=True)
    def cleanup_storage(self, task):
        """
        Background task for cleaning up old models and samples.
        """
        try:
            # Check system resources before starting
            if not self.performance_monitor.wait_for_resources():
                raise Exception("System resources not available for cleanup")

            logger.info("Starting storage cleanup")
            
            # Get database session
            from app.db.session import SessionLocal
            db = SessionLocal()
            
            # Cleanup storage
            result = self.voice_cloning.cleanup_old_models(db)
            
            logger.info("Completed storage cleanup")
            return result

        except Exception as e:
            logger.error(f"Error in storage cleanup: {str(e)}")
            raise
        finally:
            db.close()

    def schedule_training(self, model_id: int):
        """
        Schedule a model training task.
        
        Args:
            model_id: ID of the voice model to train
        """
        return self.train_voice_model.delay(model_id)

    def schedule_speech_generation(self, model_id: int, text: str):
        """
        Schedule a speech generation task.
        
        Args:
            model_id: ID of the voice model to use
            text: Text to convert to speech
        """
        return self.generate_long_speech.delay(model_id, text)

    def schedule_cleanup(self):
        """
        Schedule a storage cleanup task.
        """
        return self.cleanup_storage.delay()

@worker_process_init.connect
def setup_worker(**kwargs):
    """
    Initialize worker process with performance monitoring.
    """
    try:
        # Set process priority to below normal
        import os
        os.nice(10)  # Lower process priority
        
        # Set CPU affinity to use only specific cores
        process = psutil.Process()
        if psutil.cpu_count() > 2:
            # Leave one core free for system
            process.cpu_affinity([0, 1])
        
        logger.info("Worker process initialized with performance settings")
    except Exception as e:
        logger.error(f"Error setting up worker process: {str(e)}") 