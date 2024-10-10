# Flask Backend with PostgreSQL and Socket.IO

This is a Flask-based backend application that integrates Socket.IO for real-time communication and uses PostgreSQL as the database. The project features manual database migration using raw SQL scripts, without the use of an ORM (Object Relational Mapper).

## Features

- **Flask Framework**: Serves as the backend framework.
- **Socket.IO**: Real-time communication with clients.
- **PostgreSQL**: Database integration using raw SQL (no ORM).
- **Manual SQL Migrations**: SQL scripts for managing database schema, with no migration history tracking.
  
## Requirements

Before you begin, ensure you have the following installed on your local machine:

- Python 3.x
- PostgreSQL
- pip (Python package manager)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-repo-name/backend-project.git
cd backend-project
```

### 2. Set Up a Virtual Environment (Optional but recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
#### Create a .env file in the root of your project and add your PostgreSQL database credentials:
```bash
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_DB=your_database_name
POSTGRES_HOST=your_postgres_host
POSTGRES_PORT=your_postgres_port
```

### 5. Set Up the Database
#### Make sure your PostgreSQL database is running, then create the database specified in the `.env` file:
```bash
psql -U your_postgres_user -c "CREATE DATABASE your_database_name;"
```

### 6. Run Database Migrations
#### To apply the SQL migration scripts located in the `migrations/` folder, run the following command:
```bash
psql -U your_postgres_user -c "CREATE DATABASE your_database_name;"
```
#### This will execute all the SQL scripts in the migrations folder.

## Installation

#### To start the Flask server along with Socket.IO:
```bash
python run.py
```
#### By default, the application will run on http://localhost:5000/

## Project Structure

```bash
/backend-project
│
├── /app
│   ├── __init__.py          # Initialize Flask and Socket.IO
│   ├── db.py                # Database connection handling
│   ├── routes.py            # Define your application routes here
│   ├── socket_service.py    # Socket.IO event handlers
│   └── config.py            # Configuration settings (e.g., environment)
│
├── /migrations               # Folder for SQL migration scripts
│   └── 001_initial_schema.sql
│
├── migrate.py                # Migration script to apply SQL files
├── run.py                    # Main entry point for running the server
├── .env                      # Environment variables (DB credentials)
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

## License

#### This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

