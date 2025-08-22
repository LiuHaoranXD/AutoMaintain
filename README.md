# AutoMaintain - Intelligent Maintenance Management System

AutoMaintain is an intelligent maintenance management system that handles tenant maintenance requests, automatically classifies issues, schedules repairs, and coordinates between tenants, maintenance staff, and vendors.

## Features

### Core Features

📝 Request Submission Form: Tenant interface for submitting maintenance requests  
🤖 AI Auto Classification: Automatic issue categorization and priority assignment  
📊 Status Tracking: Real-time request progress updates  
📧 Communication System: Email notifications to relevant parties  
🔍 Solution Database: Vector search for common maintenance solutions  
📅 Calendar Integration: Automatic scheduling of maintenance appointments  

### Advanced Features

👥 Vendor Management: Route requests to appropriate service providers  
💰 Cost Estimation: AI-driven repair cost prediction  
📚 Knowledge Base Management: Upload documents to enhance the AI knowledge base  

## Installation & Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation Steps
1. Clone or download the project files
2. Install required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3. Set environment variables:
    Create a `.env` file or set the following in `run.py`:
    ```env
    OPENAI_API_KEY=your_openai_api_key
    SMTP_USER=your_email_address
    SMTP_PASS=your_app_password
    SMTP_SERVER=smtp.gmail.com (or other SMTP server)
    SMTP_PORT=587
    AUTOMAINTAIN_DB_PATH=./automaintain.db
    CHROMA_DB_DIR=./chroma_db
    ```
4. Initialize the database:
    ```bash
    python -c "from db_init import init_db; init_db()"
    ```
5. Run the application:
    ```bash
    python run.py
    ```
6. Open [http://localhost:8501](http://localhost:8501) in your browser to access the app

## Configuration

### OpenAI API Setup
- Register an account on the OpenAI platform
- Generate an API key
- Set `OPENAI_API_KEY` in your environment variables

### Email Setup (Gmail Example)
- Enable Gmail two-factor authentication
- Generate an app-specific password:
   - Log in to Gmail → Account Settings → Security
   - Enable two-factor authentication (if not already enabled)
   - Generate a new password in the "App Passwords" section
- Set the following in your environment variables:
   - `SMTP_USER`: Your Gmail address
   - `SMTP_PASS`: The generated app password

### Database Configuration
- The system uses an SQLite database, default location is `./automaintain.db`. You can change the location by setting the `AUTOMAINTAIN_DB_PATH` environment variable.

## User Guide

### Tenant Interface
- Select "Tenant Request Form"
- Fill in maintenance request details
- AI will automatically classify the issue and suggest solutions
- After submitting, the system sends a confirmation email

### Admin Interface
- Select "Admin Dashboard" to view all requests
- Use filters to view requests by status, category, or priority
- Update request status and assign vendors
- View analytics charts and statistics

### Vendor Management
- Select "Vendor Management" to view and manage vendors
- Add new vendors and set specialties and rates
- View vendor performance statistics

### Knowledge Base Management
- Select "Knowledge Base" to upload maintenance documents
- Supports PDF, TXT, and MD file formats
- Uploaded documents enhance AI response capabilities

### Calendar View
- Select "Calendar View" to view and manage appointments
- View appointments by week, month, or list
- Schedule new appointments for pending requests

## Troubleshooting

### Common Issues
- **Email sending failed**
   - Check SMTP settings
   - Ensure you are using an app password (Gmail)
   - Verify network allows SMTP traffic
- **AI features not working**
   - Check if OpenAI API key is set correctly
   - Ensure the API key has sufficient quota
- **Database errors**
   - Ensure write permissions to the database file
   - Check database path settings
- **File upload issues**
   - Ensure permission to create attachment directories

## Getting Help
If you encounter issues, check the log output or contact the system administrator.

## Technical Architecture

### Data Model
The system uses the following main tables:
- tenants - Tenant information
- maintenance_requests - Maintenance requests
- vendors - Vendor information
- solutions_database - Solution database
- interactions - User interaction records

### AI Integration
- Uses OpenAI GPT models for classification and response generation
- Uses ChromaDB for vector search and knowledge base management
- Fallback algorithms ensure system operation when API is unavailable

### Frontend Interface
- Built with Streamlit for responsive web UI
- Uses Plotly for data visualization
- Supports file upload and real-time status updates

## License
This project is for educational and personal use only. Commercial use requires permission.

## Contributing
Contributions and suggestions are welcome. Please follow the project's code style and standards.

## Changelog

v1.0
- Initial release
- All core features implemented
- Integrated AI classification and cost estimation
- Added email notification system
- Includes sample data and vendor information

For any questions or suggestions, please contact the system administrator or development team.
# AutoMaintain

AutoMaintain is an automated maintenance request management system built with Python and Streamlit. It supports multi-language UI, email notifications, and knowledge base integration for property management scenarios.

## Features
- Tenant request form and admin dashboard
- AI-powered issue classification and solution recommendation
- File upload and knowledge base management
- Calendar integration (placeholder)
- Email notifications via Gmail SMTP
- Multi-language support (English/Chinese)

## Quick Start

1. **Clone the repository**
   ```sh
   git clone <your-repo-url>
   cd AutoMaintain
   ```

2. **Create and activate a virtual environment**
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   - You can set them in `start.py` or use a `.env` file:
     ```env
     AUTOMAINTAIN_DB_PATH=./automaintain.db
     CHROMA_DB_DIR=./chroma_db
     OPENAI_API_KEY=your_openai_key
     SMTP_USER=your_gmail_address
     SMTP_PASS=your_app_password
     SMTP_SERVER=smtp.gmail.com
     SMTP_PORT=587
     ```

5. **Initialize and launch the app**
   ```sh
   python start.py
   ```
   Or directly run:
   ```sh
   streamlit run app/main.py
   ```

6. **Access the app**
   - Open [http://localhost:8501](http://localhost:8501) in your browser.

## File Structure
```
AutoMaintain/
 ├── start.py
 ├── requirements.txt
 ├── README.md
 └── app/
     ├── main.py
     ├── admin_dashboard.py
     ├── ai_agent.py
     ├── uploader.py
     ├── utils.py
     ├── db_init.py
     ├── calendar_integration.py
```

## Email Setup
- Use Gmail with an app password (not your regular password).
- Make sure your Google account allows SMTP access.

## License
MIT
