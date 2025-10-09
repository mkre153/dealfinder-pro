"""
Setup script for DealFinder Pro
Handles installation, database initialization, and configuration
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import json


class DealFinderSetup:
    """Interactive setup wizard for DealFinder Pro"""

    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.config_path = self.base_dir / 'config.json'
        self.env_path = self.base_dir / '.env'
        self.env_example_path = self.base_dir / '.env.example'

    def run(self):
        """Run complete setup process"""
        print("=" * 60)
        print("DealFinder Pro - Installation Wizard")
        print("=" * 60)
        print()

        # Check Python version
        if not self.check_python_version():
            return False

        # Install dependencies
        if not self.install_dependencies():
            return False

        # Create directories
        self.create_directories()

        # Setup environment variables
        if not self.setup_environment():
            return False

        # Configure database
        if not self.configure_database():
            return False

        # Setup GoHighLevel (optional)
        self.setup_ghl()

        # Configure email notifications
        self.setup_email()

        # Finalize
        self.finalize_setup()

        print()
        print("=" * 60)
        print("Setup Complete! 🎉")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Review and customize config.json")
        print("2. Test database: python main.py --test-db")
        print("3. Test GHL (if enabled): python main.py --test-ghl")
        print("4. Run test scrape: python main.py --test-scrape 90210")
        print("5. Run full workflow: python main.py --full-workflow")
        print()

        return True

    def check_python_version(self):
        """Verify Python version meets requirements"""
        print("Checking Python version...")

        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 9):
            print(f"❌ Python 3.9+ required. You have {version.major}.{version.minor}")
            return False

        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True

    def install_dependencies(self):
        """Install Python dependencies from requirements.txt"""
        print()
        print("Installing dependencies...")

        if not (self.base_dir / 'requirements.txt').exists():
            print("❌ requirements.txt not found")
            return False

        try:
            subprocess.run(
                [sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'],
                check=True,
                cwd=self.base_dir
            )
            print("✅ Dependencies installed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False

    def create_directories(self):
        """Create required directories"""
        print()
        print("Creating directories...")

        directories = ['logs', 'reports', 'backups', 'data', 'imports']

        for directory in directories:
            path = self.base_dir / directory
            path.mkdir(exist_ok=True)
            print(f"  ✅ {directory}/")

    def setup_environment(self):
        """Setup .env file"""
        print()
        print("Setting up environment variables...")

        if self.env_path.exists():
            response = input(".env file already exists. Overwrite? (y/N): ")
            if response.lower() != 'y':
                print("Skipping .env setup")
                return True

        # Copy from example
        if self.env_example_path.exists():
            shutil.copy(self.env_example_path, self.env_path)
            print("✅ Created .env from template")
        else:
            # Create minimal .env
            with open(self.env_path, 'w') as f:
                f.write("# DealFinder Pro Environment Variables\n")
                f.write("# Fill in your credentials below\n\n")
            print("✅ Created empty .env")

        print()
        print("Please edit .env file with your credentials:")
        print(f"  {self.env_path}")

        return True

    def configure_database(self):
        """Configure database connection"""
        print()
        print("=" * 60)
        print("Database Configuration")
        print("=" * 60)

        db_type = self.prompt_choice(
            "Select database type:",
            ['postgresql', 'mysql', 'sqlite'],
            default='postgresql'
        )

        if db_type == 'sqlite':
            print("Using SQLite (for development/testing only)")
            db_config = {
                'type': 'sqlite',
                'database': 'dealfinder.db',
                'enabled': True
            }
        else:
            print(f"\nConfiguring {db_type.upper()}...")

            db_host = input(f"Database host [localhost]: ").strip() or 'localhost'
            db_port = input(f"Database port [{self.get_default_port(db_type)}]: ").strip()
            db_port = int(db_port) if db_port else self.get_default_port(db_type)
            db_name = input("Database name [dealfinder]: ").strip() or 'dealfinder'
            db_user = input(f"Database user [{os.getenv('USER', 'postgres')}]: ").strip() or os.getenv('USER', 'postgres')

            db_config = {
                'type': db_type,
                'host': db_host,
                'port': db_port,
                'database': db_name,
                'enabled': True,
                'min_connections': 2,
                'max_connections': 10
            }

            # Update .env with database credentials
            print("\nUpdating .env with database credentials...")
            self.update_env_file('DB_USER', db_user)
            self.update_env_file('DB_HOST', db_host)
            self.update_env_file('DB_PORT', str(db_port))
            self.update_env_file('DB_NAME', db_name)
            print("✅ Database credentials added to .env")
            print("⚠️  Don't forget to set DB_PASSWORD in .env!")

        # Update config.json
        self.update_config('databases.primary', db_config)
        print("✅ Database configuration saved to config.json")

        # Initialize database schema
        if self.prompt_yes_no("\nInitialize database schema now?", default=True):
            self.initialize_database_schema()

        return True

    def setup_ghl(self):
        """Setup GoHighLevel integration"""
        print()
        print("=" * 60)
        print("GoHighLevel Integration (Optional)")
        print("=" * 60)

        if not self.prompt_yes_no("Enable GoHighLevel integration?", default=True):
            self.update_config('gohighlevel.enabled', False)
            print("GHL integration disabled")
            return

        print("\nYou'll need:")
        print("  - GHL API Key")
        print("  - GHL Location ID")
        print("  - Pipeline ID")
        print("  - Workflow IDs (optional)")
        print()
        print("See GHL_SETUP_GUIDE.md for detailed instructions")
        print()

        if self.prompt_yes_no("Configure GHL now?", default=False):
            print("\nGHL API Key and Location ID should be added to .env:")
            print("  GHL_API_KEY=your_api_key")
            print("  GHL_LOCATION_ID=your_location_id")
            print()

            pipeline_id = input("Pipeline ID (optional, press Enter to skip): ").strip()
            if pipeline_id:
                self.update_config('gohighlevel.pipeline_id', pipeline_id)
                print("✅ Pipeline ID saved")

            self.update_config('gohighlevel.enabled', True)
        else:
            print("You can configure GHL later by:")
            print("  1. Adding credentials to .env")
            print("  2. Updating config.json with pipeline/workflow IDs")
            print("  3. Running: python main.py --test-ghl")

    def setup_email(self):
        """Setup email notifications"""
        print()
        print("=" * 60)
        print("Email Notifications")
        print("=" * 60)

        if not self.prompt_yes_no("Enable email notifications?", default=True):
            self.update_config('notifications.email.enabled', False)
            return

        print("\nFor Gmail, you'll need an App Password:")
        print("  https://myaccount.google.com/apppasswords")
        print()

        smtp_server = input("SMTP server [smtp.gmail.com]: ").strip() or 'smtp.gmail.com'
        smtp_port = input("SMTP port [587]: ").strip() or '587'
        sender = input("Sender email: ").strip()
        recipient = input("Recipient email: ").strip()

        email_config = {
            'enabled': True,
            'smtp_server': smtp_server,
            'smtp_port': int(smtp_port),
            'sender': sender,
            'recipient': recipient,
            'include_excel_attachment': True
        }

        self.update_config('notifications.email', email_config)
        print("✅ Email configuration saved")
        print("⚠️  Don't forget to add EMAIL_USERNAME and EMAIL_PASSWORD to .env!")

    def initialize_database_schema(self):
        """Initialize database schema"""
        schema_file = self.base_dir / 'database' / 'schema.sql'

        if not schema_file.exists():
            print("❌ Schema file not found: database/schema.sql")
            return False

        print("\nInitializing database schema...")
        print("This will create all required tables.")
        print()

        # Read database config from .env
        from dotenv import load_dotenv
        load_dotenv(self.env_path)

        db_type = os.getenv('DB_TYPE', 'postgresql')
        db_name = os.getenv('DB_NAME', 'dealfinder')

        if db_type == 'postgresql':
            cmd = f"psql {db_name} < {schema_file}"
            print(f"Run this command:")
            print(f"  {cmd}")
            print()
        elif db_type == 'mysql':
            cmd = f"mysql {db_name} < {schema_file}"
            print(f"Run this command:")
            print(f"  {cmd}")
            print()
        else:
            print("SQLite schema will be created automatically on first run")

        return True

    def finalize_setup(self):
        """Final setup steps"""
        print()
        print("Creating .gitignore...")

        gitignore_content = """
