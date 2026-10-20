import os
import tarfile
import fnmatch
import shutil
import uuid
import logging
from datetime import datetime, timezone

logger=logging.getLogger(__name__)

def handle_tar(file_path, display_chain, depth, pattern, workspace_dir, matches, job_id, recursive_trigger, source_archive_name=None):
    logger.info(f"Opening TAR archive: {display_chain} (Depth: {depth})")

    with tarfile.open(file_path,'r:*') as tf:
        for member in tf.getmembers():
            if not member.isfile():
                continue
            
            current_chain=f"{display_chain}/{member.name}"
            base_name =os.path.basename(member.name)
            
            if fnmatch.fnmatch(member.name,pattern):
                logger.info(f"Match found: {current_chain}")
                matches.append({
                    "job_id": job_id,
                    "full_path":current_chain,
                    "file_name":base_name,
                    "file_size":member.size, 
                    "nesting_depth":depth,
                    "source_archive_name":source_archive_name,
                    "extracted_at":datetime.now(timezone.utc)
                })
                
            if member.name.lower().endswith(('.zip', '.tar', '.tar.gz', '.tgz')):
                logger.info(f"Nested archive discovered: {current_chain}. Streaming to disk...")
                
                unique_prefix=uuid.uuid4().hex[:6]
                nested_filename =f"depth{depth}_{unique_prefix}_{base_name}"
                nested_target_path=os.path.join(workspace_dir, nested_filename)
                
                with tf.extractfile(member) as source, open(nested_target_path, "wb") as target:
                    shutil.copyfileobj(source, target)
                    
                recursive_trigger(
                    file_path=nested_target_path,
                    display_chain=current_chain,
                    depth=depth + 1,
                    pattern=pattern,
                    workspace_dir=workspace_dir,
                    matches=matches,
                    job_id=job_id,
                    source_archive_name=source_archive_name
                )

                if os.path.exists(nested_target_path):
                    try:
                        os.remove(nested_target_path)
                    except OSError:
                        pass
