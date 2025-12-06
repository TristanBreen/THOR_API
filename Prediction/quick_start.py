"""
Updated Quick Start Script for Production Seizure Prediction System
Runs complete pipeline: Load → Engineer → Train → Analyze → Predict → Output

Compatible with the new modular production system.
"""

import sys
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Add parent directory to path for imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_section(text):
    """Print formatted section"""
    print("\n" + "-" * 70)
    print(f"  {text}")
    print("-" * 70)


def check_data_files():
    """Check if required data files exist"""
    # Determine data folder location
    PARENT_DIR = os.path.dirname(SCRIPT_DIR)
    SERVER_BASE_PATH = "/home/tristan/API/API_Repoed/THOR_API"
    
    if os.path.exists(os.path.join(SERVER_BASE_PATH, "Data")):
        data_folder = os.path.join(SERVER_BASE_PATH, "Data")
    elif os.path.exists('/data/Data'):
        data_folder = '/data/Data'
    elif os.path.exists(os.path.join(PARENT_DIR, "Data")):
        data_folder = os.path.join(PARENT_DIR, "Data")
    else:
        data_folder = os.path.join(PARENT_DIR, "Data")
    
    required_files = ['seizures.csv', 'appleWatchData.csv', 'pain.csv']
    
    missing_files = []
    for file in required_files:
        filepath = os.path.join(data_folder, file)
        if not os.path.exists(filepath):
            missing_files.append(file)
    
    if missing_files:
        print("[ERROR] Missing required data files:")
        for file in missing_files:
            print(f"   - {file}")
        print(f"\nPlease ensure these files exist in {data_folder}/")
        return False
    
    print("[OK] All required data files found")
    return True


def run_main_pipeline():
    """Run the main production pipeline"""
    print_section("1/4: Running Main Production Pipeline")
    
    try:
        # Check if we can import the main script
        import importlib.util
        main_script = os.path.join(SCRIPT_DIR, 'main.py')
        
        if not os.path.exists(main_script):
            print("[WARNING] main.py not found in Prediction folder.")
            print("[INFO] Looking for legacy train_model.py...")
            
            # Fall back to legacy system
            from train_model import main as train_main
            from predict import main as predict_main
            
            print("[INFO] Using legacy training system...")
            predictor, metrics = train_main()
            
            print("[INFO] Generating predictions...")
            forecaster = predict_main()
            
            return True
        
        # Load and execute the main script
        spec = importlib.util.spec_from_file_location("main_module", main_script)
        main_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(main_module)
        
        # Run the main function
        main_module.main()
        
        print("[OK] Main pipeline completed successfully")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error during main pipeline: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_trigger_analysis():
    """Run trigger analysis if available"""
    print_section("2/4: Analyzing Seizure Triggers")
    
    try:
        # Try to import analyze_triggers
        from analyze_triggers import TriggerAnalyzer
        
        # Import the data loader from the new system
        try:
            # Try new system first
            main_script = os.path.join(SCRIPT_DIR, 'main.py')
            if os.path.exists(main_script):
                import importlib.util
                spec = importlib.util.spec_from_file_location("main_module", main_script)
                main_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(main_module)
                
                loader = main_module.DataLoader()
                df, seizures = loader.load_and_harmonize(include_feedback=False)
                
                engineer = main_module.FeatureEngineer()
                df_features = engineer.create_features(df)
            else:
                # Fall back to legacy
                from data_preprocessing import DataLoader
                from feature_engineering import FeatureEngineer
                
                loader = DataLoader()
                df, seizures = loader.create_hourly_dataset()
                
                engineer = FeatureEngineer()
                df_features = engineer.create_features(df)
        except:
            # Ultimate fallback
            from data_preprocessing import DataLoader
            from feature_engineering import FeatureEngineer
            
            loader = DataLoader()
            df, seizures = loader.create_hourly_dataset()
            
            engineer = FeatureEngineer()
            df_features = engineer.create_features(df)
        
        # Run analysis
        analyzer = TriggerAnalyzer()
        results = analyzer.analyze_all_triggers(df_features, seizures)
        analyzer.save_results()
        
        print("[OK] Trigger analysis complete")
        return True
        
    except ImportError:
        print("[WARNING] Trigger analysis module not available")
        print("[INFO] Skipping trigger analysis...")
        return False
    except Exception as e:
        print(f"[ERROR] Error during trigger analysis: {e}")
        print("[INFO] Continuing without trigger analysis...")
        return False