# DealFinder Pro - Git Ignore

# Environment variables
.env
.env.local

# Database
*.db
*.sqlite
*.sqlite3

# Logs
logs/*.log

# Reports
reports/*.xlsx
reports/*.csv

# Backups
backups/*.sql
backups/*.dump

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo
.DS_Store

# Testing
.pytest_cache/
.coverage
htmlcov/

# Data
data/*.csv
data/*.json
imports/*.csv
        """.strip()

        gitignore_path = self.base_dir / '.gitignore'
        with open(gitignore_path, 'w') as f:
            f.write(gitignore_content)

        print("✅ .gitignore created")

    # ========================================
    # HELPER METHODS
    # ========================================

    def prompt_choice(self, question, choices, default=None):
        """Prompt user to select from choices"""
        print(f"\n{question}")
        for i, choice in enumerate(choices, 1):
            marker = " (default)" if choice == default else ""
            print(f"  {i}. {choice}{marker}")

        while True:
            response = input("Select: ").strip()
            if not response and default:
                return default

            try:
                idx = int(response) - 1
                if 0 <= idx < len(choices):
                    return choices[idx]
            except ValueError:
                pass

            print("Invalid choice. Try again.")

    def prompt_yes_no(self, question, default=True):
        """Prompt yes/no question"""
        default_str = "Y/n" if default else "y/N"
        response = input(f"{question} [{default_str}]: ").strip().lower()

        if not response:
            return default

        return response in ['y', 'yes']

    def get_default_port(self, db_type):
        """Get default port for database type"""
        ports = {
            'postgresql': 5432,
            'mysql': 3306,
            'sqlserver': 1433
        }
        return ports.get(db_type, 5432)

    def update_config(self, key_path, value):
        """Update config.json with dotted key path"""
        # Load config
        with open(self.config_path) as f:
            config = json.load(f)

        # Navigate to nested key
        keys = key_path.split('.')
        target = config
        for key in keys[:-1]:
            if key not in target:
                target[key] = {}
            target = target[key]

        # Set value
        target[keys[-1]] = value

        # Save config
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)

    def update_env_file(self, key, value):
        """Update .env file with key=value"""
        lines = []

        if self.env_path.exists():
            with open(self.env_path) as f:
                lines = f.readlines()

        # Check if key exists
        found = False
        for i, line in enumerate(lines):
            if line.startswith(f"{key}="):
                lines[i] = f"{key}={value}\n"
                found = True
                break

        # Add if not found
        if not found:
            lines.append(f"{key}={value}\n")

        # Write back
        with open(self.env_path, 'w') as f:
            f.writelines(lines)


def main():
    """Main entry point"""
    setup = DealFinderSetup()

    try:
        success = setup.run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nSetup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
