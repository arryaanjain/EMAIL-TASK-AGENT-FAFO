<h1>Email Task Agent</h1>
    <p>A simple Agentic AI app that reads your emails, summarizes them using GPT, and extracts key tasks or follow-ups.</p>

    <h2>Setup</h2>
    <p>Follow the steps below to get started with the Email Task Agent:</p>

    <h3>1. Clone the repository</h3>
    <pre>
git clone https://github.com/yourusername/email-task-agent.git
cd email-task-agent
    </pre>

    <h3>2. Set up a Python environment</h3>
    <p>It's recommended to use a virtual environment to manage dependencies.</p>
    
    <ul>
        <li><strong>Create a virtual environment</strong>:
            <pre>python3 -m venv venv</pre>
        </li>
        <li><strong>Activate the virtual environment</strong>:
            <ul>
                <li>On macOS/Linux: 
                    <pre>source venv/bin/activate</pre>
                </li>
                <li>On Windows: 
                    <pre>venv\Scripts\activate</pre>
                </li>
            </ul>
        </li>
    </ul>

    <h3>3. Set up the .env file</h3>
    <p>In the root of your project, create a <code>.env</code> file and add your configuration:</p>
    <pre>
EMAIL_ADDRESS=your_email@example.com
EMAIL_PASSWORD=your_email_app_password
EMAIL_IMAP=imap.gmail.com
OPENAI_API_KEY=your_openai_api_key
    </pre>

    <p><strong>Important:</strong> For Gmail, use an <strong>App Password</strong> instead of your regular account password.  
    You can create an App Password here: <a href="https://myaccount.google.com/apppasswords" target="_blank">Google App Passwords</a>.</p>

    <h3>4. Install dependencies</h3>
    <p>Run the following command to install the required Python libraries:</p>
    <pre>
pip install -r requirements.txt
    </pre>

    <h3>5. Run the application</h3>
    <p>Finally, run the script:</p>
    <pre>
python main.py
    </pre>
    <p>This will start the email processing agent, which will read unread emails, summarize them, and extract tasks or follow-ups.</p>

    <h3>Troubleshooting</h3>
    <ul>
        <li><strong>App Password issue:</strong> Ensure you are using the correct <a href="https://myaccount.google.com/apppasswords" target="_blank">Google App Password</a> and not your regular Gmail password.</li>
        <li><strong>Quota issues:</strong> If you're using OpenAI, make sure your API key is valid and within usage limits.</li>
    </ul>

    <p>For more help or questions, feel free to open an issue in this repository.</p>
