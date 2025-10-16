import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

class MedicineAnalyzer:
    def __init__(self, csv_file):
        self.df = pd.read_csv(csv_file)
        self.setup_plots()
    
    def setup_plots(self):
        plt.style.use('default')
        sns.set_palette("husl")
        
    def manufacturer_analysis(self):
        print("=" * 60)
        print("1. MANUFACTURER ANALYSIS")
        print("=" * 60)
        
        # Top 15 manufacturers
        top_manufacturers = self.df['manufacturer_name'].value_counts().head(15)
        
        plt.figure(figsize=(12, 8))
        top_manufacturers.plot(kind='barh')
        plt.title('Top 15 Manufacturers by Number of Medicines')
        plt.xlabel('Number of Medicines')
        plt.tight_layout()
        plt.savefig('top_manufacturers.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("\nTop 15 Manufacturers:")
        for i, (manufacturer, count) in enumerate(top_manufacturers.items(), 1):
            print(f"{i:2d}. {manufacturer}: {count} medicines")
        
        # Paracetamol price comparison
        paracetamol_medicines = self.df[(self.df['short_composition1'].str.contains('Paracetamol', case=False, na=False)) | 
                                        (self.df['short_composition2'].str.contains('Paracetamol', case=False, na=False))]
        paracetamol_sorted = paracetamol_medicines[['name', 'manufacturer_name', 'price(₹)']].sort_values('price(₹)')
        
        print(f"\n\nParacetamol Medicines Price Comparison ({len(paracetamol_sorted)} medicines):")
        print("-" * 80)
        print(f"{'Medicine Name':<30} {'Manufacturer':<25} {'Price (Rs)':<10}")
        print("-" * 80)
        for _, row in paracetamol_sorted.head(20).iterrows():
            print(f"{str(row['name'])[:29]:<30} {str(row['manufacturer_name'])[:24]:<25} {row['price(₹)']:<10}")
        
        # Cipla portfolio analysis
        cipla_medicines = self.df[self.df['manufacturer_name'].str.contains('Cipla', case=False, na=False)]
        cipla_compositions = []
        for comp1 in cipla_medicines['short_composition1'].dropna():
            cipla_compositions.append(str(comp1).strip())
        for comp2 in cipla_medicines['short_composition2'].dropna():
            if str(comp2) != 'nan':
                cipla_compositions.append(str(comp2).strip())
        
        top_cipla_compositions = Counter(cipla_compositions).most_common(5)
        print(f"\n\nCipla Ltd - Top 5 Most Common Compositions:")
        print("-" * 50)
        for i, (comp, count) in enumerate(top_cipla_compositions, 1):
            print(f"{i}. {comp}: {count} medicines")
    
    def price_analysis(self):
        print("\n\n" + "=" * 60)
        print("2. PRICE ANALYSIS")
        print("=" * 60)
        
        # Most expensive and cheapest medicines
        expensive = self.df.nlargest(10, 'price(₹)')[['name', 'manufacturer_name', 'price(₹)']]
        cheapest = self.df.nsmallest(10, 'price(₹)')[['name', 'manufacturer_name', 'price(₹)']]
        
        print("\n10 Most Expensive Medicines:")
        print("-" * 70)
        print(f"{'Medicine Name':<30} {'Manufacturer':<25} {'Price (Rs)':<10}")
        print("-" * 70)
        for _, row in expensive.iterrows():
            print(f"{str(row['name'])[:29]:<30} {str(row['manufacturer_name'])[:24]:<25} {row['price(₹)']:<10}")
        
        print("\n\n10 Cheapest Medicines:")
        print("-" * 70)
        print(f"{'Medicine Name':<30} {'Manufacturer':<25} {'Price (Rs)':<10}")
        print("-" * 70)
        for _, row in cheapest.iterrows():
            print(f"{str(row['name'])[:29]:<30} {str(row['manufacturer_name'])[:24]:<25} {row['price(₹)']:<10}")
        
        # High blood pressure medicines (using composition as proxy since no Uses column)
        bp_medicines = self.df[(self.df['short_composition1'].str.contains('Amlodipine|Atenolol|Losartan|Telmisartan', case=False, na=False)) |
                              (self.df['short_composition2'].str.contains('Amlodipine|Atenolol|Losartan|Telmisartan', case=False, na=False))]
        if not bp_medicines.empty:
            bp_stats = {
                'Average': bp_medicines['price(₹)'].mean(),
                'Minimum': bp_medicines['price(₹)'].min(),
                'Maximum': bp_medicines['price(₹)'].max(),
                'Count': len(bp_medicines)
            }
            
            print(f"\n\nHigh Blood Pressure Medicines Price Statistics:")
            print("-" * 50)
            for stat, value in bp_stats.items():
                if stat == 'Count':
                    print(f"{stat}: {value}")
                else:
                    print(f"{stat}: Rs{value:.2f}")
        
        # Price distribution histogram
        plt.figure(figsize=(12, 6))
        plt.hist(self.df['price(₹)'].dropna(), bins=50, edgecolor='black', alpha=0.7)
        plt.title('Distribution of Medicine Prices')
        plt.xlabel('Price (Rs)')
        plt.ylabel('Frequency')
        plt.yscale('log')
        plt.tight_layout()
        plt.savefig('price_distribution.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def therapeutic_analysis(self):
        print("\n\n" + "=" * 60)
        print("3. THERAPEUTIC USE & DISEASE ANALYSIS")
        print("=" * 60)
        
        # Diabetes medicines (using composition as proxy)
        diabetes_medicines = self.df[(self.df['short_composition1'].str.contains('Glimepiride|Metformin|Insulin|Sitagliptin', case=False, na=False)) |
                                     (self.df['short_composition2'].str.contains('Glimepiride|Metformin|Insulin|Sitagliptin', case=False, na=False))]
        
        print(f"\nDiabetes Medicines ({len(diabetes_medicines)} found):")
        print("-" * 90)
        print(f"{'Medicine Name':<25} {'Manufacturer':<20} {'Composition':<40}")
        print("-" * 90)
        for _, row in diabetes_medicines.head(20).iterrows():
            comp = f"{str(row['short_composition1'])} + {str(row['short_composition2'])}" if pd.notna(row['short_composition2']) else str(row['short_composition1'])
            print(f"{str(row['name'])[:24]:<25} {str(row['manufacturer_name'])[:19]:<20} {comp[:39]:<40}")
        
        # Most versatile medicines (based on composition complexity)
        medicine_complexity = {}
        for _, row in self.df.iterrows():
            complexity = 1 if pd.notna(row['short_composition1']) else 0
            complexity += 1 if pd.notna(row['short_composition2']) and str(row['short_composition2']) != 'nan' else 0
            if complexity > 0:
                medicine_complexity[row['name']] = complexity
        
        top_versatile = sorted(medicine_complexity.items(), key=lambda x: x[1], reverse=True)[:10]
        
        print(f"\n\nTop 10 Most Complex Medicines (Multiple Compositions):")
        print("-" * 60)
        print(f"{'Medicine Name':<35} {'Composition Count':<15}")
        print("-" * 60)
        for medicine, comp_count in top_versatile:
            print(f"{str(medicine)[:34]:<35} {comp_count:<15}")
    
    def chemical_analysis(self):
        print("\n\n" + "=" * 60)
        print("4. CHEMICAL COMPOSITION (SALT) ANALYSIS")
        print("=" * 60)
        
        # Most common compositions
        all_compositions = []
        for comp in self.df['short_composition1'].dropna():
            all_compositions.append(str(comp).strip())
        for comp in self.df['short_composition2'].dropna():
            if str(comp) != 'nan':
                all_compositions.append(str(comp).strip())
        
        composition_counts = pd.Series(all_compositions).value_counts().head(15)
        
        plt.figure(figsize=(14, 8))
        composition_counts.plot(kind='bar')
        plt.title('Top 15 Most Common Chemical Compositions')
        plt.xlabel('Chemical Composition')
        plt.ylabel('Frequency')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig('common_compositions.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("\nTop 15 Most Common Chemical Compositions:")
        print("-" * 60)
        for i, (composition, count) in enumerate(composition_counts.items(), 1):
            print(f"{i:2d}. {str(composition)[:50]}: {count}")
        
        # Diclofenac medicines
        diclofenac_medicines = self.df[(self.df['short_composition1'].str.contains('Diclofenac', case=False, na=False)) |
                                       (self.df['short_composition2'].str.contains('Diclofenac', case=False, na=False))]
        
        print(f"\n\nMedicines containing Diclofenac ({len(diclofenac_medicines)} found):")
        print("-" * 80)
        print(f"{'Medicine Name':<40} {'Manufacturer':<25} {'Price (Rs)':<10}")
        print("-" * 80)
        for _, row in diclofenac_medicines.head(20).iterrows():
            print(f"{str(row['name'])[:39]:<40} {str(row['manufacturer_name'])[:24]:<25} {row['price(₹)']:<10}")
    
    def generate_summary(self):
        print("\n\n" + "=" * 60)
        print("DATASET SUMMARY")
        print("=" * 60)
        
        summary_stats = {
            'Total Medicines': len(self.df),
            'Total Manufacturers': self.df['manufacturer_name'].nunique(),
            'Average Price': f"Rs{self.df['price(₹)'].mean():.2f}",
            'Price Range': f"Rs{self.df['price(₹)'].min():.2f} - Rs{self.df['price(₹)'].max():.2f}",
            'Unique Compositions': self.df['short_composition1'].nunique()
        }
        
        for stat, value in summary_stats.items():
            print(f"{stat}: {value}")
    
    def run_full_analysis(self):
        print("COMPREHENSIVE MEDICINE DATASET ANALYSIS")
        print("=" * 60)
        
        self.manufacturer_analysis()
        self.price_analysis()
        self.therapeutic_analysis()
        self.chemical_analysis()
        self.generate_summary()
        
        print(f"\n\nAnalysis complete! Charts saved as PNG files.")

# Usage
if __name__ == "__main__":
    try:
        import os
        # Get the absolute path to the CSV file
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(BASE_DIR, 'A_Z_medicines_dataset_of_India.csv')
        
        analyzer = MedicineAnalyzer(csv_path)
        analyzer.run_full_analysis()
    except FileNotFoundError:
        print("Error: 'A_Z_medicines_dataset_of_India.csv' file not found!")
        print("Please ensure the CSV file is in the same directory as this script.")
    except Exception as e:
        print(f"Error: {e}")