def check_outputs():
    """Verify output files were created"""
    print_section("3/4: Verifying Output Files")
    
    # Determine data folder
    PARENT_DIR = os.path.dirname(SCRIPT_DIR)
    SERVER_BASE_PATH = "/home/tristan/API/API_Repoed/THOR_API"
    
    if os.path.exists(os.path.join(SERVER_BASE_PATH, "Data")):
        data_folder = os.path.join(SERVER_BASE_PATH, "Data")
    elif os.path.exists('/data/Data'):
        data_folder = '/data/Data'
    elif os.path.exists(os.path.join(PARENT_DIR, "Data")):
        data_folder = os.path.join(PARENT_DIR, "Data")
    else:
        data_folder = os.path.join(PARENT_DIR, "Data")
    
    model_folder = os.path.join(SCRIPT_DIR, "models")
    
    # Check required output files
    outputs = {
        'prediction.txt': os.path.join(data_folder, 'prediction.txt'),
        'longTermPredictions.json': os.path.join(data_folder, 'longTermPredictions.json'),
        'model_24h.pkl': os.path.join(model_folder, 'model_24h.pkl'),
        'model_48h.pkl': os.path.join(model_folder, 'model_48h.pkl'),
        'model_72h.pkl': os.path.join(model_folder, 'model_72h.pkl'),
    }
    
    all_exist = True
    for name, path in outputs.items():
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"   ✓ {name:30s} ({size:,} bytes)")
        else:
            print(f"   ✗ {name:30s} [MISSING]")
            all_exist = False
    
    if all_exist:
        print("\n[OK] All output files created successfully")
    else:
        print("\n[WARNING] Some output files are missing")
    
    return all_exist


def display_summary():
    """Display final summary and next steps"""
    print_section("4/4: Summary & Next Steps")
    
    # Determine data folder
    PARENT_DIR = os.path.dirname(SCRIPT_DIR)
    SERVER_BASE_PATH = "/home/tristan/API/API_Repoed/THOR_API"
    
    if os.path.exists(os.path.join(SERVER_BASE_PATH, "Data")):
        data_folder = os.path.join(SERVER_BASE_PATH, "Data")
    elif os.path.exists('/data/Data'):
        data_folder = '/data/Data'
    elif os.path.exists(os.path.join(PARENT_DIR, "Data")):
        data_folder = os.path.join(PARENT_DIR, "Data")
    else:
        data_folder = os.path.join(PARENT_DIR, "Data")
    
    # Try to read and display current predictions
    try:
        prediction_txt = os.path.join(data_folder, 'prediction.txt')
        if os.path.exists(prediction_txt):
            print("\n📊 CURRENT PREDICTIONS:")
            print("-" * 70)
            with open(prediction_txt, 'r') as f:
                print(f.read())
    except Exception as e:
        print(f"[WARNING] Could not read predictions: {e}")
    
    print("\n📁 GENERATED FILES:")
    print("   • prediction.txt - Current seizure risk percentages")
    print("   • longTermPredictions.json - Historical prediction log")
    print("   • models/model_24h.pkl - Trained 24-hour model")
    print("   • models/model_48h.pkl - Trained 48-hour model")
    print("   • models/model_72h.pkl - Trained 72-hour model")
    print("   • models/scaler.pkl - Feature scaler")
    print("   • models/feature_columns.pkl - Feature metadata")
    
    if os.path.exists(os.path.join(SCRIPT_DIR, "models", "trigger_analysis.json")):
        print("   • models/trigger_analysis.json - Trigger patterns")
    
    print("\n🔄 NEXT STEPS:")
    print("   1. Review predictions in prediction.txt")
    print("   2. Check longTermPredictions.json for historical trends")
    print("   3. Run 'python main.py' anytime for updated predictions")
    print("   4. Retrain models weekly with 'python main.py' (auto-detects)")
    
    print("\n💡 TIPS:")
    print("   • High risk (>60%): Elevated seizure probability")
    print("   • Models improve with more data (3+ months ideal)")
    print("   • Check trigger analysis for pattern insights")
    print("   • System automatically uses existing models if found")
    
    print("\n⚡ AUTOMATION:")
    print("   • Set up cron job to run every 3 hours:")
    print("     0 */3 * * * cd /path/to/Prediction && python main.py")
    print("   • Or use Docker scheduler for continuous operation")


def main():
    """Run complete quick start pipeline"""
    print_header("SEIZURE PREDICTION SYSTEM - QUICK START")
    print(f"\nStarting pipeline at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Check data files
    print_section("Step 0: Checking Data Files")
    if not check_data_files():
        sys.exit(1)
    
    # Step 2: Run main pipeline (load, engineer, train, predict)
    success = run_main_pipeline()
    if not success:
        print("\n[ERROR] Main pipeline failed. Exiting...")
        sys.exit(1)
    
    # Step 3: Run trigger analysis (optional)
    run_trigger_analysis()
    
    # Step 4: Verify outputs
    check_outputs()
    
    # Step 5: Display summary
    display_summary()
    
    # Final completion message
    print_header("PIPELINE COMPLETE")
    print(f"\n✅ All done! Completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[WARNING] Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)