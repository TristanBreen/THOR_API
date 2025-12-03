"""
Quick start script for seizure prediction system
Runs the complete pipeline: train, analyze, predict, visualize
"""

import sys
import os
from datetime import datetime

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
    data_folder = '../Data'
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

def main():
    """Run complete pipeline"""
    print_header("SEIZURE PREDICTION SYSTEM - QUICK START")
    print(f"\nStarting pipeline at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check data files
    print_section("1/5: Checking Data Files")
    if not check_data_files():
        sys.exit(1)
    
    # Train models
    print_section("2/5: Training Machine Learning Models")
    try:
        from train_model import main as train_main
        predictor, metrics = train_main()
        print("[OK] Model training complete")
    except Exception as e:
        print(f"[ERROR] Error during training: {e}")
        sys.exit(1)
    
    # Analyze triggers
    print_section("3/5: Analyzing Seizure Triggers")
    try:
        from analyze_triggers import main as analyze_main
        analyzer = analyze_main()
        print("[OK] Trigger analysis complete")
    except Exception as e:
        print(f"[ERROR] Error during analysis: {e}")
        sys.exit(1)
    
    # Generate predictions
    print_section("4/5: Generating Current Predictions")
    try:
        from predict import main as predict_main
        forecaster = predict_main()
        print("[OK] Predictions generated")
    except Exception as e:
        print(f"[ERROR] Error during prediction: {e}")
        sys.exit(1)
    
    # Create visualizations UNCOMMENT TO HAVE VISUALS AGAIN
    #print_section("5/5: Creating Visualizations")
    #try:
    #    from visualize import main as visualize_main
    #    visualizer = visualize_main()
    #    print("✅ Visualizations created")
    #except Exception as e:
    #    print(f"❌ Error during visualization: {e}")
    #    print("Continuing without visualizations...")
    
    # Summary
    print_header("PIPELINE COMPLETE")
    print("\n[INFO] Generated Files:")
    print("   - models/classification_model_latest.pkl")
    print("   - models/regression_model_latest.pkl")
    print("   - models/scaler_latest.pkl")
    print("   - models/feature_importance.json")
    print("   - models/trigger_analysis.json")
    print("   - visualizations/*.png")
    
    print("\n[INFO] Next Steps:")
    print("   1. Review visualizations in the 'visualizations/' folder")
    print("   2. Check trigger analysis in 'models/trigger_analysis.json'")
    print("   3. Run 'python predict.py' anytime for current predictions")
    print("   4. Retrain models periodically as new data arrives")
    
    print("\n[TIPS] Tips:")
    print("   - High seizure probability (>60%) indicates elevated risk")
    print("   - Check feature importance to understand key factors")
    print("   - Regular retraining improves model accuracy")
    
    print(f"\n[OK] All done! Completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
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