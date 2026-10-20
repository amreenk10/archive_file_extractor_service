from app.config import Config
from app.services.task_pool import get_task_pool,shutdown_task_pool
from app.services.task_pool import _executor

def test_shutdown_task_pool():
   
    pool=get_task_pool()
    assert pool is not None
    shutdown_task_pool()
  
    assert _executor is None
