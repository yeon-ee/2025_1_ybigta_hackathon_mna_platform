# M&A Platform for Innovative Companies

## Project Overview
This project is an intelligent M&A platform that leverages Upstage's advanced AI capabilities to analyze and evaluate innovative companies. The platform combines financial expertise with state-of-the-art language models to provide comprehensive company analysis and evaluation services.

## Quick Test Guide for Judges from upstage

### 1. Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set up API keys
echo "SOLAR_API_KEY=your_upstage_solar_api_key" > .env
```

### 2. Test the Core Features
The platform's core functionality can be tested through the Jupyter notebook in the agents folder:

```bash
# Navigate to the agents directory
cd agents

# Launch Jupyter notebook
jupyter notebook test.ipynb
```

The test notebook (`test.ipynb`) provides an interactive testing environment that demonstrates:

1. **Interactive Agent Communication**
   - Set up a test scenario with a custom `user_query`:
   ```python
   user_query = "헬스케어 산업에 종사하는, 연매출 100억 이상, 최근 1년 투자금 100억 이상, 작년 성장률 25% 이상, 영업이익률 10% 이상인 기업을 찾고 있습니다."
   ```
   - Observe the interaction between three key agents:
     - `ChecklistInspector`: Evaluates companies against criteria
     - `SellSideAgent`: Provides company information
     - `Questioner`: Manages the conversation flow

2. **Document Processing**
   - Test PDF document parsing with Upstage API
   - Analyze financial statements
   - Extract key metrics

3. **Company Evaluation**
   - Run the evaluation workflow
   - View scoring results
   - Analyze company recommendations

4. **Agent-Based Analysis**
   - Monitor the conversation between agents
   - Track information gathering process
   - View final evaluation results

The notebook provides a step-by-step guide to:
1. Initialize the agents
2. Set up the evaluation criteria
3. Run the analysis
4. View and interpret the results

### 3. Sample Data for testing
Test files are available in:
- `web/db/pages/utils/meatbox_finance.pdf`: Sample financial document(재무제표)
- `web/db/json/inno_company.json`: Sample company data

## Project Structure

### 1. Agents (`agents/`)
Core AI components that handle company analysis and evaluation:
- `test.ipynb`: Main test notebook for evaluating the platform
- `checklist_reviewer_new.py`: Analyzes the acquirer's input query and determines the relative importance of each evaluation criterion.
It assigns a score within a predefined range for each item, reflecting how strongly it was emphasized.
Unmentioned but domain-critical factors are still included with minimum scores.

- `sell_side_agent.py`: Acts as the virtual representative of the target company.
It retrieves structured data from the internal database and supplements missing context from public sources.
It answers investor questions about revenue, growth, funding history, profitability, and more.

- `checklist_inspector.py`: Aggregates all available data (DB, sell-side answers, external content) and scores the company
based on how well it matches each checklist item.
Requests clarification if information is missing or ambiguous to ensure accurate scoring.

- `web_surfer.py`: Web content analysis agent

### 2. Graph (`graph/`)
Workflow management system:
- `graph.py`: Main workflow implementation
- `state.py`: State management for the evaluation process
- `checklist.py`: Evaluation criteria and scoring system

### 3. Web (`web/`)
User interface and data processing:
- `utils/`: Document processing and analysis tools
- `db/`: Data storage and management
- `pages/`: Web interface components

## Upstage API Integration

### 1. Document Parsing (`web/utils/document_parse.py`)
**Purpose**: Extract structured information from financial documents

**Input**:
- PDF documents containing financial statements
- Document metadata (company name, year, etc.)

**Output**:
- Structured text data
- Table data from financial statements
- Document metadata

**API Usage**:
```python
from langchain_upstage import ChatUpstage

# Initialize the parser
parser = DocumentParser(api_key=SOLAR_API_KEY)

# Parse a document
result = parser.parse_document("path/to/document.pdf")
```

### 2. Information Extraction (`web/utils/financial_info_extractor.py`)
**Purpose**: Extract and analyze financial metrics from parsed documents

**Input**:
- Parsed document data
- Company information
- Analysis parameters

**Output**:
- Financial ratios
- Key performance indicators
- Risk metrics
- Growth indicators

**API Usage**:
```python
from langchain_upstage import ChatUpstage

# Initialize the extractor
extractor = FinancialInfoExtractor(api_key=SOLAR_API_KEY)

# Extract financial information
financial_data = extractor.extract_info(parsed_document)
```

### 3. Company Evaluation (`agents/checklist_reviewer_new.py`)
**Purpose**: Evaluate companies based on predefined criteria

**Input**:
- Company financial data
- Evaluation criteria
- Industry benchmarks

**Output**:
- Evaluation scores
- Risk assessment
- Growth potential analysis
- Investment recommendations

**API Usage**:
```python
from langchain_upstage import ChatUpstage

# Initialize the evaluator
evaluator = ChecklistReviewer(api_key=SOLAR_API_KEY)

# Evaluate a company
evaluation = evaluator.review_company(company_data)
```

## License
MIT License

## Contact
For support and inquiries, please contact the project maintainers.
