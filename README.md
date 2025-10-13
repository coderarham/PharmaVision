# Indian Medicines Dataset Analysis Website

A comprehensive web-based analysis tool for the Indian medicines dataset that provides detailed insights into manufacturers, pricing, therapeutic uses, and chemical compositions.

## Features

### 📊 Analysis Sections
1. **Manufacturer Analysis**
   - Top 15 manufacturers by medicine count
   - Paracetamol price comparison
   - Cipla portfolio analysis

2. **Price Analysis**
   - Most expensive and cheapest medicines
   - High blood pressure medicines statistics
   - Price distribution visualization

3. **Therapeutic Use & Disease Analysis**
   - Diabetes medicines listing
   - Most versatile medicines

4. **Chemical Composition Analysis**
   - Most common chemical compositions
   - Diclofenac-containing medicines

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Add Dataset
Place your `A_Z_medicines_dataset_of_India.csv` file in the project directory.

### 3. Run Analysis (Console)
```bash
python medicine_analysis.py
```

### 4. Run Web Interface
```bash
python app.py
```

Then open your browser and go to: `http://localhost:5000`

## File Structure
```
medicine/
├── medicine_analysis.py    # Main analysis script
├── app.py                 # Flask web application
├── templates/
│   └── index.html        # Web interface template
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Dataset Requirements

The CSV file should contain these columns:
- Medicine Name
- Manufacturer
- Composition
- Uses
- Price

## Output

### Console Analysis
- Detailed text reports with tables
- Generated PNG charts (saved to disk)

### Web Interface
- Interactive dashboard
- Real-time charts and tables
- Responsive design

## Technologies Used
- **Backend**: Python, Flask, Pandas, Matplotlib, Seaborn
- **Frontend**: HTML, CSS, JavaScript, Chart.js
- **Data Processing**: NumPy, Collections

## Usage Tips
1. Ensure your CSV file has the correct column names
2. The web interface loads data dynamically via API endpoints
3. Charts are interactive and responsive
4. All price values are displayed in Indian Rupees (₹)

## Troubleshooting
- If you get "Data not loaded" error, check if the CSV file exists
- Make sure all dependencies are installed correctly
- Check console for any error messages