import shutil
from pathlib import Path
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_project_structure():
    """Create the necessary project directories."""
    # Define base paths
    project_root = Path(__file__).parent.parent
    dirs_to_create = [
        project_root / "data" / "raw",
        project_root / "data" / "processed",
        project_root / "output" / "plots",
        project_root / "output" / "dashboards",
        project_root / "logs"
    ]
    
    # Create directories
    for dir_path in dirs_to_create:
        dir_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {dir_path}")
    
    return project_root

def copy_source_data(source_root: Path, target_root: Path):
    """
    Copy source data to project directory.
    
    Args:
        source_root (Path): Path to source data
        target_root (Path): Path to project root
    """
    # Define source and target paths
    anfragen_source = source_root / "Anfragen" / "pdfs"
    beantwortungen_source = source_root / "Beantwortungen" / "pdfs"
    
    data_dir = target_root / "data" / "raw"
    anfragen_target = data_dir / "anfragen"
    beantwortungen_target = data_dir / "beantwortungen"
    
    # Copy directories
    for source, target in [(anfragen_source, anfragen_target),
                          (beantwortungen_source, beantwortungen_target)]:
        if source.exists():
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(source, target)
            logger.info(f"Copied data from {source} to {target}")
        else:
            logger.error(f"Source directory not found: {source}")

def main():
    """Main setup function."""
    try:
        # Setup project structure
        project_root = setup_project_structure()
        logger.info("Project structure setup completed")
        
        # Define source data root
        source_root = Path("../raw_data/alle_Anfragen_Beantwortungen")
        
        # Copy source data
        copy_source_data(source_root, project_root)
        logger.info("Data copy completed")
        
        # Create timestamp file to track last update
        timestamp_file = project_root / "data" / "last_update.txt"
        with open(timestamp_file, 'w') as f:
            f.write(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("Setup completed successfully")
        
    except Exception as e:
        logger.error(f"Setup failed: {str(e)}")
        raise

if __name__ == "__main__":
    main() 