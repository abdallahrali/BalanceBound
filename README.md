# BalanceBound ⚖️

BalanceBound is a Financial Intelligence Platform designed to provide a robust and intuitive double-entry accounting system. Built with Python and Streamlit, it allows users to manage their Chart of Accounts, record journal entries, and generate essential financial reports in real-time.

## Quick Start for Windows (No Coding Required)

If you have received the `BalanceBound.exe` file, follow these steps to run the application:

1.  **Double-click `BalanceBound.exe`**: You may see a window titled "Windows protected your PC".
2.  **Click "More info"**: Then click the **"Run anyway"** button.
3.  **Wait a moment**: A black window (terminal) will briefly appear while the system starts.
4.  **Automatic Launch**: Your web browser will automatically open and display the BalanceBound dashboard.

*Note: No installation of Python or any other software is required to use this version.*

## Project Structure

The project is organized into several key directories and files:

- **`app.py`**: The main entry point of the Streamlit application.
- **`config.py`**: Contains application-wide configuration, constants, and path settings.
- **`data/`**: Stores data files including:
  - `accounts.csv`: Chart of accounts definition.
  - `opening_balances.csv`: Initial balances for accounts.
  - `sample_entries.json`: Pre-populated journal entry data for demonstration.
- **`logic/`**: Core business and accounting logic:
  - `accounts.py`: Management of account hierarchies and types.
  - `journal.py`: Handling of journal entries and transaction logic.
  - `reports.py`: Generation of financial statements (Balance Sheet, Income Statement, Trial Balance).
- **`ui/`**: Modular Streamlit UI components:
  - `dashboard.py`: Overview of financial health and metrics.
  - `chart_of_accounts.py`: Visualization and management of accounts.
  - `journal_entries.py`: Interface for recording and viewing transactions.
  - `trial_balance.py`, `income_statement.py`, `balance_sheet.py`: Specific reporting pages.
  - `sidebar.py`: Main navigation and global filters.
  - `styles.py`: Custom CSS for the platform.

## Requirements

To run BalanceBound, you need:

- **Python 3.8 or higher**
- The dependencies listed in `requirements.txt`:
  - `streamlit`: Web framework for data apps.
  - `pandas`: Data manipulation and analysis.
  - `plotly`: Interactive visualizations.
  - `openpyxl`: Excel file support.
  - `streamlit-keyup`: Enhanced input handling.

## Installation

Follow these steps to set up the project locally:

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd BalanceBound
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
   ```

3. **Install the required packages:**
   ```bash
   pip install -r requirements.txt
   ```

## How to Run

Once the installation is complete, you can launch the application using the Streamlit CLI:

```bash
streamlit run app.py
```

After running this command, the application will be accessible in your web browser, typically at `http://localhost:8501`.
