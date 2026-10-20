import os
import zipfile
import fnmatch
import shutil
import uuid
import logging
from datetime import datetime, timezone

logger=logging.getLogger(__name__)

def handle_zip(file_path, display_chain, depth, pattern, workspace_dir, matches, job_id, recursive_trigger, source_archive_name=None):
    logger.info(f"Opening ZIP archive: {display_chain} (Depth: {depth})")
    
    with zipfile.ZipFile(file_path, 'r') as zf:
        for member in zf.infolist():
            if member.is_dir():
                continue
            
            current_chain=f"{display_chain}/{member.filename}"
            base_name=os.path.basename(member.filename)
            
            if fnmatch.fnmatch(member.filename, pattern):
                logger.info(f"Match found: {current_chain}")
                matches.append({
                    "job_id": job_id,
                    "full_path":current_chain,
                    "file_name":base_name,
                    "file_size":member.file_size,
                    "nesting_depth": depth,
                    "source_archive_name": source_archive_name, 
                    "extracted_at":datetime.now(timezone.utc)
                })

            if member.filename.lower().endswith(('.zip', '.tar', '.tar.gz', '.tgz')):
                logger.info(f"Nested archive discovered: {current_chain}. Streaming to disk...")
                
                unique_prefix=uuid.uuid4().hex[:6]
                nested_filename=f"depth{depth}_{unique_prefix}_{base_name}"
                nested_target_path=os.path.join(workspace_dir, nested_filename)
                
                with zf.open(member) as source, open(nested_target_path, "wb") as target:
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
