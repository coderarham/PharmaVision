from flask import Flask, render_template, jsonify, request
import pandas as pd
import json
import os
from medicine_analysis import MedicineAnalyzer

app = Flask(__name__)

# Global variable to store analyzer
analyzer = None

def load_data():
    global analyzer
    try:
        # Get the absolute path to the CSV file
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(BASE_DIR, 'A_Z_medicines_dataset_of_India.csv')
        
        if os.path.exists(csv_path):
            analyzer = MedicineAnalyzer(csv_path)
            return True
    except Exception as e:
        print(f"Error loading data: {e}")
    return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/manufacturers')
def get_manufacturers():
    if not analyzer:
        return jsonify({'error': 'Data not loaded'})
    
    top_manufacturers = analyzer.df['manufacturer_name'].value_counts().head(15)
    return jsonify({
        'labels': top_manufacturers.index.tolist(),
        'data': top_manufacturers.values.tolist()
    })

@app.route('/api/paracetamol')
def get_paracetamol():
    if not analyzer:
        return jsonify({'error': 'Data not loaded'})
    
    paracetamol_medicines = analyzer.df[(analyzer.df['short_composition1'].str.contains('Paracetamol', case=False, na=False)) | 
                                        (analyzer.df['short_composition2'].str.contains('Paracetamol', case=False, na=False))]
    paracetamol_sorted = paracetamol_medicines[['name', 'manufacturer_name', 'price(₹)']].sort_values('price(₹)').head(20)
    
    return jsonify({
        'medicines': paracetamol_sorted.to_dict('records')
    })

@app.route('/api/price-stats')
def get_price_stats():
    if not analyzer:
        return jsonify({'error': 'Data not loaded'})
    
    expensive = analyzer.df.nlargest(10, 'price(₹)')[['name', 'manufacturer_name', 'price(₹)']]
    cheapest = analyzer.df.nsmallest(10, 'price(₹)')[['name', 'manufacturer_name', 'price(₹)']]
    
    return jsonify({
        'expensive': expensive.to_dict('records'),
        'cheapest': cheapest.to_dict('records'),
        'price_distribution': analyzer.df['price(₹)'].dropna().tolist()
    })

@app.route('/api/diabetes')
def get_diabetes():
    if not analyzer:
        return jsonify({'error': 'Data not loaded'})
    
    diabetes_medicines = analyzer.df[(analyzer.df['short_composition1'].str.contains('Glimepiride|Metformin|Insulin|Sitagliptin', case=False, na=False)) |
                                     (analyzer.df['short_composition2'].str.contains('Glimepiride|Metformin|Insulin|Sitagliptin', case=False, na=False))]
    
    return jsonify({
        'medicines': diabetes_medicines[['name', 'manufacturer_name', 'short_composition1']].head(20).to_dict('records')
    })

@app.route('/api/compositions')
def get_compositions():
    if not analyzer:
        return jsonify({'error': 'Data not loaded'})
    
    all_compositions = []
    for comp in analyzer.df['short_composition1'].dropna():
        all_compositions.append(str(comp).strip())
    for comp in analyzer.df['short_composition2'].dropna():
        if str(comp) != 'nan':
            all_compositions.append(str(comp).strip())
    
    composition_counts = pd.Series(all_compositions).value_counts().head(15)
    
    return jsonify({
        'labels': composition_counts.index.tolist(),
        'data': composition_counts.values.tolist()
    })

@app.route('/api/summary')
def get_summary():
    if not analyzer:
        return jsonify({'error': 'Data not loaded'})
    
    return jsonify({
        'total_medicines': len(analyzer.df),
        'total_manufacturers': analyzer.df['manufacturer_name'].nunique(),
        'avg_price': round(analyzer.df['price(₹)'].mean(), 2),
        'min_price': analyzer.df['price(₹)'].min(),
        'max_price': analyzer.df['price(₹)'].max(),
        'unique_compositions': analyzer.df['short_composition1'].nunique()
    })

@app.route('/api/search')
def search_medicines():
    if not analyzer:
        return jsonify({'error': 'Data not loaded'})
    
    query = request.args.get('q', '').strip()
    if len(query) < 1:
        return jsonify({'medicines': []})
    
    # Search for medicines that start with the query (case-insensitive)
    mask = analyzer.df['name'].str.lower().str.startswith(query.lower(), na=False)
    results = analyzer.df[mask].head(50)
    
    medicines = []
    for _, row in results.iterrows():
        comp = f"{row['short_composition1']}"
        if pd.notna(row['short_composition2']) and str(row['short_composition2']) != 'nan':
            comp += f" + {row['short_composition2']}"
        
        medicines.append({
            'name': row['name'],
            'manufacturer': row['manufacturer_name'],
            'composition': comp,
            'price': row['price(₹)'],
            'pack_size': row['pack_size_label'],
            'type': row['type'],
            'discontinued': row['Is_discontinued']
        })
    
    return jsonify({'medicines': medicines})

@app.route('/api/suggestions')
def get_suggestions():
    if not analyzer:
        return jsonify({'suggestions': []})
    
    query = request.args.get('q', '').strip()
    if len(query) < 2:
        return jsonify({'suggestions': []})
    
    # Get medicine name suggestions
    medicine_suggestions = analyzer.df[analyzer.df['name'].str.contains(query, case=False, na=False)]['name'].unique()[:10]
    
    # Get manufacturer suggestions
    manufacturer_suggestions = analyzer.df[analyzer.df['manufacturer_name'].str.contains(query, case=False, na=False)]['manufacturer_name'].unique()[:5]
    
    # Get composition suggestions
    comp1_suggestions = analyzer.df[analyzer.df['short_composition1'].str.contains(query, case=False, na=False)]['short_composition1'].unique()[:5]
    
    suggestions = list(medicine_suggestions) + list(manufacturer_suggestions) + list(comp1_suggestions)
    
    return jsonify({'suggestions': suggestions[:15]})

@app.route('/api/companies')
def get_companies():
    if not analyzer:
        return jsonify({'error': 'Data not loaded'})
    
    companies = sorted(analyzer.df['manufacturer_name'].unique())
    return jsonify({'companies': companies})

@app.route('/api/filter-by-company')
def filter_by_company():
    if not analyzer:
        return jsonify({'error': 'Data not loaded'})
    
    company = request.args.get('company', '').strip()
    if not company:
        return jsonify({'medicines': []})
    
    # Filter medicines by company
    company_medicines = analyzer.df[analyzer.df['manufacturer_name'] == company]
    
    medicines = []
    for _, row in company_medicines.head(100).iterrows():  # Limit to 100 results
        comp = f"{row['short_composition1']}"
        if pd.notna(row['short_composition2']) and str(row['short_composition2']) != 'nan':
            comp += f" + {row['short_composition2']}"
        
        medicines.append({
            'name': row['name'],
            'manufacturer': row['manufacturer_name'],
            'composition': comp,
            'price': row['price(₹)'],
            'pack_size': row['pack_size_label'],
            'type': row['type'],
            'discontinued': row['Is_discontinued']
        })
    
    return jsonify({
        'medicines': medicines,
        'total_count': len(company_medicines),
        'company': company
    })

@app.route('/api/medicine-details')
def get_medicine_details():
    if not analyzer:
        return jsonify({'error': 'Data not loaded'})
    
    medicine_name = request.args.get('name', '').strip()
    if not medicine_name:
        return jsonify({'error': 'Medicine name required'})
    
    # Find the medicine
    medicine = analyzer.df[analyzer.df['name'] == medicine_name].iloc[0] if len(analyzer.df[analyzer.df['name'] == medicine_name]) > 0 else None
    
    if medicine is None:
        return jsonify({'error': 'Medicine not found'})
    
    # Get similar medicines from same manufacturer
    similar_medicines = analyzer.df[
        (analyzer.df['manufacturer_name'] == medicine['manufacturer_name']) & 
        (analyzer.df['name'] != medicine_name)
    ].head(5)
    
    # Get medicines with similar composition
    comp_similar = analyzer.df[
        (analyzer.df['short_composition1'] == medicine['short_composition1']) & 
        (analyzer.df['name'] != medicine_name)
    ].head(3)
    
    similar_list = []
    for _, row in similar_medicines.iterrows():
        similar_list.append({
            'name': row['name'],
            'price': row['price(₹)'],
            'pack_size': row['pack_size_label']
        })
    
    comp_similar_list = []
    for _, row in comp_similar.iterrows():
        comp_similar_list.append({
            'name': row['name'],
            'manufacturer': row['manufacturer_name'],
            'price': row['price(₹)']
        })
    
    return jsonify({
        'name': medicine['name'],
        'manufacturer': medicine['manufacturer_name'],
        'composition1': medicine['short_composition1'],
        'composition2': medicine['short_composition2'] if pd.notna(medicine['short_composition2']) and str(medicine['short_composition2']) != 'nan' else '',
        'price': medicine['price(₹)'],
        'pack_size': medicine['pack_size_label'],
        'type': medicine['type'],
        'discontinued': medicine['Is_discontinued'],
        'id': medicine['id'],
        'similar_medicines': similar_list,
        'composition_similar': comp_similar_list
    })

if __name__ == '__main__':
    # Load data on startup
    if load_data():
        print("Data loaded successfully!")
    else:
        print("Failed to load data!")
    
    # Run the app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)